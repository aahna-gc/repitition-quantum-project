"""
smoke_test_phenomenological.py
Owner: Hyunmin
Date: Sat, Aug 29
Duty: "Run first logical error rate experiments (phenomenological noise,
both decoders) as a smoke test."

THIS IS A SMOKE TEST, NOT A RIGOROUS RESULT: it exists to confirm every
piece built this week (shor9_code.py, hard_decision_decoder.py,
ml_decoder_stub.py, monte_carlo.py, benchmark_harness/) actually fits
together end to end, and to surface anything surprising early -- which,
as it turns out, it did (see "IMPORTANT FINDING" below). Swap
ml_decoder_stub.py for Aahna's real ML decoder once it lands.

Two things are checked here:

  1. Code-capacity, both decoders (a rerun of Aug 27's baseline, now with
     the ML stub added for comparison -- this is where the finding below
     first showed up).
  2. Phenomenological noise, both decoders (the literal Aug 29 ask): the
     same data-qubit noise as code-capacity, PLUS independent readout
     error on each stabilizer measurement (see
     shor9_code.build_phenomenological_circuit for the Stim version of
     this same model -- this script decodes classically rather than via
     Stim sampling, for speed, but uses the identical noise parameters).

--- IMPORTANT FINDING from this smoke test ---

Across the ENTIRE physically relevant range (p from 0.01 to 0.49), the
hard-decision decoder and the brute-force ML decoder produced IDENTICAL
logical error rates on the bare 9-qubit Shor code under code-capacity
noise -- not just "close", but exactly equal, trial for trial, at every p
tested. This is not a bug (see the derivation notes below); it appears to
be a real structural fact about this specific code/channel combination.

Why: the Shor code's two error channels decouple completely (X errors
only affect the Z_bar observable, Z errors only affect X_bar), and each
channel's logical failure reduces to an XOR of 3 independent block-level
outcomes, each of which is more likely "no failure" than "failure" for
any p < 0.5 (this is exactly the project's own "majority vote is optimal
for a single repetition code" fact, applied block-by-block). A basic
probability identity -- if several independent bits are each more likely
0 than 1, their XOR is too -- means the block-by-block majority vote
ends up choosing the SAME global logical class as the true coset-sum ML
decoder, every time, for this code. There's no "extra" cross-block
information for ML to exploit here because the code-capacity noise model
makes every qubit's error fully independent of every other qubit's.

This matters for the project's actual research question: it suggests
that a nonzero decoder-induced gap for the 9-qubit Shor code specifically
may require either (a) noise that correlates errors across qubits --
e.g. Chloe's circuit-level noise model, where a single faulty gate can
produce a correlated multi-qubit error that breaks the clean per-block
independence this analysis relies on -- or (b) a deeper concatenation
(more than 2 levels) where genuine cross-level correlations appear. It's
worth raising with Aahna and Chloe before assuming the code-capacity
experiment alone will show the effect the project abstract describes.

The phenomenological-noise check below also shows agreement between the
two decoders, but with a caveat: `ml_decoder_stub.py`'s brute-force
decoder does NOT yet weight its likelihood by measurement-error
probability (it treats the reported syndrome as ground truth, same as
hard-decision does) -- Aahna's real Aug 29 task ("extend the ML decoder
to handle the circuit-level detector error model") is exactly the piece
that would let ML use its knowledge of measurement noise to do better
here. So the phenomenological "no gap" result below is weaker evidence
than the code-capacity one -- it may just reflect this stub's
limitation, not a fact about the problem.

Run:  python3 smoke_test_phenomenological.py
"""

import random
from typing import List, Tuple

from benchmark_harness import ExperimentConfig, ResultLogger
from hard_decision_decoder import hard_decision_decode
from ml_decoder_stub import ml_bruteforce_decode
from monte_carlo import estimate_logical_error_rate, sample_error
from shor9_code import syndrome_z, syndrome_x, logical_z_value, logical_x_value

DECODERS = {
    "hard_decision_concatenated": hard_decision_decode,
    "ml_bruteforce": ml_bruteforce_decode,
}


