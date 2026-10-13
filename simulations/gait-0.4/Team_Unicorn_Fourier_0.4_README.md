# Team Unicorn Fourier Gait Lab 0.4 — first probe

This is an exploratory **toy** model, not a proof of a number-theoretic or physical principle.

## Files

- `Team_Unicorn_Fourier_Gait_Lab_0.4.html` — standalone browser experiment; select a destination 2..100 to inspect the selected Fourier gait and a separate Fourier divisibility filter.
- `team_unicorn_fourier_probe.py` — simulation code (Python 3 + NumPy) that regenerates the CSV and JSON data.
- `Team_Unicorn_Fourier_probe_results.csv` — winning gait architecture at each destination (99 total).
- `Team_Unicorn_Fourier_probe.json` — full selected gait results, assumptions and divisibility hits for q <= sqrt(n).
- `fourier_sensitivity/test_params.py` — sensitivity testing variant with BIRTH_K and COORD_K environment variables.

## Experiment 1 — wave gait, **no stride=p assignment**

- Candidate leg frequencies f in {1, 2, 3, 4, 5, 6} (ordinary numeric frequencies, not prime leg labels).
- Candidate phase offsets phi in {0, pi/2, pi, 3pi/2}, leg counts k in {1, 2, 3}.
- Repetition allowed, yielding 2924 possible leg designs.
- Each leg's positive-contact activation is a_i(t)=max(0,sin(2*pi*f_i*t+phi_i)).
- A bounded effort normalization and overlapping-contact penalty create the *assumed* forward speed:

  v(t)=10*[sum_i a_i(t)]/[sqrt(k)*(1+0.30*sum_{i<j}a_i(t)*a_j(t))].

- Time horizon is continuous. Because all frequencies are integers, this velocity is 1-second periodic; we numerically integrate on a 720-point grid per second and invert cumulative travel distance for outbound distance n-1 and return distance n.
- Cost = birth 0.43*k^2 + 0.028*sum_i f_i^2 + (T_out+T_return)*(1+0.055*k*(k-1)) + 0.35 for the obligatory final +1 step.
- The positive-part operation models hypothetical contact/rectification; it does NOT follow automatically from Fourier superposition, and in general v_wave=lambda*f is wave phase speed rather than a body's translation speed.
- No leg's prime number determines its stride, because there **are no prime labels in this wave-gait mechanism**; assigning prime labels later without changing v(t) cannot generate prime-specific motion.

**Results in this fixed parameter set:** 99 targets, optimized k=1 in 12 cases, k=2 in 87, k=3 in 0; frequencies selected across 186 active legs: 1 Hz 179 times, 2 Hz 7 times. The prevalence of f=1 is a model-specific outcome, not a prime signature. Example selected 2-leg gait with f1=f2=1 Hz and phases pi apart advances about 4.502 units per second versus single-leg 3.183 units per second (different model-normalised effort and birth costs must be included for fair net comparison).

**Sensitivity:** when BIRTH_K=0.08 and COORD_K=0.012, k=1 in 2 cases, k=2 in 7, k=3 in 90; when BIRTH_K=1.1 and COORD_K=0.13, k=1 in 56 and k=2 in 43. This supports conditional gait-optimisation but no universal prime law.

## Experiment 2 — exact Fourier divisibility

The roots-of-unity character identity is

  delta_q(n) = (1/q)*sum_{r=0}^{q-1} exp(2*pi*i*r*n/q)

and equals 1 if q|n and 0 otherwise. Therefore n>=2 is prime iff no q in 2..floor(sqrt(n)) has delta_q(n)=1. This exactly recovers all primality labels for n=2..100 using character sums over *all* potential divisors q (no pre-enumerated prime list).

**Crucial limitation:** this is the divisibility test written in Fourier/phase notation, not an efficient novelty; finding this exact identity is not evidence that the wave-gait process spontaneously creates the prime distribution. To get a genuine discovery, a single generative dynamical law must specify how gait phases couple to arithmetic structure without inserting the divisibility test by hand, and it must outperform a held-out baseline / null control.

## Reproduce

```
python3 team_unicorn_fourier_probe.py
```

This writes results to `/mnt/data` in the current source file; adjust `root` for other environments.

The interactive HTML was visually checked with Chromium via Playwright set_content; destination changes and division labels worked without JavaScript exceptions.
