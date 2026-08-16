# ConiQ-QEC
reference paper link: https://arxiv.org/abs/2508.05779
 # timeline
 Mon Aug 17
+ Hyunmin: Read ConiQ §II-B (QEC basics,  code, Table I logical operators) and §V (AHA scheme) closely. Write out by hand: the  code’s stabilizers, its 4 logical operators, and the automorphism-based SWAP/CNOT from Fig. 6a-b. This is your ground truth for correctness checks later.
+ Chloe: Read ConiQ §II-A (physical instruction set) and §VI-A (VAIR definition) closely. Start the physical-layer simulator: a Python class representing the state tuple (I, J, A, S) from §II-A, with Trans_a_to_s, Trans_s_to_a, Mov, 1Qgate, ParallelCZ as methods, enforcing the order-preserving and row-column constraints.
+ Aahna: Pull 2-3 magic-state distillation protocols (15-to-1, small-angle) with concrete input-copy counts and output-infidelity formulas. Set up the repo skeleton (folders: physical/, gadgets/, vair/, simulator/, benchmarks/) so everyone commits into a shared structure from day one.

Tue Aug 18
+ Aahna: Write out the  state-preparation gadget (Fig. 4 is level-2; derive the level-1/level-0 base case yourself since that’s your literal starting point) as an instruction sequence using Chloe’s physical instruction set.
+ Chloe: Implement PhysicalArray unit tests: verify order-preserving and row-column constraint enforcement actually raises errors on illegal moves. Start the D4Code class: stabilizers, logical operator table (from Table I), encode/decode helper methods.
+ Hyunmin: Draft the Toffoli-gate benchmark circuit by hand in a simple circuit IR (list of (gate, qubits) tuples is enough for now — don’t over-engineer this yet).

Wed Aug 19 — Mentor meeting #1
Bring: the from-scratch plan itself (confirm this is a sane scope given the deadline), Aahna’s hand-derived  gadget sequence, Chloe’s physical-layer skeleton. Ask directly: is single-level  + magic states a defensible MVP for a poster/lightning-talk abstract, or does the mentor think you need at least one concatenation level to make a compelling claim? Get this settled before you lock in scope.

Thu Aug 20
+ Aahna: Incorporate mentor feedback on scope. Finalize the  state-prep gadget instruction sequence; write the transversal CNOT and transversal H as instruction sequences too (these are simple — transversal means “apply the physical gate to every corresponding physical qubit pair,” per §II-B).
+ Chloe: Implement state_prep_D4() in code, using Aahna’s derivation, running on top of PhysicalArray. Get a single  logical qubit prepared and verified (check stabilizers measure +1) as your first working milestone.
+ Hyunmin: Add the adder circuit (3-bit ripple carry) and a small QFT circuit to the benchmark set, same simple IR as Toffoli.
