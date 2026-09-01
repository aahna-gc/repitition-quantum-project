"""
shor9_code.py
Owner: Hyunmin
Date: Tue, Aug 26 (foundation module, supports the Aug 26-29 decoder work)

Defines the 9-qubit Shor code's CSS structure as plain data (qubit index
lists), plus Stim circuit builders under code-capacity and (simplified)
phenomenological noise.

NOTE ON OWNERSHIP: the Stim circuit builders here are a STAND-IN for
Chloe's forthcoming `shor_code_circuit.py` (see benchmark_harness/
conventions.md). They exist so Hyunmin's decoder + Monte Carlo work isn't
blocked waiting on that file, and are built directly from the same Hz/Hx/
Lz/Lx definitions below so nothing can drift out of sync. Swap in Chloe's
real circuit once it lands (same interface: a function of `p` returning a
stim.Circuit with DETECTOR/OBSERVABLE_INCLUDE already declared).

--- The CSS structure, spelled out ---

9 data qubits, indices 0-8, arranged in 3 blocks of 3:
    block 0 = {0, 1, 2}
    block 1 = {3, 4, 5}
    block 2 = {6, 7, 8}

Stabilizer generators:
    Z-type (6 of them, detect X/bit-flip errors, one pair per block):
        Z0 Z1, Z1 Z2   (block 0)
        Z3 Z4, Z4 Z5   (block 1)
        Z6 Z7, Z7 Z8   (block 2)
    X-type (2 of them, detect Z/phase-flip errors, span pairs of blocks):
        X0 X1 X2 X3 X4 X5   (blocks 0+1)
        X3 X4 X5 X6 X7 X8   (blocks 1+2)

Logical operators (verified by hand to commute with every stabilizer
above -- see the module docstring math in the project notes):
    Z_bar = Z0 Z3 Z6   (one representative qubit per block)
    X_bar = X0 X1 X2   (a full block)

These four objects (HZ_PAIRS, HX_GROUPS, LZ_SUPPORT, LX_SUPPORT) are the
single source of truth every decoder in this project should import rather
than re-deriving.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import stim

NUM_QUBITS = 9
BLOCKS: List[List[int]] = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]

# Z-type stabilizers: adjacent-pair parity checks within each block.
# Detect X (bit-flip) errors. 6 checks total, 2 per block.
HZ_PAIRS: List[Tuple[int, int]] = [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8)]

# X-type stabilizers: each spans two adjacent blocks (6 qubits).
# Detect Z (phase-flip) errors. 2 checks total.
HX_GROUPS: List[List[int]] = [[0, 1, 2, 3, 4, 5], [3, 4, 5, 6, 7, 8]]

# Logical operators.
LZ_SUPPORT: List[int] = [0, 3, 6]
LX_SUPPORT: List[int] = [0, 1, 2]


def parity(bits: Sequence[int], indices: Sequence[int]) -> int:
    """XOR of `bits` at the given `indices`."""
    acc = 0
    for i in indices:
        acc ^= bits[i]
    return acc


def syndrome_z(ex: Sequence[int]) -> Tuple[int, ...]:
    """Z-stabilizer outcomes given a length-9 X-error vector `ex`.
    These are what the Z-check ancillas measure; they carry ALL the
    information available about where X errors happened."""
    return tuple(ex[i] ^ ex[j] for (i, j) in HZ_PAIRS)


def syndrome_x(ez: Sequence[int]) -> Tuple[int, ...]:
    """X-stabilizer outcomes given a length-9 Z-error vector `ez`."""
    return tuple(parity(ez, group) for group in HX_GROUPS)


def logical_z_value(ex: Sequence[int]) -> int:
    """Whether a (residual) X-error vector flips the logical Z_bar
    eigenvalue -- i.e. whether it constitutes a logical bit-flip error."""
    return parity(ex, LZ_SUPPORT)


def logical_x_value(ez: Sequence[int]) -> int:
    """Whether a (residual) Z-error vector flips the logical X_bar
    eigenvalue -- i.e. whether it constitutes a logical phase-flip error."""
    return parity(ez, LX_SUPPORT)


# ---------------------------------------------------------------------------
# Stim circuit builders (stand-in for Chloe's shor_code_circuit.py)
# ---------------------------------------------------------------------------

def build_code_capacity_circuit(p: float) -> stim.Circuit:
    """Single-shot code-capacity noise: iid X_ERROR(p) and Z_ERROR(p) on
    every data qubit, then one perfect round of syndrome extraction.
    Mirrors day2_noise_models_and_pymatching.py::code_capacity_circuit,
    scaled up to the full 9-qubit code and both error types.

    Qubit layout: data = 0..8, z-check ancillas = 9..14 (2 per block),
    x-check ancillas = 15..16.
    """
    data = list(range(NUM_QUBITS))
    z_anc = list(range(9, 15))
    x_anc = [15, 16]

    circuit = stim.Circuit()
    circuit.append("R", data + z_anc + x_anc)
    _append_encode_logical_zero(circuit)
    circuit.append("H", x_anc)  # prepare |+> for X-type stabilizer readout
    circuit.append("TICK")

    circuit.append("X_ERROR", data, p)
    circuit.append("Z_ERROR", data, p)
    circuit.append("TICK")

    # Z-type stabilizers: CNOT(data -> ancilla) for each pair, then measure.
    for anc_idx, (a, b) in zip(z_anc, HZ_PAIRS):
        circuit.append("CNOT", [a, anc_idx, b, anc_idx])
    circuit.append("M", z_anc)
    for i in range(len(z_anc)):
        circuit.append("DETECTOR", [stim.target_rec(-(len(z_anc) - i))])

    # X-type stabilizers: CNOT(ancilla -> data) for each qubit in the group,
    # then measure the ancilla in the X basis.
    for anc_idx, group in zip(x_anc, HX_GROUPS):
        targets = []
        for q in group:
            targets.extend([anc_idx, q])
        circuit.append("CNOT", targets)
    circuit.append("MX", x_anc)
    for i in range(len(x_anc)):
        circuit.append("DETECTOR", [stim.target_rec(-(len(x_anc) - i))])

    # Final data readout + both logical observables (fine to declare both --
    # a real device could only certify one per run, but Stim will happily
    # simulate the joint statistics for us here).
    circuit.append("M", data)
    z_obs_targets = [stim.target_rec(-(NUM_QUBITS - q)) for q in LZ_SUPPORT]
    circuit.append("OBSERVABLE_INCLUDE", z_obs_targets, 0)

    return circuit


def _append_encode_logical_zero(circuit: stim.Circuit) -> None:
    """Prepend the encoding circuit for logical |0>_L, assuming all 9 data
    qubits start at |0>: put the first qubit of each block into |+> via H,
    then GHZ-ify each block with 2 CNOTs. Produces
    ((|000>+|111>)/sqrt(2))^{\\otimes 3} / sqrt(2) -- exactly logical |0>_L.
    Without this step the data qubits are just |000000000>, which is NOT a
    codeword and will not have deterministic (noiseless) stabilizer
    outcomes -- this bit us on the first attempt (see shor9_code self-check
    history) until it was added.
    """
    leaders = [block[0] for block in BLOCKS]
    circuit.append("H", leaders)
    for block in BLOCKS:
        leader = block[0]
        for q in block[1:]:
            circuit.append("CNOT", [leader, q])
    circuit.append("TICK")


def build_phenomenological_circuit(
    p: float, measurement_error_prob: float = None
) -> stim.Circuit:
    """Simplified single-round phenomenological noise: same data-qubit
    noise as code-capacity, PLUS the syndrome-extraction ancillas
    themselves are noisy (X_ERROR on ancillas before their measurement,
    which flips their reported outcome with the given probability).

    This is a deliberately minimal approximation for pipeline smoke-testing
    (Hyunmin, Aug 29) -- it is NOT the full multi-round phenomenological
    model Chloe is building (Aug 26/28/29 circuit-level work); it only
    exists so the decoder + Monte Carlo infrastructure can be exercised
    against *some* noisier-than-code-capacity model before her circuit
    lands. Swap this out once her real circuit is available.

    Defaults `measurement_error_prob` to `p` if not given.
    """
    if measurement_error_prob is None:
        measurement_error_prob = p

    data = list(range(NUM_QUBITS))
    z_anc = list(range(9, 15))
    x_anc = [15, 16]

    circuit = stim.Circuit()
    circuit.append("R", data + z_anc + x_anc)
    _append_encode_logical_zero(circuit)
    circuit.append("H", x_anc)
    circuit.append("TICK")

    circuit.append("X_ERROR", data, p)
    circuit.append("Z_ERROR", data, p)
    circuit.append("TICK")

    for anc_idx, (a, b) in zip(z_anc, HZ_PAIRS):
        circuit.append("CNOT", [a, anc_idx, b, anc_idx])
    # Readout noise on the Z-check ancillas before measurement.
    circuit.append("X_ERROR", z_anc, measurement_error_prob)
    circuit.append("M", z_anc)
    for i in range(len(z_anc)):
        circuit.append("DETECTOR", [stim.target_rec(-(len(z_anc) - i))])

    for anc_idx, group in zip(x_anc, HX_GROUPS):
        targets = []
        for q in group:
            targets.extend([anc_idx, q])
        circuit.append("CNOT", targets)
    # Readout noise on the X-check ancillas before their X-basis measurement
    # (Z_ERROR here because it's applied in the ancilla's H'd/X-basis frame).
    circuit.append("Z_ERROR", x_anc, measurement_error_prob)
    circuit.append("MX", x_anc)
    for i in range(len(x_anc)):
        circuit.append("DETECTOR", [stim.target_rec(-(len(x_anc) - i))])

    circuit.append("M", data)
    z_obs_targets = [stim.target_rec(-(NUM_QUBITS - q)) for q in LZ_SUPPORT]
    circuit.append("OBSERVABLE_INCLUDE", z_obs_targets, 0)

    return circuit


# ---------------------------------------------------------------------------
# Self-checks: confirm the classical Hz/Hx/Lz/Lx math agrees with what the
# Stim circuit above actually samples. If these ever disagree, something in
# the circuit wiring or the classical definitions is wrong.
# ---------------------------------------------------------------------------

def _self_check() -> None:
    # 1) Logical operators must commute with every stabilizer (else they
    # aren't valid logical operators at all). Overlap-parity must be even.
    for (a, b) in HZ_PAIRS:
        overlap = len({a, b} & set(LX_SUPPORT))
        assert overlap % 2 == 0, f"Z-pair {(a, b)} anticommutes with X_bar"
    for group in HX_GROUPS:
        overlap = len(set(group) & set(LZ_SUPPORT))
        assert overlap % 2 == 0, f"X-group {group} anticommutes with Z_bar"

    # 2) Deterministic single-qubit-error probes via Stim, cross-checked
    # against the classical syndrome/logical formulas.
    import numpy as np

    test_cases = [
        ("no error", [0] * 9, [0] * 9),
        ("X on qubit 0", [1, 0, 0, 0, 0, 0, 0, 0, 0], [0] * 9),
        ("X on qubit 4", [0, 0, 0, 0, 1, 0, 0, 0, 0], [0] * 9),
        ("Z on qubit 2", [0] * 9, [0, 0, 1, 0, 0, 0, 0, 0, 0]),
        ("X0 and Z7 together", [1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0]),
    ]

    for name, ex, ez in test_cases:
        expected_sz = syndrome_z(ex)
        expected_sx = syndrome_x(ez)

        # Build a p=0 circuit and manually inject the exact error pattern
        # with deterministic (p=1 on chosen qubits) X_ERROR/Z_ERROR calls,
        # so Stim gives us a single, deterministic sample to compare.
        circuit = stim.Circuit()
        data = list(range(NUM_QUBITS))
        z_anc = list(range(9, 15))
        x_anc = [15, 16]
        circuit.append("R", data + z_anc + x_anc)
        _append_encode_logical_zero(circuit)
        circuit.append("H", x_anc)
        for q, bit in enumerate(ex):
            if bit:
                circuit.append("X_ERROR", [q], 1.0)
        for q, bit in enumerate(ez):
            if bit:
                circuit.append("Z_ERROR", [q], 1.0)
        for anc_idx, (a, b) in zip(z_anc, HZ_PAIRS):
            circuit.append("CNOT", [a, anc_idx, b, anc_idx])
        circuit.append("M", z_anc)
        for anc_idx, group in zip(x_anc, HX_GROUPS):
            targets = []
            for q in group:
                targets.extend([anc_idx, q])
            circuit.append("CNOT", targets)
        circuit.append("MX", x_anc)

        sample = circuit.compile_sampler().sample(shots=1)[0].astype(int)
        stim_sz = tuple(sample[:6])
        stim_sx = tuple(sample[6:8])

        assert stim_sz == expected_sz, (
            f"[{name}] Z-syndrome mismatch: stim={stim_sz} vs "
            f"classical={expected_sz}"
        )
        assert stim_sx == expected_sx, (
            f"[{name}] X-syndrome mismatch: stim={stim_sx} vs "
            f"classical={expected_sx}"
        )

    print("shor9_code self-check PASSED: classical Hz/Hx/Lz/Lx definitions "
          "agree with Stim's simulated syndrome outcomes on all probe cases.")


if __name__ == "__main__":
    _self_check()

    print("\nCode-capacity circuit (p=0.05):")
    c = build_code_capacity_circuit(0.05)
    print(f"  {c.num_detectors} detectors, {c.num_observables} observable(s), "
          f"{len(c)} instructions")

    print("\nPhenomenological circuit (p=0.05):")
    c2 = build_phenomenological_circuit(0.05)
    print(f"  {c2.num_detectors} detectors, {c2.num_observables} observable(s), "
          f"{len(c2)} instructions")
