# Team Unicorn Fourier Gait Lab 0.5 — n=2..1,000,000

## Source and validity

This extends the *unchanged* 0.4 Python Gait Lab to all integer destinations from 2 to 1,000,000. Source code is available in `unicorn_scale_full.py` (root path is `/mnt/data`). It does NOT infer a physics model or a nontrivial prime rule. Leg count k=1..3, f=1..6 Hz, phase quarter-turns, 2,924 candidate multiset gaits.

Velocity v(t)=10*sum_i max(0,sin(2*pi*f_i*t+phase_i))/(sqrt(k)*(1+0.30*sum_{i<j}a_i*a_j)).
Birth cost 0.43*k^2+0.028*sum_i(f_i^2), travel multiplier [1+0.055*k*(k-1)], +1 fixed cost 0.35. Outbound n-1, return n. Sine wave sampled with 720 trapezoidal subdivisions per 1-second period, and cumulative distance numerically inverted with linear interpolation.

## Performance and exact search

Naive 999,999*2,924 brute-force combinations ≈2.924 billion. All 2,924 candidate 1-second wave curves are still constructed and compared, but asymptotic time bounds prune options that cannot beat the fastest-asymptotic reference at sufficiently large n. `|time_to_travel(d) - d/advance_per_sec| <= 1 second`, so a certified lower bound on candidate time compared with a certified upper bound on the reference rules out candidates without approximation in the *discrete waveform model*. About 3.62M candidate-target evaluations remain. 409 targets were independently cross-checked by exhaustive 2,924-design search, including all 99 original targets from v0.4. The UI stores exact winner IDs bit-packed, and recomputes chosen gait details locally on selection.

## Findings (baseline cost weights only)

- 999,999 destinations, 78,498 primes in range, 2,924 candidate gait designs.
- Only six distinct winner designs across 1M targets.
- k=1 selected in 12 cases and k=2 selected in 999,987; k=3 never selected.
- n>=40 winner always one of two 1Hz opposite-phase k=2 designs (0°/180° or 90°/270°).
- Overall mission time falls 21.51% against the per-destination optimized k=1 baseline.
- Total mission time for an imagined serial 2..1M relay is ≈246,583,683,620 **model seconds**, 7,813.8 model years on a 365.25-day conversion. Since time weights and worldline geometry are invented, this number has no empirical physical interpretation. It does illustrate inherent serial origin-roundtrip cost.
- Prime destination status is a *separate property* computed by sieve and plays no role in the gait optimizer. No prime-specific gait emerged. Repeating a fixed 1-second gait and giving the HQ destination does not force a useful prime law.
- Sensitivity: with no/low coordination coefficient γ=0/0.012, fastest long-distance design has 3 legs; at γ=.055/.13 it has 2; at γ=.25 it has 1. Thus optimum leg count is NOT universal.

## Output files

- `Team_Unicorn_Fourier_Gait_Lab_0.5_1M.html` — self-contained offline interactive browser (packed winner catalogue), destination 2..1,000,000.
- `Team_Unicorn_Fourier_2-100000.csv` — 99,999 rows of all winners to 100K.
- `Team_Unicorn_Fourier_2-1000000.csv.gz` — full million-range 999,999 rows of winners and time scores.
- `summary.json`, `bins_10000.csv`, `winning_runs.json` — summary and detailed metadata.
- `unicorn_scale_full.py` — exact scaled solver with search pruning proof and validation.

## Next scientific test

Go beyond the current assumed rectified sinusoidal thrust law. Make gait dynamics adaptive to destination, costs and phases; vary models, compare prime-labelled vs composite-labelled or label-shuffled legs, and perform held-out tests for any proposed prime-specific signature. More scale alone cannot identify a missing mechanism.
