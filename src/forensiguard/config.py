"""Configuration manager for ForensiGuard."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class PathConfig:
    root_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    data_dir: Path = field(default_factory=lambda: Path("data"))
    raw_dir: Path = field(default_factory=lambda: Path("data/raw"))
    processed_dir: Path = field(default_factory=lambda: Path("data/processed"))
    benchmark_dir: Path = field(default_factory=lambda: Path("data/benchmark"))
    models_dir: Path = field(default_factory=lambda: Path("artifacts/models"))
    results_dir: Path = field(default_factory=lambda: Path("results"))
    reports_dir: Path = field(default_factory=lambda: Path("reports"))
    figures_dir: Path = field(default_factory=lambda: Path("paper/figures"))
    tables_dir: Path = field(default_factory=lambda: Path("paper/tables"))

    def resolve_paths(self, base: Path) -> None:
        """Resolve all relative paths against base directory."""
        self.root_dir = base.resolve()
        for attr in [
            "data_dir", "raw_dir", "processed_dir", "benchmark_dir",
            "models_dir", "results_dir", "reports_dir", "figures_dir", "tables_dir"
        ]:
            val = getattr(self, attr)
            if not isinstance(val, Path):
                val = Path(val)
            if not val.is_absolute():
                setattr(self, attr, (self.root_dir / val).resolve())


@dataclass
class BenchmarkConfig:
    num_sources: int = 140
    split_ratios: Dict[str, float] = field(default_factory=lambda: {"train": 0.70, "val": 0.15, "test": 0.15})
    split_group_key: str = "source_file_id"
    include_clean: bool = True
    include_timestomp_coarse: bool = True
    include_timestomp_subtle: bool = True
    include_stego_lsb: bool = True
    include_stego_steghide: bool = True
    include_obfuscation: bool = True
    include_compound: bool = True


@dataclass
class MetadataModelConfig:
    anomaly_model: str = "isolation_forest"
    anomaly_contamination: float = 0.05
    anomaly_n_estimators: int = 150
    xgb_n_estimators: int = 120
    xgb_max_depth: int = 4
    xgb_learning_rate: float = 0.05
    xgb_subsample: float = 0.85
    xgb_colsample: float = 0.85
    features: List[str] = field(default_factory=lambda: [
        "delta_mtime_ctime",
        "delta_atime_mtime",
        "delta_atime_ctime",
        "is_chronology_inverted",
        "mtime_zero_subseconds",
        "ctime_zero_subseconds",
        "atime_zero_subseconds",
        "mtime_round_minute",
        "mtime_round_hour",
        "folder_mtime_deviation_zscore",
        "folder_mtime_diff_median",
        "file_size_bytes",
    ])


@dataclass
class ImageModelConfig:
    architecture: str = "SRNetLite"
    input_size: int = 128
    batch_size: int = 16
    epochs: int = 15
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    filter_type: str = "laplacian_and_kv"


@dataclass
class FusionModelConfig:
    meta_classifier: str = "logistic_regression"
    cv_folds: int = 5
    c_param: float = 1.0
    random_state: int = 42


@dataclass
class ForensiGuardConfig:
    seed: int = 42
    paths: PathConfig = field(default_factory=PathConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    metadata_model: MetadataModelConfig = field(default_factory=MetadataModelConfig)
    image_model: ImageModelConfig = field(default_factory=ImageModelConfig)
    fusion_model: FusionModelConfig = field(default_factory=FusionModelConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None, root_dir: Optional[Path] = None) -> "ForensiGuardConfig":
        """Load configuration from YAML file or return defaults."""
        config = cls()
        if root_dir is not None:
            config.paths.resolve_paths(root_dir)
        elif config.paths.root_dir:
            config.paths.resolve_paths(config.paths.root_dir)

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            if "seed" in data:
                config.seed = int(data["seed"])
            if "benchmark" in data:
                b = data["benchmark"]
                config.benchmark.num_sources = b.get("num_sources", config.benchmark.num_sources)
                config.benchmark.split_ratios = b.get("split_ratios", config.benchmark.split_ratios)
            if "metadata_model" in data:
                m = data["metadata_model"]
                if "anomaly" in m:
                    config.metadata_model.anomaly_contamination = m["anomaly"].get("contamination", 0.05)
                    config.metadata_model.anomaly_n_estimators = m["anomaly"].get("n_estimators", 150)
                if "classifier" in m:
                    config.metadata_model.xgb_n_estimators = m["classifier"].get("n_estimators", 120)
                    config.metadata_model.xgb_max_depth = m["classifier"].get("max_depth", 4)
                    config.metadata_model.xgb_learning_rate = m["classifier"].get("learning_rate", 0.05)
            if "image_model" in data:
                im = data["image_model"]
                config.image_model.input_size = im.get("input_size", 128)
                config.image_model.epochs = im.get("epochs", 15)
                config.image_model.batch_size = im.get("batch_size", 16)
        return config
