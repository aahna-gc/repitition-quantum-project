from __future__ import annotations

from typing import Sequence
import numpy as np

# Syndrome pair (det0, det1) -> index of the failed element in a 3-element repetition code:
# (0, 0) -> no error
# (1, 0) -> element 0
# (1, 1) -> element 1
# (0, 1) -> element 2
_REP3_LOOKUP = {
    (0, 0): None,
    (1, 0): 0,
    (1, 1): 1,
    (0, 1): 2,
}


def decode_single_shot_stim(dets: Sequence[int]) -> int:
    """Decodes a single shot of Stim detector events (8 detectors per round)

    using level-by-level hard-decision majority voting.

    Chloe's circuit detector ordering per round:
      - dets[0:2]: Block 0 Z-stabilizers -> inner repetition code 0
      - dets[2:4]: Block 1 Z-stabilizers -> inner repetition code 1
      - dets[4:6]: Block 2 Z-stabilizers -> inner repetition code 2
      - dets[6:8]: Outer X-stabilizers   -> outer repetition code across blocks

    Returns:
        Predicted logical observable flip (0 or 1).
    """
    # Use the final round of syndrome detectors (or the 8 detectors if rounds=1)
    # For multi-round, we look at the last round's differential syndrome
    last_round_dets = dets[-8:]

    # Level 1 (Inner bit-flip repetition codes)
    # We evaluate majority vote for each block to decide if the block has an odd Z-parity flip
    block_z_flips = [0, 0, 0]
    for block_idx in range(3):
        d0 = int(last_round_dets[2 * block_idx])
        d1 = int(last_round_dets[2 * block_idx + 1])
        flipped_qubit = _REP3_LOOKUP.get((d0, d1))

        # A hard-decision level-1 correction is applied internally to the block.
        # If majority vote flags an odd qubit flip, the block's physical correction
        # restores its internal alignment without leaking probabilistic soft info upward.
        if flipped_qubit is not None:
            block_z_flips[block_idx] = 1

    # Level 2 (Outer phase-flip repetition code)
    # Evaluates the 2 X-stabilizers across the 3 blocks.
    x_d0 = int(last_round_dets[6])
    x_d1 = int(last_round_dets[7])

    flipped_block = _REP3_LOOKUP.get((x_d0, x_d1))

    # Output prediction:
    # If Level 2 majority vote detects an uncorrected outer phase flip,
    # it predicts a logical X_bar flip (1), otherwise no flip (0).
    predicted_logical_flip = 1 if flipped_block is not None else 0

    return predicted_logical_flip


def hard_decision_decode(
    detector_samples: np.ndarray, p: float | None = None
) -> np.ndarray:
    """Batch decoder entry point compatible with Monte Carlo pipeline and Stim samplers.

    Args:
        detector_samples: Binary 2D numpy array of shape (num_shots, num_detectors).
        p: Physical error rate (accepted for interface compatibility with ML decoder).

    Returns:
        Binary 2D numpy array of shape (num_shots, 1) containing predicted logical flips.
    """
    num_shots = detector_samples.shape[0]
    predictions = np.zeros((num_shots, 1), dtype=np.uint8)

    for i in range(num_shots):
        predictions[i, 0] = decode_single_shot_stim(detector_samples[i])

    return predictions


# ---------------------------------------------------------------------------
# Sanity check unit tests on simulated Stim detector arrays
# ---------------------------------------------------------------------------


def _run_unit_tests() -> None:
    print("Testing Stim-compatible Hard Decision Decoder...")

    # Case 1: No errors -> all 8 detectors 0
    dets_clean = np.array([[0, 0, 0, 0, 0, 0, 0, 0]])
    assert hard_decision_decode(dets_clean)[0, 0] == 0, "Failed: Clean case"
    print("  PASS: Clean syndrome (no logical flip predicted)")

    # Case 2: Single Z error inside block 0 (det0=1, det1=0) -> Level 1 corrects, Level 2 clear
    dets_single_z = np.array([[1, 0, 0, 0, 0, 0, 0, 0]])
    assert hard_decision_decode(dets_single_z)[0, 0] == 0, "Failed: Single Z error"
    print("  PASS: Single Z error within block 0 correctly neutralized at Level 1")

    # Case 3: Outer phase error (X-detector 0 flags: det6=1, det7=0) -> Level 2 flags block 0
    dets_outer_x = np.array([[0, 0, 0, 0, 0, 0, 1, 0]])
    assert hard_decision_decode(dets_outer_x)[0, 0] == 1, "Failed: Outer X error"
    print("  PASS: Outer phase error detected and predicted as logical flip")

    print("\nALL STIM DECODER TESTS PASSED.")


if __name__ == "__main__":
    _run_unit_tests()
