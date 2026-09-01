"""
benchmark_harness/logger.py
Owner: Hyunmin
Date: Tue, Aug 25

Result logging for decoder-benchmark experiments: one raw CSV row per
(p value, trial-batch) and one JSON summary per experiment. See
conventions.md for exactly where these files land and how they're named.

Usage:

    from benchmark_harness import ExperimentConfig, ResultLogger

    cfg = ExperimentConfig(...)
    logger = ResultLogger(cfg, results_root="results")

    for p in cfg.p_values:
        num_failures = ...  # from actually running the decoder
        logger.log_p_value(p=p, num_trials=cfg.num_trials, num_failures=num_failures)

    logger.finalize()  # writes the CSV and the summary JSON to disk
"""

from __future__ import annotations

import csv
import json
import platform
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from benchmark_harness.config import ExperimentConfig


@dataclass
class PValueResult:
    p: float
    num_trials: int
    num_failures: int

    @property
    def logical_error_rate(self) -> float:
        return self.num_failures / self.num_trials


class ResultLogger:
    """Accumulates per-p-value results for one experiment run, then writes
    both a raw CSV (one row per p value -- easy to load with pandas/Excel)
    and a JSON summary (includes the full config for provenance) to disk.

    Directory convention (see conventions.md for the full writeup):

        results/<experiment_name>/<run_timestamp>_raw.csv
        results/<experiment_name>/<run_timestamp>_summary.json
        results/<experiment_name>/<run_timestamp>_config.json
    """

    def __init__(self, config: ExperimentConfig, results_root: str | Path = "results"):
        self.config = config
        self.results_root = Path(results_root)
        self.run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self._results: List[PValueResult] = []

        self.run_dir = self.results_root / config.experiment_name
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def log_p_value(self, p: float, num_trials: int, num_failures: int) -> None:
        if num_failures > num_trials:
            raise ValueError("num_failures cannot exceed num_trials")
        self._results.append(
            PValueResult(p=p, num_trials=num_trials, num_failures=num_failures)
        )

    # -- file path helpers, exposed so other scripts can find a run's files
    # without duplicating the naming convention --

    def raw_csv_path(self) -> Path:
        return self.run_dir / f"{self.run_timestamp}_raw.csv"

    def summary_json_path(self) -> Path:
        return self.run_dir / f"{self.run_timestamp}_summary.json"

    def config_json_path(self) -> Path:
        return self.run_dir / f"{self.run_timestamp}_config.json"

    def finalize(self) -> None:
        """Write the raw CSV, the config snapshot, and the summary JSON.
        Call this once, after all log_p_value() calls for the run."""
        self._write_raw_csv()
        self.config.save(self.config_json_path())
        self._write_summary_json()

    def _write_raw_csv(self) -> None:
        with open(self.raw_csv_path(), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["p", "num_trials", "num_failures", "logical_error_rate"])
            for r in self._results:
                writer.writerow([r.p, r.num_trials, r.num_failures, r.logical_error_rate])

    def _write_summary_json(self) -> None:
        summary = {
            "experiment_name": self.config.experiment_name,
            "run_timestamp": self.run_timestamp,
            "config": self.config.to_dict(),
            "environment": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
            },
            "results": [
                {
                    "p": r.p,
                    "num_trials": r.num_trials,
                    "num_failures": r.num_failures,
                    "logical_error_rate": r.logical_error_rate,
                }
                for r in self._results
            ],
        }
        with open(self.summary_json_path(), "w") as f:
            json.dump(summary, f, indent=2)
