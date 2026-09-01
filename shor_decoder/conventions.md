# Directory & filename conventions

**Owner:** Hyunmin
**Date:** Tue, Aug 25
**Duty:** *"Build benchmarking harness scaffolding: experiment config schema,
result logging (CSV/JSON), directory conventions. (make sure to let others
know what filenames correlate to what)"*

This is the "let others know what filenames correlate to what" writeup for
the harness, so Aahna and Chloe can plug their decoder / circuit code into
it without guessing paths.

## Project layout

```
shor_decoder_project/
├── requirements.txt                        # pinned stim/pymatching/numpy
├── day1_stim_tutorial.py                   # Hyunmin, Aug 18 — Stim basics
├── day2_noise_models_and_pymatching.py     # Hyunmin, Aug 23 — noise models + pymatching survey
├── day3_majority_vote_notes.md             # Hyunmin, Aug 24 — literature notes
├── day3_majority_vote_demo.py              # Hyunmin, Aug 24 — toy info-loss demo
├── shor9_code.py                           # Hyunmin, Aug 26 — CSS code definition (Hz/Hx/Lz/Lx) + Stim circuit builders (stand-in for Chloe's shor_code_circuit.py)
├── hard_decision_decoder.py                # Hyunmin, Aug 26 — two-level majority-vote decoder
├── run_baseline_experiment.py              # Hyunmin, Aug 27 — first end-to-end baseline run
├── monte_carlo.py                          # Hyunmin, Aug 28 — reusable Monte Carlo + Wilson CI infrastructure
├── ml_decoder_stub.py                      # Hyunmin, Aug 29 — brute-force ML decoder (stand-in for Aahna's real decoder)
├── smoke_test_phenomenological.py          # Hyunmin, Aug 29 — phenomenological-noise smoke test, both decoders
├── benchmark_harness/                      # Hyunmin, Aug 25 — shared scaffolding
│   ├── __init__.py
│   ├── config.py                           # ExperimentConfig schema
│   ├── logger.py                           # ResultLogger (CSV + JSON)
│   ├── conventions.md                      # this file
│   └── smoke_test.py                       # end-to-end sanity check
├── configs/                                # saved ExperimentConfig JSON files
│   └── <experiment_name>.json
└── results/
    └── <experiment_name>/
        ├── <run_timestamp>_raw.csv         # one row per p value
        ├── <run_timestamp>_summary.json    # full config + results + env info
        └── <run_timestamp>_config.json     # config snapshot for this exact run
```

`<run_timestamp>` is UTC, formatted `YYYYMMDDTHHMMSSZ` (e.g.
`20260825T140302Z`), generated automatically by `ResultLogger` at
construction time — every file from one run shares the same timestamp, so
`ls results/<experiment_name>/` sorts runs chronologically and groups each
run's three files together.

## Naming `experiment_name`

Use `<code>_<decoder>` or `<code>_<comparison>`, e.g.:

- `repetition3_majority_vote` — the zero-gap control
- `shor9_hard_decision_concatenated` — Treatment A
- `shor9_ml_bruteforce` — Treatment B
- `shor9_ml_vs_hard_decision` — if logging both decoders into one combined
  sweep/comparison run

`experiment_name` must be filesystem-safe (letters, digits, `_`, `-` only)
— `ExperimentConfig` validates this at construction time and raises
immediately if not, rather than failing later when a path gets built.

## Whose code writes what

- **Chloe's Shor-code circuit**: as of Aug 29 she owns the *real*
  circuit-level / phenomenological memory circuit (started Aug 26,
  p-swept Aug 28-29). Until her file lands at the project root (expected
  name: `shor_code_circuit.py`, matching the interface below), everything
  here uses `shor9_code.py`'s `build_code_capacity_circuit(p)` /
  `build_phenomenological_circuit(p)` as a stand-in — same interface
  (function of `p` returning a `stim.Circuit` with DETECTOR/
  OBSERVABLE_INCLUDE already declared), so swapping her real one in later
  should be a one-line change per script.
- **Aahna's ML decoder**: her real exact-enumeration decoder (started Aug
  26, unit-tested Aug 27, vectorized Aug 28, extended to circuit-level DEM
  Aug 29) should land as `ml_decoder.py`, matching the
  `(synd_z, synd_x, p) -> (correction_x, correction_z)` interface used by
  `monte_carlo.DecodeFn`. Until then, `ml_decoder_stub.py` (Hyunmin, Aug
  29) is a minimal, unoptimized brute-force placeholder with the same
  interface — correct but O(512) per channel per trial, not meant for
  large sweeps.
- **The hard-decision baseline decoder**: `hard_decision_decoder.py`
  (Hyunmin, Aug 26) — the two-level majority-vote decoder described in
  the project abstract. Done.
- **CSS code data** (Hz/Hx/Lz/Lx, i.e. which qubits make up which
  stabilizer/logical operator): `shor9_code.py` (Hyunmin, Aug 26) is the
  single source of truth. Both decoders and both circuit builders import
  from here — if the code's qubit layout ever changes, this is the only
  file that needs to change.
- **Monte Carlo / logical-error-rate estimation**: `monte_carlo.py`
  (Hyunmin, Aug 28) — decoder-agnostic, works with either decoder above
  via the shared interface, includes Wilson-interval confidence bounds.
- All of the above feed into `benchmark_harness.ExperimentConfig` +
  `benchmark_harness.ResultLogger` so results land in a consistent place
  regardless of who ran the experiment.

### Note on `noise_model` values

`ExperimentConfig.noise_model` now accepts `"code_capacity"` (single-shot,
perfect syndrome extraction) or `"phenomenological"` (added Aug 29 —
noisy syndrome readout too). Circuit-level noise (Chloe's Aug 26/28/29
work: gate errors, idling errors) doesn't have a slot yet — add it to
`VALID_NOISE_MODELS` in `config.py` once her circuit is ready to benchmark
directly rather than through a stand-in.

### Flag for the team: see smoke_test_phenomenological.py

The Aug 29 smoke test found that hard-decision and brute-force ML give
**identical** logical error rates on the bare 9-qubit Shor code under
both noise models tested here, across the whole p range checked
(0.02-0.49). The script's module docstring has the full reasoning; the
short version is that each of the Shor code's two error channels
decouples into 3 independent block-level votes that are each already
below the 50% break-even point for any p < 0.5, which forces the
block-by-block majority vote to agree with true ML every time for this
particular code/noise combination. Worth a conversation before assuming
the code-capacity experiment on the bare Shor-9 code will show the gap
the project is trying to measure — it may take circuit-level (correlated)
noise, or a deeper concatenation, to see it.

## Sanity check

Run `python3 benchmark_harness/smoke_test.py` to confirm the config
schema + logger work end-to-end (writes a throwaway experiment under
`results/smoke_test/` using fake pass/fail numbers, no real decoder
involved).