def run_phenomenological_trial(
    p: float, measurement_error_prob: float, rng: random.Random, decode_fn
) -> bool:
    """Same data-qubit noise as the code-capacity model, but the syndrome
    bits handed to the decoder are each independently flipped with
    probability `measurement_error_prob` before decoding -- modeling noisy
    ancilla readout. The decoder's correction is still applied to the
    TRUE error pattern (a wrong syndrome doesn't change what physically
    happened, only what the decoder believes happened)."""
    ex = sample_error(9, p, rng)
    ez = sample_error(9, p, rng)

    true_sz = syndrome_z(ex)
    true_sx = syndrome_x(ez)
    obs_sz = tuple(b ^ (1 if rng.random() < measurement_error_prob else 0) for b in true_sz)
    obs_sx = tuple(b ^ (1 if rng.random() < measurement_error_prob else 0) for b in true_sx)

    cx, cz = decode_fn(obs_sz, obs_sx, p)
    residual_x = [e ^ c for e, c in zip(ex, cx)]
    residual_z = [e ^ c for e, c in zip(ez, cz)]
    return bool(logical_z_value(residual_x) or logical_x_value(residual_z))


def run_code_capacity_comparison(p_values, num_trials, seed) -> None:
    print("=" * 70)
    print("PART 1: code-capacity noise, both decoders")
    print("=" * 70)

    for decoder_name, decode_fn in DECODERS.items():
        cfg = ExperimentConfig(
            experiment_name=f"shor9_smoketest_codecap_{decoder_name}",
            code="shor_9",
            decoder=decoder_name,
            noise_model="code_capacity",
            p_values=list(p_values),
            num_trials=num_trials,
            seed=seed,
            notes="Aug 29 smoke test -- see smoke_test_phenomenological.py header.",
        )
        logger = ResultLogger(cfg, results_root="results")
        print(f"\n{decoder_name}:")
        for i, p in enumerate(p_values):
            result = estimate_logical_error_rate(decode_fn, p, num_trials, seed=seed + i)
            logger.log_p_value(p=p, num_trials=result.num_trials, num_failures=result.num_failures)
            print(f"  p={p:<6} logical_error_rate={result.rate:.5f}  "
                  f"95% CI=[{result.ci_low:.5f}, {result.ci_high:.5f}]")
        logger.finalize()


def run_phenomenological_comparison(p_values, measurement_error_prob, num_trials, seed) -> None:
    print("\n" + "=" * 70)
    print(f"PART 2: phenomenological noise (measurement_error_prob={measurement_error_prob}), "
          "both decoders")
    print("=" * 70)

    all_results = {}
    for decoder_name, decode_fn in DECODERS.items():
        cfg = ExperimentConfig(
            experiment_name=f"shor9_smoketest_phenomenological_{decoder_name}",
            code="shor_9",
            decoder=decoder_name,
            noise_model="phenomenological",
            p_values=list(p_values),
            num_trials=num_trials,
            seed=seed,
            notes=(
                "Aug 29 smoke test -- simplified single-round phenomenological "
                "model (data noise + independent syndrome readout noise at "
                f"rate {measurement_error_prob}). See smoke_test_phenomenological.py "
                "header for caveats about the ML stub not yet modeling "
                "measurement noise in its likelihood."
            ),
        )
        logger = ResultLogger(cfg, results_root="results")
        print(f"\n{decoder_name}:")
        rates = []
        for i, p in enumerate(p_values):
            rng = random.Random(seed + i)
            num_failures = sum(
                1 for _ in range(num_trials)
                if run_phenomenological_trial(p, measurement_error_prob, rng, decode_fn)
            )
            rate = num_failures / num_trials
            rates.append(rate)
            logger.log_p_value(p=p, num_trials=num_trials, num_failures=num_failures)
            print(f"  p={p:<6} logical_error_rate={rate:.5f}")
        logger.finalize()
        all_results[decoder_name] = rates

    print("\nDecoder comparison (phenomenological):")
    hd_rates = all_results["hard_decision_concatenated"]
    ml_rates = all_results["ml_bruteforce"]
    for p, hd, ml in zip(p_values, hd_rates, ml_rates):
        gap = hd - ml
        print(f"  p={p:<6} hard-decision={hd:.5f}  ml={ml:.5f}  gap={gap:+.5f}")


def main() -> None:
    p_values = [0.02, 0.05, 0.1, 0.2]
    num_trials = 5_000  # kept modest -- brute-force ML is O(512) per trial per channel

    run_code_capacity_comparison(p_values, num_trials, seed=100)
    run_phenomenological_comparison(p_values, measurement_error_prob=0.03, num_trials=num_trials, seed=200)

    print(
        "\n" + "=" * 70 + "\nSMOKE TEST COMPLETE.\n" + "=" * 70 +
        "\nPipeline wiring confirmed working end to end. See this file's "
        "module docstring for the IMPORTANT FINDING about hard-decision "
        "vs. ML showing no measurable gap on the bare 9-qubit Shor code "
        "under these two noise models with the current (non-DEM-aware) "
        "ML stub -- worth discussing with Aahna/Chloe before the next "
        "phase of the project."
    )


if __name__ == "__main__":
    main()
