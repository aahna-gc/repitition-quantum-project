"""
run_baseline_experiment.py
Owner: Hyunmin
Date: Thu, Aug 27
Duty: "Wire the majority-vote decoder into the pipeline; run first
end-to-end baseline experiment."

"The pipeline" = benchmark_harness (Aug 25: ExperimentConfig + ResultLogger)
+ the CSS code definitions in shor9_code.py (Aug 26) + the hard-decision
decoder (Aug 26). This script is the first time all of those pieces are
run together, end to end, for real: sample random errors under the
code-capacity noise model, decode with hard_decision_decoder, check
against shor9_code's logical operators, and log results the same way
every future experiment (Aahna's ML decoder included) will.

This is intentionally a simple, direct loop -- Aahna/Hyunmin generalize
this into reusable Monte Carlo infrastructure on Aug 28
(monte_carlo.py). Aug 27's job is just "does the wiring work end to end."

Run:  python3 run_baseline_experiment.py
"""

import random
from typing import List

from benchmark_harness import ExperimentConfig, ResultLogger
from hard_decision_decoder import hard_decision_decode
from shor9_code import syndrome_z, syndrome_x, logical_z_value, logical_x_value


def sample_error(n: int, p: float, rng: random.Random) -> List[int]:
    return [1 if rng.random() < p else 0 for _ in range(n)]


def run_one_trial(p: float, rng: random.Random) -> bool:
    """Returns True iff this trial ends in a logical error (either Z_bar
    or X_bar flipped) after hard-decision decoding."""
    ex = sample_error(9, p, rng)
    ez = sample_error(9, p, rng)

    sz = syndrome_z(ex)
    sx = syndrome_x(ez)
    cx, cz = hard_decision_decode(sz, sx)

    residual_x = [e ^ c for e, c in zip(ex, cx)]
    residual_z = [e ^ c for e, c in zip(ez, cz)]

    return bool(logical_z_value(residual_x) or logical_x_value(residual_z))


def main() -> None:
    cfg = ExperimentConfig(
        experiment_name="shor9_hard_decision_baseline",
        code="shor_9",
        decoder="hard_decision_concatenated",
        noise_model="code_capacity",
        p_values=[0.01, 0.02, 0.05, 0.1, 0.15, 0.2],
        num_trials=20_000,
        seed=2026,
        notes=(
            "First end-to-end baseline experiment (Aug 27). Uses the "
            "two-level majority-vote decoder from hard_decision_decoder.py "
            "against shor9_code.py's code-capacity noise model."
        ),
    )
    print(f"Running: {cfg.experiment_name}")
    print(f"  decoder={cfg.decoder}, code={cfg.code}, noise_model={cfg.noise_model}")
    print(f"  p_values={cfg.p_values}, num_trials={cfg.num_trials}\n")

    logger = ResultLogger(cfg, results_root="results")
    rng = random.Random(cfg.seed)

    for p in cfg.p_values:
        num_failures = sum(1 for _ in range(cfg.num_trials) if run_one_trial(p, rng))
        rate = num_failures / cfg.num_trials
        logger.log_p_value(p=p, num_trials=cfg.num_trials, num_failures=num_failures)
        print(f"  p={p:<6} -> {num_failures:>5}/{cfg.num_trials} failures "
              f"(logical error rate = {rate:.5f})")

    logger.finalize()
    print(f"\nWrote:\n  {logger.raw_csv_path()}\n  {logger.summary_json_path()}\n  "
          f"{logger.config_json_path()}")

    print(
        "\nSanity check: logical error rate should grow roughly like O(p^2) "
        "for small p (Shor code has distance 3) -- eyeball the p=0.01 vs "
        "p=0.02 rows above; doubling p should roughly quadruple the rate."
    )


if __name__ == "__main__":
    main()
