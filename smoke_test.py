"""
benchmark_harness/smoke_test.py
Owner: Hyunmin
Date: Tue, Aug 25

End-to-end sanity check for the harness scaffolding: builds a config,
logs a few fake p-value results, finalizes, then reads everything back
and checks it round-trips. No real decoder or Stim circuit involved --
this only tests the harness plumbing itself.

Run:  python3 benchmark_harness/smoke_test.py
"""

import csv
import json
import random
import sys
from pathlib import Path

# Allow running this file directly (python3 benchmark_harness/smoke_test.py)
# as well as as a module (python3 -m benchmark_harness.smoke_test).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark_harness import ExperimentConfig, ResultLogger


def main() -> None:
    cfg = ExperimentConfig(
        experiment_name="smoke_test",
        code="repetition_3",
        decoder="majority_vote",
        noise_model="code_capacity",
        p_values=[0.05, 0.1, 0.2],
        num_trials=1000,
        seed=42,
        notes="harness plumbing check, not a real experiment",
    )
    print(f"Built config: {cfg}")

    logger = ResultLogger(cfg, results_root="results")
    rng = random.Random(cfg.seed)
    for p in cfg.p_values:
        # Fake failure counts standing in for a real decoder run.
        num_failures = sum(1 for _ in range(cfg.num_trials) if rng.random() < p)
        logger.log_p_value(p=p, num_trials=cfg.num_trials, num_failures=num_failures)
        print(f"  p={p}: {num_failures}/{cfg.num_trials} failures logged")

    logger.finalize()
    print(f"\nWrote:\n  {logger.raw_csv_path()}\n  {logger.summary_json_path()}\n  {logger.config_json_path()}")

    # Round-trip checks.
    with open(logger.raw_csv_path()) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(cfg.p_values), "CSV row count mismatch"

    with open(logger.summary_json_path()) as f:
        summary = json.load(f)
    assert summary["experiment_name"] == cfg.experiment_name
    assert len(summary["results"]) == len(cfg.p_values)

    reloaded_cfg = ExperimentConfig.load(logger.config_json_path())
    assert reloaded_cfg == cfg, "config did not round-trip through JSON"

    # Validation should reject a bad config.
    try:
        ExperimentConfig(
            experiment_name="bad config!",
            code="shor_9",
            decoder="majority_vote",
            noise_model="code_capacity",
            p_values=[0.1],
            num_trials=10,
        )
        raise AssertionError("expected ValueError for invalid experiment_name")
    except ValueError as e:
        print(f"\nValidation correctly rejected a bad config: {e}")

    print("\nSMOKE TEST PASSED: config schema + result logging round-trip correctly.")


if __name__ == "__main__":
    main()
