# Team Unicorn · Destination-Aware Gait Lab v0.3

Experimental, deterministic and strictly hypothetical. Not physical locomotion or a novel prime theorem.

## Run
Open `index.html` locally in a modern browser. No server or network required. Results for all 99 target destinations are embedded.
For raw full results, open `results.json` or `results.csv`. To reproduce: `python3 simulate.py`. To rebuild HTML after changing simulation: `python3 build_ui.py`.

## Exact design question
For Unicorn n with **known** destination n (2≤n≤100): HQ chooses a prime-labelled multiset of legs (count k is arbitrary in 1..4), sends the unicorn from origin to prior rock n−1, permits a final +1 move to place rock n, and optionally accounts for travel home. 1D stones are outputs, 3D limb mechanics not yet specified. Negative integers are deferred.

## Hypothetical mechanics and limits
- Only prime-labelled legs 2,3,5,7,11,13; duplicates permitted.
- 209 candidate architectures from combinations with replacement at k=1..4.
- On one pulse a **subset** of legs fires; their numerical prime labels sum to distance moved: Δx=Σp. This is *an assumption*, not a discovered mapping of primes to physical stride.
- Pulses are executed sequentially. No real Fourier phase optimisation, spring dynamics, physical torques or wave propagation.
- Pulse time τ=max(0.10+0.045√p_i) + γ(r−1)^2 + 0.015(k−r) + 0.015(k−1) seconds. r is active leg count, k installed leg count. Gamma alternatives are 0.06/0.14/0.24. Each pulse, λ_eff=Σp_i and f_eff=1/τ so its ideal average speed resembles λf.
- A slow **fine +1** action is allowed *during* the trip at 0.62 + 0.015(k−1) s, separate from the mandatory **final +1** from n−1 to n at 0.35 s. Fine adjustment guarantees reachability including n=2. A physical model must motivate this action. Without it some one-legged architectures could not exactly reach an odd target.
- HQ birth cost = 0.07 Σ√p_i + 0.10 k² seconds. This cost (like every coefficient) is hypothetical and tunable by editing simulate.py.
- Optional return is a symmetric traversal covering length n, at the same optimised pulse costs. It is a stand-in for information transfer, not a model of actual retrograde limb dynamics.
- Optimise `birth + min_time(n−1) + final +1 + min_time(n)` for full relay; outbound mode drops return.
- `min_time(d)` is calculated exactly by shortest-path dynamic programming over integer positions x=0..d with positive actions. Both design catalog enumeration and the route reconstruction are exhaustive and verified.
- For an **inherited** catalog, Unicorn n may only construct legs from known prime labels p≤n−1, with one explicit bootstrap seed p=2 at n=2. This is not generative prime discovery: known primes are hard-coded in candidate pool.
- For **preloaded**, all six primes are available from the first unicorn (mathematical preexistence vs physical adoption); differences expose anticipatory information.
- The fixed-architecture baseline uses the best single architecture over all n under the preloaded catalog; the fairer baseline for the inherited case is the best one-leg design eligible for each known destination.

## Interpretation
All results are conditional on chosen rules and cost coefficients. No evidence yet that a prime-labelled leg literally has p units of stride; no evidence that new primes are physically generated; no actual optimisation over gait Fourier phases or 3D spherical versus cubic worlds. The test is useful for isolating feasibility, causality and cost tradeoffs. The fact that choices differ for prime versus composite destination integers is not itself a new number-theoretic discovery.

## Checks
`simulate.py` verifies every selected outbound and return path hits the target exactly, and for each case checks the selected design score against all allowed 209 catalog configurations. Three coordination regimes × two catalog modes × two objectives × 99 destinations = 1,188 exhaustive optima checked. (Counts for candidate designs permitted are smaller in inherited mode for small n.)
