# Team Unicorn Feedback Gait Lab 0.6

First controlled experiment introducing local sensory feedback and frequency corrections without changing the 0.5 positive-part sine velocity law. Source of baseline: /mnt/data/unicorn_scale_full.py (previously uploaded Gait Lab 0.5)

Inputs: 1, 2 or 3 legs with uniform 1Hz frequency and equally spaced initial phases. Phase disturbances (unexpected) at 0.75, 3, 7 seconds; local phase control u_i = clip(-K sin(theta_i-theta_0-2*pi*i/k), +/-3 rad/s); the first leg is the fixed cadence reference. The controller affects angular velocity dynamically, with control effort E=int sum u_i**2 dt and an illustrative score x-alpha*E. Integration dt=0.0025s. This toy model does not yet take the destination error as feedback, fit prime-specific parameters, produce true physical locomotion, model 3D space, evolve HQ between generations, or include return and design costs. Any apparent benefit is contingent on synthetic disturbances and controllers.

The CSV contains k=1..3, horizons 1/5/10 seconds, gains 0/0.6/1.5/3.0. Interactive HTML adds adjustable gain, effort price and disturbance on/off. Run Python 3 (standard library only): python feedback_probe.py. The HTML is offline; open it directly in a browser.
