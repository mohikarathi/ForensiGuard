"""Script to generate the ForensiGuard reproducible benchmark dataset."""

from pathlib import Path
import sys

# Add project root to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src"))

from forensiguard.config import ForensiGuardConfig
from forensiguard.data.generation import BenchmarkGenerator


def main():
    cfg = ForensiGuardConfig.load(root_dir=root_dir)
    print(f"Generating benchmark in {cfg.paths.benchmark_dir} with {cfg.benchmark.num_sources} sources...")
    generator = BenchmarkGenerator(output_dir=cfg.paths.benchmark_dir, seed=cfg.seed)
    df = generator.generate_benchmark(num_sources=cfg.benchmark.num_sources)
    print(f"Successfully generated {len(df)} artifacts.")
    print("Class distribution:")
    print(df["technique"].value_counts())
    print("Split distribution:")
    print(df["split"].value_counts())


if __name__ == "__main__":
    main()
