"""
benchmark_harness/config.py
Owner: Hyunmin
Date: Tue, Aug 25

Defines the experiment config schema every decoder-benchmark run should
use, so that Aahna's ML decoder, Chloe's Shor-code circuit, and any
majority-vote baseline all get compared under an identically-specified
experiment -- same code, same noise model, same trial count, same p sweep.

Usage:

    from benchmark_harness import ExperimentConfig

    cfg = ExperimentConfig(
        experiment_name="shor9_ml_vs_hard_decision",
        code="shor_9",
        decoder="ml_bruteforce",
        noise_model="code_capacity",
        p_values=[0.01, 0.02, 0.05, 0.1, 0.15, 0.2],
        num_trials=50_000,
        seed=1234,
    )
    cfg.save("configs/shor9_ml_vs_hard_decision.json")
    cfg2 = ExperimentConfig.load("configs/shor9_ml_vs_hard_decision.json")
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional


# Codes and decoders this project is scoped to compare. Keeping these as
# validated string enums (rather than free text) means a typo in a config
# fails loudly at construction time instead of silently producing an
# empty/mismatched results file later.
VALID_CODES = {"repetition_3", "shor_9"}
VALID_DECODERS = {"majority_vote", "hard_decision_concatenated", "ml_bruteforce"}
VALID_NOISE_MODELS = {"code_capacity", "phenomenological"}


@dataclass
class ExperimentConfig:
    """Schema for a single decoder-benchmark experiment.

    Fields
    ------
    experiment_name : short, filesystem-safe identifier. Used to name the
        results subdirectory (see conventions.md) -- keep it stable across
        reruns of "the same" experiment so results accumulate sensibly.
    code : which code is being decoded.
        - "repetition_3": bare 3-qubit repetition code (the zero-gap control)
        - "shor_9": the full 9-qubit Shor code
    decoder : which decoding strategy to benchmark.
        - "majority_vote": single-level hard-decision majority vote
          (only meaningful for code="repetition_3")
        - "hard_decision_concatenated": standard level-by-level majority
          vote applied to the concatenated code (code="shor_9")
        - "ml_bruteforce": exact maximum-likelihood decoder, enumerating
          all error patterns (valid for either code, used as the ceiling)
    noise_model : which noise model generates errors. Only "code_capacity"
        (single-shot iid noise, perfect syndrome extraction) is in scope
        for this project -- see day2_noise_models_and_pymatching.py notes
        on why code-capacity isolates decoder effects most cleanly.
    p_values : list of physical error rates to sweep over.
    num_trials : Monte Carlo shots per p value.
    seed : RNG seed, recorded for reproducibility.
    notes : free-text field for anything not captured by the schema
        (e.g. "control run for Aug 29 comparison").
    """

    experiment_name: str
    code: str
    decoder: str
    noise_model: str
    p_values: List[float]
    num_trials: int
    seed: int = 0
    notes: str = ""

    def __post_init__(self) -> None:
        if self.code not in VALID_CODES:
            raise ValueError(f"code must be one of {VALID_CODES}, got {self.code!r}")
        if self.decoder not in VALID_DECODERS:
            raise ValueError(
                f"decoder must be one of {VALID_DECODERS}, got {self.decoder!r}"
            )
        if self.noise_model not in VALID_NOISE_MODELS:
            raise ValueError(
                f"noise_model must be one of {VALID_NOISE_MODELS}, "
                f"got {self.noise_model!r}"
            )
        if not self.p_values:
            raise ValueError("p_values must be non-empty")
        if any(not (0.0 <= p <= 1.0) for p in self.p_values):
            raise ValueError("all p_values must be in [0, 1]")
        if self.num_trials <= 0:
            raise ValueError("num_trials must be positive")
        if not self.experiment_name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "experiment_name should be filesystem-safe "
                "(letters, digits, '_' and '-' only)"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ExperimentConfig":
        return cls(**d)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "ExperimentConfig":
        with open(path) as f:
            return cls.from_dict(json.load(f))
