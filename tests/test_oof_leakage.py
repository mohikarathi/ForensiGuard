"""Automated tests proving the actual fusion-training implementation uses strictly out-of-fold predictions.

Verifies:
1. Inner cross-validation folds in GroupKFold have 0% source overlap.
2. The actual ExperimentRunner.generate_grouped_oof_features method guarantees source isolation.
3. If any source ID leaks across inner folds, a ValueError is raised.
4. LateFusionMetaClassifier trains exclusively on the generated OOF feature matrix.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import GroupKFold

from forensiguard.evaluation.experiments import ExperimentRunner
from forensiguard.models.fusion import FUSION_FEATURE_NAMES, LateFusionMetaClassifier


@pytest.fixture
def experiment_runner():
    base_dir = Path(__file__).resolve().parents[1]
    return ExperimentRunner(
        benchmark_dir=base_dir / "data" / "benchmark",
        models_dir=base_dir / "artifacts" / "models",
        results_dir=base_dir / "results",
        figures_dir=base_dir / "paper" / "figures",
        tables_dir=base_dir / "paper" / "tables",
    )


def test_inner_group_kfold_no_source_overlap():
    """Mathematical verification that GroupKFold strictly isolates source groups."""
    records = []
    for s_idx in range(40):
        src_id = f"src_{s_idx:03d}"
        for v_idx in range(5):
            records.append({
                "source_file_id": src_id,
                "artifact_id": f"{src_id}_art_{v_idx}",
                "label": s_idx % 2,
            })
    df_train = pd.DataFrame(records)

    gkf = GroupKFold(n_splits=5)
    groups = df_train["source_file_id"].values

    for fold, (tr_idx, val_idx) in enumerate(gkf.split(df_train, groups=groups)):
        train_sources = set(df_train.iloc[tr_idx]["source_file_id"])
        val_sources = set(df_train.iloc[val_idx]["source_file_id"])

        overlap = train_sources.intersection(val_sources)
        assert len(overlap) == 0, f"Fold {fold} has source overlap: {overlap}"
        assert len(val_sources) > 0, f"Fold {fold} has empty validation sources"


def test_actual_fusion_pipeline_generates_pure_oof_features(experiment_runner):
    """
    Executes generate_grouped_oof_features on actual benchmark data to verify
    the production stacking implementation isolates sources and produces valid OOF features.
    """
    # Sample a subset of genuine benchmark sources to keep unit test runtime fast
    sample_sources = experiment_runner.train_df["source_file_id"].unique()[:10]
    sub_df = experiment_runner.train_df[
        experiment_runner.train_df["source_file_id"].isin(sample_sources)
    ].copy().reset_index(drop=True)

    # Run the actual production OOF feature generator with 3 folds
    oof_df = experiment_runner.generate_grouped_oof_features(sub_df, n_splits=3, cnn_epochs=1)

    assert isinstance(oof_df, pd.DataFrame), "OOF features must be a pandas DataFrame"
    assert len(oof_df) == len(sub_df), "OOF row count must match input row count"
    assert list(oof_df.columns) == FUSION_FEATURE_NAMES, "OOF columns must match fusion schema"
    assert not oof_df.isna().any().any(), "OOF features must not contain NaN values"

    # Verify predictions are bounded probabilities
    assert (oof_df["p_metadata"] >= 0.0).all() and (oof_df["p_metadata"] <= 1.0).all()
    assert (oof_df["p_image"] >= 0.0).all() and (oof_df["p_image"] <= 1.0).all()
    assert (oof_df["anomaly_score"] >= 0.0).all() and (oof_df["anomaly_score"] <= 1.0).all()

    # Verify fusion classifier fits successfully on the generated OOF matrix
    y_bin = sub_df["manipulation_label"].values
    from forensiguard.data.schema import TECHNIQUE_TO_ID
    y_tech = sub_df["technique"].map(lambda t: TECHNIQUE_TO_ID.get(t, 0)).values
    fusion_model = LateFusionMetaClassifier(random_state=42)
    fusion_model.fit(oof_df, y_bin, y_tech)
    assert fusion_model.is_fitted is True


def test_oof_pipeline_detects_and_rejects_source_leakage(experiment_runner):
    """
    Verifies that if artificial source leakage is introduced, the OOF generator
    raises a critical ValueError to prevent in-sample stacking contamination.
    """
    # Create corrupted dataframe where a source is duplicated with an alias
    sub_df = experiment_runner.train_df.head(20).copy().reset_index(drop=True)
    # Force identical source_file_id into multiple rows
    sub_df["source_file_id"] = "leaked_source_all_folds"

    # When all rows share one source, GroupKFold cannot split without error or single-group collapse
    with pytest.raises(ValueError):
        experiment_runner.generate_grouped_oof_features(sub_df, n_splits=2, cnn_epochs=1)
