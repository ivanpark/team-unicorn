# Entropy and Information Management Research Protocol (v0.7.1)
**2026-10-13 · Team Unicorn — Concept Engineering and Number-Universe Testbed**

## Question
Does engineering efficiency primarily mean speed and minimal leg count, or does it also require **optimising what is known, represented, stored, revised, transmitted and irreversibly discarded** while extending a verified mathematical scaffold?

## Four quantities that must not be conflated
1. **Spatial-layout information entropy** `H_U = -Σ_X P(X) log₂ P(X)`: meaningful only after specifying an ensemble/probability law over valid 3D arrangements X of a fixed integer prefix. The set of integers has no inherent Shannon entropy.
2. **HQ design uncertainty** `H_HQ = -Σ_g P(g | E_t) log₂ P(g | E_t)`: uncertainty over gait designs g conditioned on inherited evidence E_t. A sharply concentrated but incorrect belief is not inherently optimal.
3. **Encoding length and computational complexity:** bits stored for proof/certification, retained HQ state, code/description length, verification and recomputation time. Do not identify Shannon entropy with algorithmic description length.
4. **Thermodynamic entropy production** `Σ_phys`: requires an explicit physical device, temperature, energy accounting and environment. Toy-model gait time does not measure this quantity.

## Information-flow ledger
`HQ(t) → U(t) → prefix-check → +1 marker → return/handover → HQ(t+1)`

At each transition track input information, newly observed facts, preserved/reused proof, compression, logical erasure, failed checks and elapsed time.

## Candidate objective
Subject to *identical* correctness and completion constraints compare `J = w_T T + w_C C_coord + w_B B_birth + w_R R_relayout + w_V V_verify + w_M M_memory + w_E E_erase`. Publish weight normalisations; absent real hardware `E_erase` can only be a **proxy** such as the count of logical erasures.

**Landauer's principle:** at reservoir temperature `Θ`, the ideal thermodynamic lower bound associated with erasing one bit of information is `k_B Θ ln 2`. This does not mean the current software unicorns dissipate a measured amount of heat or that all their logical updates pay that bound exactly.

## Proposed controlled experiments
- S1: **Full-prefix recomputation versus inherited/cached proof certificates**, with identical arithmetic integrity guarantees. Compare runtime, certificate size and validation overhead.
- S2: **HQ memory policies**: full archive, compressed sufficient summaries and bounded caches. Test error rates, memory footprint and task completion time.
- S3: **Reorganisation**: no relayout, global relayout and local relayout. Track communication, movement and maintenance costs.
- S4: **Coordination topology**: independent legs, all-pairs synchronisation and neighbourhood control. Measure feedback messages and cost separately from propulsion.
- S5: **Leg-label controls**: genuine prime labels, composite labels and shuffled labels under identical constraints, with held-out results.

## Interpretation limits
- A successor +1 marker does not literally create real numbers; completion/interpolation requires its own representation axioms.
- Unique prime factorisation alone does not guarantee compression, reduced storage or lower entropy.
- Lower local structural uncertainty is not a violation or reduction of total thermodynamic entropy.
- Report sensitivity to arbitrary weights; do not tune the entropy penalty to predetermine the preferred outcome.
- A toy-world engineering analogy is **not direct evidence about human cognition, conceptual genesis or metaphysical reality**.

## Priority next prototype
The present Feedback Gait Lab 0.6.1 tracks coordination/feedback penalties, **not measured entropy**. First implement a genuine inherited-prefix checksum and HQ memory ledger, then integrate with gait, 3D embedding and feedback.
