"""
benchmark_harness
Owner: Hyunmin
Date: Tue, Aug 25
Duty: "Build benchmarking harness scaffolding: experiment config schema,
result logging (CSV/JSON), directory conventions."

Public API re-exported here for convenience:

    from benchmark_harness import ExperimentConfig, ResultLogger

See benchmark_harness/conventions.md for the directory/filename conventions
every teammate's scripts should follow when they plug into this harness.
"""

from benchmark_harness.config import ExperimentConfig
from benchmark_harness.logger import ResultLogger

__all__ = ["ExperimentConfig", "ResultLogger"]
