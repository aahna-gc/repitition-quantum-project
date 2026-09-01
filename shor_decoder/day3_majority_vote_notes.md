# Literature notes: hard-decision majority-vote decoding of concatenated codes

**Owner:** Hyunmin
**Date:** Mon, Aug 24
**Duty:** *"Investigate literature on local hard-decision majority-vote decoders
for concatenated codes; note what 'information loss' means at each layer."*

These are working notes to ground the project's central question: how much
of a concatenated code's logical error rate is caused by the *decoder*
(hard-decision, level-by-level majority vote) rather than by the *code*
itself (the concatenation structure).

## 1. Background: why concatenated codes use hard-decision decoding at all

Concatenation was introduced alongside the threshold theorem (Knill,
Laflamme & Zurek, 1996; Aliferis, Gottesman & Preskill, 2006) as a way to
suppress errors doubly-exponentially in the number of nesting levels,
*provided* each level is decoded independently and quickly. The standard
recipe, used from Shor's original 9-qubit code (1995) through modern
high-rate concatenated constructions, is:

1. Decode the innermost level (e.g. a 3-qubit repetition block) using a
   simple rule — majority vote for bit/phase flips.
2. Treat the result as a clean, classical bit and pass it up to the next
   level.
3. Repeat.

This is attractive because each level's decoding problem stays small and
local (majority vote on 3 bits is O(1)), so the overall decoder scales
**linearly** in block count instead of exponentially in total qubit count.
That's precisely the practicality trade-off the project abstract calls out.

## 2. Where "information loss" actually happens

The key phrase in our project description is that hard-decision decoding
"discards probabilistic information at each level that an optimal decoder
would retain." Concretely, at each level:

- **What majority vote outputs:** a single hard bit — "this block's logical
  value is 0" or "is 1" — with no indication of *how confident* that call
  was.
- **What is discarded:** the actual syndrome pattern / vote count. A block
  that voted 2-to-1 and a block that voted 3-to-0 both get reported
  upward as the same hard bit, even though the 3-0 block is much more
  likely to be correct. An optimal (maximum-likelihood) decoder retains
  the *full probability* that each block's logical value is 0 vs. 1, and
  carries that likelihood into the next level's decision.
- **Why it matters at the next level up:** the second-level decoder (in
  our case, another majority vote, over the three first-level blocks) is
  itself only optimal if its three inputs are equally reliable. Once
  hard-decision decoding has thrown away confidence information, the
  second-level vote can be swayed by a low-confidence block exactly as
  much as by a high-confidence one — a strictly worse decision rule than
  one that weights inputs by their actual reliability.
- **Rahn, Doherty & Mabuchi (2002), "Exact performance of concatenated
  quantum codes"** derive exact recursive formulas for logical error rate
  under concatenation and note that these differ from the hard-decision,
  independent-level treatment.
- **Poulin (2006), "Optimal and efficient decoding of concatenated
  quantum block codes"** is the most directly relevant prior work: it
  explicitly formulates near-ML decoding for concatenated codes by
  passing *soft* (likelihood) information between levels rather than
  hard bits, and reports the resulting gain over naive hard-decision,
  level-by-level decoding — i.e., essentially the same gap our project
  measures, but for general concatenated block codes rather than the
  specific 9-qubit Shor code as a minimal/pedagogical case.

## 3. What this means for our experiment design

Our project isolates this effect on the smallest interesting example (the
9-qubit Shor code = one level of phase-flip repetition concatenated with
one level of bit-flip repetition) so the gap can be measured exactly via
brute-force enumeration, rather than approximated:

- **Control (zero gap by construction):** majority vote on a *bare* 3-qubit
  repetition code. Majority vote is provably optimal here — there's only
  one level, so there's no "information loss between levels" to speak of.
  We expect this to match the exact ML decoder's logical error rate.
- **Treatment A:** standard hard-decision, level-by-level decoding of the
  full 9-qubit Shor code (majority vote inside each 3-qubit block, then
  majority vote across the 3 block outcomes). This is where the literature
  above predicts a gap opens up.
- **Treatment B:** exact brute-force ML decoding of the full 9-qubit code,
  enumerating all 2^9 error patterns and picking the most likely logical
  coset directly from the code-capacity noise model. No level-by-level
  hard bits at all — this is the "keeps all the information" baseline.

The difference in logical error rate between Treatment A and Treatment B,
with Control confirming the comparison isn't contaminated by some other
effect, is exactly the "decoder-induced gap" the project abstract promises
to quantify.

## 4. Open questions / things to watch for when building the harness (Aug 25+)

- Need to fix a single code-capacity noise model (iid X and/or Z flips
  with probability `p` per qubit, perfect syndrome extraction) so all
  three decoders are compared on identical noise realizations.
- Need to decide how ties are broken in majority vote (e.g. 1-1-1 vote at
  the block level, which can't happen for 3-qubit blocks but can recur in
  edge cases) — should be documented once Chloe's circuit is finalized.
- Poulin's near-ML approach for general concatenated codes is a useful
  sanity check for our exact brute-force decoder's expected shape of
  improvement (monotonic in `p`, larger gap as `p` grows toward the
  code's threshold).

See `day3_majority_vote_demo.py` for a small, self-contained numerical
illustration of point 2 above (why a hard-vote output is strictly less
informative than the vote tally it came from).
