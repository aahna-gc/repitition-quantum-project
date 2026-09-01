"""
See day3_majority_vote_notes.md for the literature discussion. This script
makes the "information loss" idea from those notes concrete with a small,
self-contained numerical example. It is deliberately a TOY illustration --
the real 3-qubit-block x 3-qubit-block Shor code circuit, and the real
ML/hard-decision decoder implementations, land in later phases (Chloe's
circuit + Aahna's ML decoder + the harness this project builds toward).

The point demonstrated here:

    Hard-decision majority vote replaces a 3-bit vote tally (e.g. "2 votes
    for 0, 1 vote for 1") with a single bit ("block value = 0"). That bit
    throws away *how close* the vote was -- i.e., how confident we should
    be. When those hard bits are combined at the next level up (another
    majority vote across 3 blocks), a low-confidence block's hard bit
    counts exactly as much as a high-confidence block's hard bit. An
    optimal decoder would instead weight each block's contribution by its
    actual reliability (a likelihood), not treat every hard bit the same.
"""

import itertools
from typing import List, Tuple

import numpy as np


def majority_vote(bits: List[int]) -> int:
    """Hard-decision rule: return the bit value held by >= 2 of 3 votes."""
    return 1 if sum(bits) >= 2 else 0


def block_confidence(bits: List[int], p: float) -> float:
    """P(this block's majority-vote output is the TRUE value), given iid
    bit-flip probability p per qubit and 3 qubits per block. This is the
    'soft' information a hard-decision decoder discards."""
    n_flipped = sum(bits)
    # Confidence depends only on how many of the 3 bits agree with the
    # majority, not on which specific bits flipped.
    n_agreeing = 3 - n_flipped if n_flipped >= 2 else n_flipped
    n_agreeing = max(n_agreeing, 3 - n_agreeing)  # bits agreeing with majority
    # P(true value == majority | this many agree), assuming true value 0 and
    # iid flip probability p per qubit (symmetric in true value by symmetry).
    # This is just Bayes' rule over the two hypotheses "true=0" vs "true=1".
    from math import comb

    def likelihood(true_is_zero: bool) -> float:
        # probability of observing exactly this bit pattern given the
        # hypothesis, summed only through n_flipped (order doesn't matter
        # for the vote, but let's be exact and use the actual pattern).
        flips_from_hypothesis = sum(
            (b == 1) if true_is_zero else (b == 0) for b in bits
        )
        return (p ** flips_from_hypothesis) * ((1 - p) ** (3 - flips_from_hypothesis))

    l0 = likelihood(True)
    l1 = likelihood(False)
    return max(l0, l1) / (l0 + l1)


def demo_two_blocks_same_hard_output_different_confidence(p: float = 0.15) -> None:
    print("=" * 70)
    print("Two blocks with the SAME hard-vote output but different confidence")
    print("=" * 70)

    # Block A: a clean 3-0 vote (all three qubits agree).
    block_a = [0, 0, 0]
    # Block B: a narrow 2-1 vote (majority barely wins).
    block_b = [0, 0, 1]

    vote_a = majority_vote(block_a)
    vote_b = majority_vote(block_b)
    conf_a = block_confidence(block_a, p)
    conf_b = block_confidence(block_b, p)

    print(f"Block A raw bits: {block_a} -> hard-decision output: {vote_a}, "
          f"true confidence: {conf_a:.4f}")
    print(f"Block B raw bits: {block_b} -> hard-decision output: {vote_b}, "
          f"true confidence: {conf_b:.4f}")
    print(
        "\nBoth blocks report the SAME hard bit (0) to the next level, but "
        f"block A is right with probability {conf_a:.4f} while block B is "
        f"only right with probability {conf_b:.4f}. A hard-decision "
        "second-level majority vote cannot see this difference -- it just "
        "sees two '0' votes. An ML decoder, working from the original "
        "9 raw bits, keeps this distinction and weighs the blocks "
        "accordingly."
    )


def demo_second_level_disagreement_costs_more_than_it_should(p: float = 0.15) -> None:
    print("\n" + "=" * 70)
    print("Concrete failure case: hard-decision outvotes a very confident block")
    print("=" * 70)

    # Three blocks feeding the second-level vote.
    block_1 = [0, 0, 0]  # very confident 0 (3-0)
    block_2 = [1, 1, 0]  # confident 1 (2-1)
    block_3 = [1, 1, 0]  # confident 1 (2-1)

    hard_votes = [majority_vote(b) for b in (block_1, block_2, block_3)]
    confidences = [block_confidence(b, p) for b in (block_1, block_2, block_3)]
    final_hard_decision = majority_vote(hard_votes)

    print(f"Block hard votes: {hard_votes} -> level-2 majority vote result: "
          f"{final_hard_decision}")
    print(f"Block confidences (P[hard vote is correct]): "
          f"{[round(c, 4) for c in confidences]}")

    # A likelihood-respecting combination: multiply per-block likelihood
    # ratios instead of just counting hard votes (this is the spirit of
    # what an ML/soft decoder does -- full derivation lives in Aahna's
    # ML decoder work).
    def log_likelihood_ratio(bits: List[int], p: float) -> float:
        n_ones = sum(bits)
        # LLR in favor of "true = 1" vs "true = 0" for this block's 3 raw bits
        # (positive => evidence for 1, negative => evidence for 0).
        ll1 = n_ones * np.log(1 - p) + (3 - n_ones) * np.log(p)
        ll0 = n_ones * np.log(p) + (3 - n_ones) * np.log(1 - p)
        return ll1 - ll0

    total_llr = sum(
        log_likelihood_ratio(b, p) for b in (block_1, block_2, block_3)
    )
    soft_decision = 1 if total_llr > 0 else 0

    print(f"Sum of block log-likelihood-ratios: {total_llr:.4f} -> "
          f"soft/likelihood-based decision: {soft_decision}")
    print(
        "\nHard-decision level-2 majority vote sees two '1' hard votes "
        "(blocks 2 and 3) against one '0' (block 1) and outputs 1 -- even "
        "though block 1's vote was much more confident (3-0) than blocks "
        "2/3's narrow 2-1 votes. The likelihood-based combination correctly "
        "weighs that confidence difference. This is exactly the mechanism "
        "the project's decoder-comparison experiment measures at scale."
    )


def main() -> None:
    demo_two_blocks_same_hard_output_different_confidence()
    demo_second_level_disagreement_costs_more_than_it_should()


if __name__ == "__main__":
    main()
