"""
ml_decoder_stub.py
Owner: Hyunmin (STAND-IN for Aahna's real ML decoder)
Date: Sat, Aug 29 (built only so Hyunmin's Aug 29 smoke test can exercise
"both decoders" without being blocked on Aahna's actual implementation)

Aahna's assigned work (Aug 26: exact enumeration + coset classes; Aug 27:
unit tests; Aug 28: vectorized optimization; Aug 29: extend to the
circuit-level DEM) is the project's real ML decoder. This file is a
minimal, deliberately UNOPTIMIZED brute-force stand-in with the same
external behavior, so `smoke_test_phenomenological.py` has something to
compare the hard-decision decoder against today. Swap this out for
Aahna's real module (matching this same `(synd_z, synd_x, p) ->
(correction_x, correction_z)` interface -- see monte_carlo.py's DecodeFn)
once it lands.

Method: true coset-sum maximum likelihood, exactly as described in the
project abstract -- for each channel, enumerate all 2^9 = 512 possible
error patterns, keep the ones consistent with the observed syndrome, sum
their prior probabilities (iid rate p per qubit) grouped by which logical
class they'd produce, and decide the class with more total probability
mass. This is NOT the same as "guess the single most-likely error
pattern" (that would just be a min-weight decoder) -- summing over every
degenerate error consistent with a given logical outcome is exactly the
"exact enumeration over syndromes and logical coset classes" Aahna's Aug
26 task describes, and it's what should show the gap over hard-decision
decoding (which never considers degeneracy at all).

Deliberately not vectorized / not cached beyond the top-level candidate
list -- that optimization is explicitly Aahna's Aug 28 task, not
duplicated here.
"""

from __future__ import annotations

import itertools
from typing import List, Sequence, Tuple

from shor9_code import (
    NUM_QUBITS,
    syndrome_z,
    syndrome_x,
    logical_z_value,
    logical_x_value,
)

_ALL_PATTERNS: List[Tuple[int, ...]] = list(
    itertools.product([0, 1], repeat=NUM_QUBITS)
)


def _ml_decode_channel(
    observed_syndrome: Sequence[int],
    p: float,
    syndrome_fn,
    logical_fn,
) -> List[int]:
    """Shared brute-force coset-sum ML routine for either channel."""
    observed_syndrome = tuple(observed_syndrome)
    summed_prob = {0: 0.0, 1: 0.0}
    representative = {0: None, 1: None}

    for candidate in _ALL_PATTERNS:
        if syndrome_fn(candidate) != observed_syndrome:
            continue
        weight = sum(candidate)
        prob = (p ** weight) * ((1 - p) ** (NUM_QUBITS - weight))
        lv = logical_fn(candidate)
        summed_prob[lv] += prob
        if representative[lv] is None:
            representative[lv] = candidate

    ml_logical_class = 0 if summed_prob[0] >= summed_prob[1] else 1
    rep = representative[ml_logical_class]
    assert rep is not None, (
        "every syndrome's coset splits evenly between logical classes, so "
        "this should never be None -- if it is, syndrome_fn/logical_fn "
        "disagree with shor9_code's definitions"
    )
    return list(rep)


def ml_bruteforce_decode(
    synd_z: Sequence[int], synd_x: Sequence[int], p: float
) -> Tuple[List[int], List[int]]:
    """Brute-force ML decoder, same call signature as
    hard_decision_decoder.hard_decision_decode so both can be dropped into
    monte_carlo.estimate_logical_error_rate interchangeably."""
    cx = _ml_decode_channel(synd_z, p, syndrome_z, logical_z_value)
    cz = _ml_decode_channel(synd_x, p, syndrome_x, logical_x_value)
    return cx, cz


def _run_unit_tests() -> None:
    """A handful of hand-checkable cases, including the degenerate one
    that hard_decision_decoder.py gets wrong by construction (2 blocks bad
    looks identical, syndrome-wise, to 1 block bad -- ML should correctly
    weigh the lower-weight explanation as more likely, same conclusion as
    hard-decision here, but for cases where hard-decision breaks ties
    using local-only per-block info, ML uses the true global posterior)."""

    def xor(a, b):
        return [x ^ y for x, y in zip(a, b)]

    p = 0.1

    # No errors: ML should also correct nothing.
    ex = [0] * 9
    sz = syndrome_z(ex)
    cx = ml_bruteforce_decode(sz, (0, 0), p)[0]
    assert logical_z_value(xor(ex, cx)) == 0, "ML should recover from no errors"
    print("  PASS: no errors -> no logical flip")

    # Single X error: ML should correct it (same as hard-decision).
    ex = [1, 0, 0, 0, 0, 0, 0, 0, 0]
    sz = syndrome_z(ex)
    cx = ml_bruteforce_decode(sz, (0, 0), p)[0]
    assert logical_z_value(xor(ex, cx)) == 0, "ML should correct a single X error"
    print("  PASS: single X error -> corrected")

    # Double X error in one block: at p<0.5 the lower-weight (single-error)
    # explanation is still more likely, so ML makes the SAME call as
    # hard-decision here (both "fail" relative to the true double-error) --
    # this demonstrates degeneracy alone doesn't save you; the gap shows up
    # statistically, not on every individual hard case.
    ex = [1, 1, 0, 0, 0, 0, 0, 0, 0]
    sz = syndrome_z(ex)
    cx = ml_bruteforce_decode(sz, (0, 0), p)[0]
    assert logical_z_value(xor(ex, cx)) == 1, (
        "ML also 'fails' this specific double-error case -- expected, "
        "since weight-1 is genuinely more probable than weight-2 at p=0.1"
    )
    print("  PASS: double X error in one block -> ML agrees with hard-decision "
          "here (this case isn't where the gap comes from)")

    print("\nAll ml_decoder_stub sanity checks passed.")


if __name__ == "__main__":
    _run_unit_tests()

    print("\nTiming note: brute force enumerates 512 candidates per channel, "
          "per trial, with no caching beyond the candidate list -- fine for "
          "a smoke test, not for a production sweep (that's Aahna's Aug 28 "
          "vectorization work).")
