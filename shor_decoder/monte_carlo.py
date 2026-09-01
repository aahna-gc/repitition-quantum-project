"""
monte_carlo.py
Owner: Hyunmin
Date: Fri, Aug 28
Duty: "Build Monte Carlo sampling + logical error rate computation
infrastructure."

Generalizes the ad hoc loop in run_baseline_experiment.py (Aug 27) into
reusable, decoder-agnostic infrastructure: any decoder that matches the
`(synd_z, synd_x, p) -> (correction_x, correction_z)` interface -- which
both hard_decision_decoder.hard_decision_decode and the ML decoder stub
in ml_decoder_stub.py (Aug 29) satisfy -- can be dropped in.

Adds the piece run_baseline_experiment.py didn't bother with: a proper
confidence interval on the estimated logical error rate (Wilson score
interval, which stays well-behaved even when num_failures is 0 or close
to num_trials -- unlike the naive normal-approximation interval).

Usage:

    from monte_carlo import estimate_logical_error_rate
    from hard_decision_decoder import hard_decision_decode

    result = estimate_logical_error_rate(
        decode_fn=hard_decision_decode, p=0.05, num_trials=20_000, seed=1,
    )
    print(result.rate, result.ci_low, result.ci_high)
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple

from shor9_code import syndrome_z, syndrome_x, logical_z_value, logical_x_value

# A decoder is anything shaped like this. `p` is passed through so
# likelihood-based decoders (the ML stub) can use it; hard-decision
# decoders are free to ignore it.
DecodeFn = Callable[[Sequence[int], Sequence[int], float], Tuple[List[int], List[int]]]


@dataclass
class MonteCarloResult:
    p: float
    num_trials: int
    num_failures: int

    @property
    def rate(self) -> float:
        return self.num_failures / self.num_trials

    @property
    def ci_low(self) -> float:
        return wilson_score_interval(self.num_failures, self.num_trials)[0]

    @property
    def ci_high(self) -> float:
        return wilson_score_interval(self.num_failures, self.num_trials)[1]


def wilson_score_interval(
    num_failures: int, num_trials: int, z: float = 1.96
) -> Tuple[float, float]:
    """95% (default z=1.96) Wilson score confidence interval for a binomial
    proportion. Preferred over the naive p +/- z*sqrt(p(1-p)/n) interval
    because it doesn't produce nonsensical bounds outside [0, 1] and stays
    sane even at num_failures=0 -- which matters a lot here, since the
    lowest p values in a sweep can easily produce zero failures out of
    tens of thousands of trials."""
    if num_trials == 0:
        return (0.0, 1.0)
    n = num_trials
    phat = num_failures / n
    denom = 1 + z ** 2 / n
    center = phat + z ** 2 / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) + z ** 2 / (4 * n)) / n)
    low = (center - margin) / denom
    high = (center + margin) / denom
    return max(0.0, low), min(1.0, high)


def sample_error(n: int, p: float, rng: random.Random) -> List[int]:
    return [1 if rng.random() < p else 0 for _ in range(n)]


def run_one_trial(p: float, rng: random.Random, decode_fn: DecodeFn) -> bool:
    """One code-capacity trial: sample X and Z errors independently at
    rate p, decode, and report whether a logical error resulted (either
    observable flipped). Shared by every decoder we benchmark."""
    ex = sample_error(9, p, rng)
    ez = sample_error(9, p, rng)

    sz = syndrome_z(ex)
    sx = syndrome_x(ez)
    cx, cz = decode_fn(sz, sx, p)

    residual_x = [e ^ c for e, c in zip(ex, cx)]
    residual_z = [e ^ c for e, c in zip(ez, cz)]

    return bool(logical_z_value(residual_x) or logical_x_value(residual_z))


def estimate_logical_error_rate(
    decode_fn: DecodeFn, p: float, num_trials: int, seed: int = 0
) -> MonteCarloResult:
    """Runs `num_trials` independent code-capacity trials through
    `decode_fn` and returns the resulting MonteCarloResult (failure count,
    point estimate, and -- via .ci_low/.ci_high -- a 95% Wilson interval)."""
    rng = random.Random(seed)
    num_failures = sum(1 for _ in range(num_trials) if run_one_trial(p, rng, decode_fn))
    return MonteCarloResult(p=p, num_trials=num_trials, num_failures=num_failures)


def sweep_logical_error_rate(
    decode_fn: DecodeFn, p_values: Sequence[float], num_trials: int, seed: int = 0
) -> List[MonteCarloResult]:
    """Convenience wrapper: run estimate_logical_error_rate for a list of p
    values, using a distinct (but reproducible) sub-seed per p value so
    sweeps don't accidentally reuse the exact same error draws across p."""
    results = []
    for i, p in enumerate(p_values):
        results.append(
            estimate_logical_error_rate(decode_fn, p, num_trials, seed=seed + i)
        )
    return results


def _demo() -> None:
    from hard_decision_decoder import hard_decision_decode

    print("Monte Carlo infrastructure smoke check: hard-decision decoder, "
          "p=0.05, 20,000 trials")
    result = estimate_logical_error_rate(
        hard_decision_decode, p=0.05, num_trials=20_000, seed=7
    )
    print(f"  logical error rate = {result.rate:.5f}  "
          f"(95% CI: [{result.ci_low:.5f}, {result.ci_high:.5f}])  "
          f"({result.num_failures}/{result.num_trials} failures)")

    print("\nZero-failure edge case (very small p, few trials) -- confirms "
          "the Wilson interval stays sane instead of collapsing to [0, 0]:")
    result0 = estimate_logical_error_rate(
        hard_decision_decode, p=0.001, num_trials=200, seed=7
    )
    print(f"  {result0.num_failures}/{result0.num_trials} failures, "
          f"95% CI: [{result0.ci_low:.5f}, {result0.ci_high:.5f}]")


if __name__ == "__main__":
    _demo()
