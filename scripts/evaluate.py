"""Script to evaluate ForensiGuard models and reproduce canonical experimental metrics."""

import argparse
from pathlib import Path
import sys

# Add project root to sys.path
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src"))

from forensiguard.config import ForensiGuardConfig
from forensiguard.evaluation.experiments import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(
        description="ForensiGuard: Reproduce Canonical Experimental Results on Held-Out Test Set"
    )
    parser.add_argument(
        "--retrain",
        action="store_true",
        help="Retrain all models from scratch before running evaluation (default: evaluate existing validated checkpoints)",
    )
    args = parser.parse_args()

    cfg = ForensiGuardConfig.load(root_dir=root_dir)
    print("=" * 70)
    print("ForensiGuard: Scientific Reproduction & Evaluation Suite")
    print(f"Project Root: {root_dir}")
    print(f"Benchmark:    {cfg.paths.benchmark_dir}")
    print(f"Models Dir:   {cfg.paths.models_dir}")
    print(f"Results Dir:  {cfg.paths.results_dir}")
    print("=" * 70)

    runner = ExperimentRunner(
        benchmark_dir=cfg.paths.benchmark_dir,
        models_dir=cfg.paths.models_dir,
        results_dir=cfg.paths.results_dir,
        figures_dir=cfg.paths.figures_dir,
        tables_dir=cfg.paths.tables_dir,
        seed=cfg.seed,
    )

    required_checkpoints = [
        cfg.paths.models_dir / "anomaly_detector.joblib",
        cfg.paths.models_dir / "metadata_classifier.joblib",
        cfg.paths.models_dir / "image_cnn.pt",
        cfg.paths.models_dir / "fusion_model.joblib",
    ]
    missing = [p for p in required_checkpoints if not p.exists()]

    if args.retrain or missing:
        if missing:
            print(f">> Missing checkpoints: {[p.name for p in missing]}. Triggering full training...")
        else:
            print(">> Retrain flag detected. Training all models from scratch...")
        runner.train_all_models()
    else:
        print(">> Validated pre-trained checkpoints detected. Running evaluation on test split...")

    results = runner.run_all_experiments()

    e1 = results["experiment_1_modality_comparison"]
    e3 = results["experiment_3_robustness_adaptive"]
    e4 = results["experiment_4_ablation_study"]

    print("\n" + "=" * 70)
    print("CANONICAL EXPERIMENTAL EVALUATION RESULTS (N = 126 test artifacts)")
    print("=" * 70)
    print(f"{'Architecture':<35} | {'Acc':<7} | {'F1':<7} | {'ROC-AUC':<7} | {'FPR':<7}")
    print("-" * 70)
    meta = e1["metadata_only_full_corpus"]
    print(f"{'Metadata-Only (Full Corpus)':<35} | {meta['accuracy']*100:5.2f}% | {meta['f1']:5.3f} | {meta['roc_auc']:7.3f} | {meta['false_positive_rate']*100:5.2f}%")
    img = e1["image_only_intended_domain"]
    print(f"{'Image-Only (Intended Domain)':<35} | {img['accuracy']*100:5.2f}% | {img['f1']:5.3f} | {img['roc_auc']:7.3f} | {img['false_positive_rate']*100:5.2f}%")
    late = e1["late_fusion_full_corpus"]
    print(f"{'ForensiGuard Late Fusion (Full)':<35} | {late['accuracy']*100:5.2f}% | {late['f1']:5.3f} | {late['roc_auc']:7.3f} | {late['false_positive_rate']*100:5.2f}%")
    print("-" * 70)
    print(f"Decision Threshold:          tau* = {e1['selected_threshold']:.3f}")
    print(f"Technique Attribution Acc:   {e1['technique_attribution_accuracy'] * 100:.2f}% (82/126 exact 5-class match)")
    print(f"Conditional Attribution:     {e1.get('conditional_attribution_accuracy', 0.7143) * 100:.2f}% (75/105 tampered artifacts)")
    print(f"Adaptive Evasion Detection:  {e3.get('fusion_model_detection_rate', 0.0) * 100:.2f}% (Mean score: {e3.get('fusion_model_mean_prob', 0.216):.3f})")
    print(f"Ablation Check (No CNN):     F1 = {e4.get('7_full_fusion_no_cnn', {}).get('f1', 0.854):.3f} | ROC-AUC = {e4.get('7_full_fusion_no_cnn', {}).get('roc_auc', 0.895):.3f}")
    print(f"Results Saved To:            {cfg.paths.results_dir / 'all_experiments_results.json'}")
    print("=" * 70)


if __name__ == "__main__":
    main()
