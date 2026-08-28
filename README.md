# repitition-quantum-project

# at a glance
**We measure, on the 9-qubit Shor code, exactly how much of concatenated codes' higher logical error rate comes from using a fast hard-decision decoder instead of the true (but exponentially costly) maximum-likelihood decoder.** 

Concatenated quantum error-correcting codes are conventionally decoded using fast, local hard-decision (majority-vote) rules applied level-by-level — a practical choice used throughout the concatenated-code literature, including recent high-rate constructions, precisely because exact maximum-likelihood (ML) decoding scales exponentially with qubit count. This practicality-driven choice comes at a known but rarely quantified cost: hard-decision decoding discards probabilistic information at each level that an optimal decoder would retain. We isolate and measure this decoder-induced gap directly on the canonical example of code concatenation: the 9-qubit Shor code, itself a phase-flip repetition code concatenated with a bit-flip repetition code. Using a code-capacity noise model, we compare three decoders: majority-vote decoding of a bare 3-qubit repetition code (a zero-gap control, since majority vote is provably optimal for a single repetition code), standard hard-decision level-by-level decoding of the full Shor code, and an exact brute-force ML decoder enumerating all possible error patterns. By holding the code and noise model fixed and varying only the decoder, we attribute the resulting difference in logical error rate entirely to decoder suboptimality rather than code structure — providing, on the most pedagogically standard concatenated code, a concrete answer to how much of concatenated codes' apparent disadvantage relative to more heavily-optimized decoders (e.g., surface-code matching) is a decoder limitation rather than an inherent property of concatenation itself.

# tentative timeline
checkmark for completion: ✓ \
timeline: \
**Phase 1: research** \
Tue, Aug 18
+ Aahna: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓
+ Chloe: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓
+ Hyunmin: Install Stim; work through the official Stim getting-started tutorial (circuits, detectors, observables) + install requirements.txt ✓

Sun, Aug 23:
+ Aahna: Read up on Maximum Likelihood decoding theory for stabilizer codes — logical cosets, partition functions, degenerate error classes. ✓ 
+ Chloe: Study the Shor [[9,1,3]] code in depth: stabilizer generators, encoding circuit, X/Z error correction structure. ✓
+ Hyunmin: Read Stim docs on phenomenological vs. circuit-level noise models; survey how Stim's built-in decoders (pymatching) work as a reference point. ✓

Mon, Aug 24:
+ Aahna: Sketch pseudocode for a brute-force ML decoder: enumerate all logical cosets, sum error probabilities exactly from the detector error model. ✓
+ Chloe: Prototype a minimal (unencoded) Stim circuit for the Shor code to get comfortable with circuit syntax before fault-tolerant version. ✓
+ Hyunmin: Investigate literature on local hard-decision majority-vote decoders for concatenated codes; note what “information loss” means at each layer. ✓

Tues, Aug 25:
+ Aahna: Begin ML decoder skeleton: pull detector error model out of a Stim circuit via circuit.detector_error_model(). (make sure to let others know what filenames correlate to what) ✓
+ Chloe: Build the fault-tolerant Shor code memory circuit under a phenomenological noise model in Stim. (make sure to let others know what filenames correlate to what) ✓
+ Hyunmin: Build benchmarking harness scaffolding: experiment config schema, result logging (CSV/JSON), directory conventions. (make sure to let others know what filenames correlate to what)

Wed, Aug 26:
+ Aahna: Implement exact enumeration over syndromes and logical coset classes for the ML decoder. ✓
+ Chloe: Extend the memory circuit to a circuit-level noise model (gate errors, measurement errors, idling errors). ✓
+ Hyunmin: Implement the local hard-decision majority-vote decoder baseline.

Thu, Aug 27:
**meeting: discuss submission to urtc, meetings with deutch and shantanu, update one another on project progress**
+ Aahna: Unit-test the ML decoder on small, hand-checkable syndrome cases; validate against known Shor code error patterns. Also: schedule emails to Deutsch and Shantanu
+ Chloe: Sanity-check circuit correctness: verify detector event statistics match expected error-free behavior. ✓
+ Hyunmin: Wire the majority-vote decoder into the pipeline; run first end-to-end baseline experiment.

Fri, Aug 28:
+ Aahna: Optimize the ML decoder for larger shot counts (vectorize the brute-force enumeration where possible).
+ Chloe: Implement physical error-rate (p) sweeps for the phenomenological noise model.
+ Hyunmin: Build Monte Carlo sampling + logical error rate computation infrastructure.

Sat, Aug 29:
+ Aahna: Extend the ML decoder to handle the circuit-level detector error model.
+ Chloe: Implement p sweeps for the circuit-level noise model; cross-check DEM against phenomenological limits.
+ Hyunmin: Run first logical error rate experiments (phenomenological noise, both decoders) as a smoke test.

Sun, Aug 30:
**meeting day**
+ Aahna: Run larger-scale ML decoding experiments (phenomenological); begin comparing logical failure rate coefficients vs. majority-vote. review Aahna's decoder module, Chloe's circuit module, and Hyunmin's pipeline module in the meeting. 
+ Chloe: Run larger-scale phenomenological experiments across the full p sweep for both decoders. review Aahna's decoder module, Chloe's circuit module, and Hyunmin's pipeline module in the meeting.
+ Hyunmin: Build pseudo-threshold estimation code (curve fitting, threshold crossing point). review Aahna's decoder module, Chloe's circuit module, and Hyunmin's pipeline module in the meeting.

Mon, Aug 31:
+ Aahna: Run larger-scale ML decoding experiments (circuit-level). Draft abstracts to submit to URTC.
+ Chloe: Run circuit-level experiments at scale for both decoders. Draft abstracts to submit to URTC.
+ Hyunmin: Apply pseudo-threshold analysis to both decoders; generate first preliminary comparison plots. Draft abstracts to submit to URTC.

Tue, Sept 1:
**meeting day**
+ All: discuss drafted abstracts during meeting and work on finalizing and editing them.
+ Aahna: Full experiment run (all): execute the complete phenomenological + circuit-level, ML + majority-vote experiment matrix; collect the dataset for the August milestone.
+ Chloe: Full experiment run (all): same — focus on verifying circuit-level data quality and re-running any noisy configurations.
+ Hyunmin: Full experiment run (all): same — aggregate results into the shared dataset; start drafting a results-summary memo.

Wed, Sept 2:
+ Aahna: Make final edits to abstracts. Check in w/ Chloe on submission status. Code freeze: Finalize decoder module, docstrings, and inline comments.
+ Chloe: Make final edits to abstracts. Submit to URTC portal. Code freeze: finalize circuit-construction module, docstrings, and inline comments.
+ Hyunmin: Make final edits to abstracts. Check in w/ Chloe on submission status. Code freeze: clean up repo, write README, package for open-source release, tag a v0.1 checkpoint.

**Phase 2: writing**
