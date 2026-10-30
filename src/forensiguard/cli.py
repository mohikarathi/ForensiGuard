"""Command-line interface for ForensiGuard."""

import argparse
from pathlib import Path
import subprocess
import sys

from forensiguard.config import ForensiGuardConfig
from forensiguard.data.generation import BenchmarkGenerator
from forensiguard.evaluation.experiments import ExperimentRunner
from forensiguard.pipeline import ForensiGuardPipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ForensiGuard: Multimodal ML Framework for Detecting, Attributing, and Explaining Digital Evidence Manipulation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Generate Benchmark
    gen_parser = subparsers.add_parser("generate-benchmark", help="Generate reproducible forensic benchmark dataset")
    gen_parser.add_argument("--sources", type=int, default=120, help="Number of clean source files to generate from")
    gen_parser.add_argument("--output", type=str, default="data/benchmark", help="Output directory for benchmark")

    # 2. Train Models & Run Experiments
    train_parser = subparsers.add_parser("train-and-evaluate", help="Train all models and run complete experimental suite")
    train_parser.add_argument("--config", type=str, default="configs/default.yaml", help="Configuration file path")

    # 3. Analyze Single Evidence File
    analyze_parser = subparsers.add_parser("analyze", help="Perform forensic analysis on an artifact file")
    analyze_parser.add_argument("file_path", type=str, help="Path to evidence artifact")
    analyze_parser.add_argument("--models-dir", type=str, default="artifacts/models", help="Directory of trained models")
    analyze_parser.add_argument("--out-dir", type=str, default="reports", help="Directory to save report")
    analyze_parser.add_argument("--format", choices=["markdown", "json", "html", "pdf", "all"], default="all")

    # 4. Launch Demonstration UI
    demo_parser = subparsers.add_parser("demo", help="Launch Streamlit forensic triage interface")
    demo_parser.add_argument("--port", type=int, default=8501, help="Port for Streamlit server")

    args = parser.parse_args()
    root_dir = Path(__file__).resolve().parents[2]

    if args.command == "generate-benchmark":
        out_dir = root_dir / args.output
        print(f"Generating benchmark dataset with {args.sources} sources in {out_dir}...")
        gen = BenchmarkGenerator(output_dir=out_dir)
        df = gen.generate_benchmark(num_sources=args.sources)
        print(f"Successfully generated {len(df)} forensic artifacts across {args.sources} sources.")
        print(f"Manifest written to: {out_dir / 'benchmark_manifest.csv'}")

    elif args.command == "train-and-evaluate":
        cfg = ForensiGuardConfig.load(config_path=root_dir / args.config, root_dir=root_dir)
        runner = ExperimentRunner(
            benchmark_dir=cfg.paths.benchmark_dir,
            models_dir=cfg.paths.models_dir,
            results_dir=cfg.paths.results_dir,
            figures_dir=cfg.paths.figures_dir,
            tables_dir=cfg.paths.tables_dir,
            seed=cfg.seed,
        )
        print("Training models...")
        runner.train_all_models()
        print("Running experiments...")
        runner.run_all_experiments()
        print("Training and evaluation completed successfully.")

    elif args.command == "analyze":
        target = Path(args.file_path).resolve()
        models = root_dir / args.models_dir
        out_dir = root_dir / args.out_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        pipeline = ForensiGuardPipeline(models_dir=models)
        report = pipeline.analyze_artifact(target)

        base_name = f"forensic_report_{target.stem}"
        if args.format in ["markdown", "all"]:
            md_path = out_dir / f"{base_name}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(report.to_markdown())
            print(f"Report (Markdown): {md_path}")

        if args.format in ["html", "all"]:
            html_path = out_dir / f"{base_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(report.to_html())
            print(f"Report (HTML): {html_path}")

        if args.format in ["json", "all"]:
            json_path = out_dir / f"{base_name}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(report.to_json())
            print(f"Report (JSON): {json_path}")

        if args.format in ["pdf", "all"]:
            pdf_path = out_dir / f"{base_name}.pdf"
            report.to_pdf(pdf_path)
            print(f"Report (PDF): {pdf_path}")

        print("\n" + "=" * 60)
        print(f"VERDICT: {'TAMPERED' if report.data['probabilistic_inferences']['is_manipulated'] else 'CLEAN'}")
        print(f"Technique: {report.data['probabilistic_inferences']['attributed_technique'].upper()}")
        print(f"Probability: {report.data['probabilistic_inferences']['manipulation_probability'] * 100:.2f}%")
        print(f"Confidence: {report.data['probabilistic_inferences']['confidence'] * 100:.2f}%")
        print("=" * 60)

    elif args.command == "demo":
        app_path = root_dir / "app" / "streamlit_app.py"
        print(f"Launching Streamlit application from {app_path} on port {args.port}...")
        subprocess.run(["streamlit", "run", str(app_path), "--server.port", str(args.port)])


if __name__ == "__main__":
    main()
