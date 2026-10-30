"""PyTorch Convolutional Neural Network for noise-residual image steganalysis (SRNet-Lite)."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

from forensiguard.preprocessing.images import compute_noise_residual, load_and_preprocess_image


class ResidualBlock(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = self.relu(out + residual)
        return out


class SRNetLite(nn.Module):
    """
    Lightweight Deep Residual Steganalysis Architecture.
    Operates on spatial noise residuals to detect high-frequency modifications.
    """

    def __init__(self, in_channels: int = 1, num_classes: int = 2) -> None:
        super().__init__()
        # Initial projection
        self.stem = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
        )

        # Stage 1: Residual block + Pooling
        self.stage1 = nn.Sequential(
            ResidualBlock(16),
            nn.MaxPool2d(2, 2),  # 128 -> 64
        )

        # Stage 2: Feature expansion + Residual + Pooling
        self.stage2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            ResidualBlock(32),
            nn.MaxPool2d(2, 2),  # 64 -> 32
        )

        # Stage 3: Feature expansion + Pooling
        self.stage3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 32 -> 16
        )

        # Global average pooling and classification
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(32, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.stem(x)
        out = self.stage1(out)
        out = self.stage2(out)
        out = self.stage3(out)
        out = self.gap(out)
        out = torch.flatten(out, 1)
        logits = self.classifier(out)
        return logits


class StegoDataset(Dataset):
    """Dataset for loading pre-processed image paths and generating on-the-fly residuals."""

    def __init__(self, file_paths: List[Union[str, Path]], labels: List[int], target_size: Tuple[int, int] = (128, 128)) -> None:
        self.file_paths = [Path(p) for p in file_paths]
        self.labels = labels
        self.target_size = target_size

    def __len__(self) -> int:
        return len(self.file_paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        path = self.file_paths[idx]
        label = self.labels[idx]

        arr = load_and_preprocess_image(path, target_size=self.target_size)
        if arr is None:
            # Fallback for corrupted or missing file: zero residual
            arr = np.zeros(self.target_size, dtype=np.float32)

        res = compute_noise_residual(arr, filter_type="kv")
        tensor = torch.from_numpy(res).unsqueeze(0)  # [1, H, W]
        return tensor, label


class ImageCNNManager:
    """Manager class wrapping training, evaluation, saving, and inference for SRNetLite."""

    def __init__(self, device: Optional[str] = None) -> None:
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        self.model = SRNetLite().to(self.device)
        self.is_trained = False

    def train_model(
        self,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        epochs: int = 12,
        lr: float = 0.001,
        weight_decay: float = 1e-4,
    ) -> Dict[str, List[float]]:
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        history = {"train_loss": [], "val_loss": [], "val_acc": []}

        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            total_samples = 0

            for inputs, targets in train_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                total_samples += inputs.size(0)

            scheduler.step()
            train_loss = running_loss / max(total_samples, 1)
            history["train_loss"].append(train_loss)

            if val_loader:
                val_loss, val_acc = self.evaluate(val_loader)
                history["val_loss"].append(val_loss)
                history["val_acc"].append(val_acc)

        self.is_trained = True
        return history

    def evaluate(self, data_loader: DataLoader) -> Tuple[float, float]:
        self.model.eval()
        criterion = nn.CrossEntropyLoss()
        running_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for inputs, targets in data_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                outputs = self.model(inputs)
                loss = criterion(outputs, targets)
                running_loss += loss.item() * inputs.size(0)
                preds = outputs.argmax(dim=1)
                correct += (preds == targets).sum().item()
                total += targets.size(0)

        loss = running_loss / max(total, 1)
        acc = correct / max(total, 1)
        return loss, acc

    def predict_proba(self, image_path: Union[str, Path]) -> float:
        """
        Inference on a single image.
        Returns float P(steganography) in [0, 1].
        """
        arr = load_and_preprocess_image(image_path, target_size=(128, 128))
        if arr is None:
            return 0.5  # Neutral fallback for non-image or unreadable files

        res = compute_noise_residual(arr, filter_type="kv")
        tensor = torch.from_numpy(res).unsqueeze(0).unsqueeze(0).to(self.device)  # [1, 1, 128, 128]

        self.model.eval()
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1)
            p_stego = float(probs[0, 1].item())
        return p_stego

    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "is_trained": self.is_trained,
        }, path)

    def load(self, path: Union[str, Path]) -> None:
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.is_trained = checkpoint.get("is_trained", True)
        self.model.eval()
