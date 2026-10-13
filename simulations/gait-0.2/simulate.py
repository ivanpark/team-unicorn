#!/usr/bin/env python3
"""Unicorn Gait Lab 0.2: exact-arithmetic, event-driven toy model.

This is an arithmetic/scheduling experiment, NOT a locomotion model.
A leg label does not determine its stride or cadence. All strides are editable.
Scheduled requests continue at their intended cadence even if a controller lags.
Each completed request contributes +stride; no continuous partial stroke is counted.

Defaults reproduce the conversation's illustrative strides and cadences:
(5, 7), (2, 1), (3, 1), (7, 1), (11, 1), (13, 1).
Prime strides here are example inputs, not an emergent result.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Leg:
    stride: int
    frequency: F
    phase: F = F(1)
    # phase in (0, 1]: first request at phase/frequency, no request at t=0.

    def __post_init__(self) -> None:
        if self.stride < 1 or self.frequency <= 0 or not (0 < self.phase <= 1):
            raise ValueError('Require stride >= 1, frequency > 0, 0 < phase <= 1.')


def prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def factorise(n: int) -> list[list[int]]:
    if n < 1:
        return []
    out = []
    d = 2
    while d*d <= n:
        power = 0
        while n % d == 0:
            power += 1
            n //= d
        if power:
            out.append([d, power])
        d = 3 if d == 2 else d+2
    if n > 1:
        out.append([n, 1])
    return out


def make_legs(k: int, phase_mode: str = 'staggered') -> list[Leg]:
    if not 1 <= k <= 6:
        raise ValueError('Default comparison supports 1..6 legs.')
    ds = (5, 2, 3, 7, 11, 13)
    fs = (7, 1, 1, 1, 1, 1)
    legs = []
    for i in range(k):
        phase = F(1) if i == 0 or phase_mode == 'aligned' else F(i, k)
        legs.append(Leg(ds[i], F(fs[i]), phase))
    return legs


def schedule(legs: list[Leg], horizon: F, per_other_leg: F = F(0),
             controller: str = 'shared') -> list[dict]:
    if horizon <= 0 or per_other_leg < 0 or controller not in ('shared', 'independent'):
        raise ValueError('Invalid horizon, coordination cost or controller.')
    events = []
    for i, leg in enumerate(legs):
        j = 0
        while True:
            release = (F(j) + leg.phase) / leg.frequency
            if release > horizon:
                break
            events.append((release, i, j+1, leg.stride))
            j += 1
            if len(events) > 1_000_000:
                raise ValueError('Simulation event limit exceeded.')
    events.sort()  # ties: leg index, then within-leg request number
    service = per_other_leg * (len(legs)-1)
    free = [F(0)] * (1 if controller == 'shared' else len(legs))
    out = []
    for release, i, j, stride in events:
        lane = 0 if controller == 'shared' else i
        start = max(release, free[lane])
        finish = start + service
        free[lane] = finish
        out.append(dict(leg=i+1, request=j, release=release,
                        start=start, finish=finish, wait=start-release,
                        service=service, stride=stride))
    return out


def snapshot(legs: list[Leg], events: list[dict], T: F,
             cost: F, controller: str) -> dict:
    released = [e for e in events if e['release'] <= T]
    done = [e for e in released if e['finish'] <= T]
    D = sum(e['stride'] for e in done)
    previous = sum(e['stride'] for e in done if e['finish'] <= max(F(0), T-F(1)))
    h = cost*(len(legs)-1)
    rho = h*sum((leg.frequency for leg in legs), F(0))
    independent_load = max((h*leg.frequency for leg in legs), default=F(0))
    return dict(time_seconds=float(T), distance=D, distance_is_prime=prime(D),
                factorisation=factorise(D), mean_speed=float(F(D)/T),
                last_second_distance=D-previous,
                requested=len(released), completed=len(done), pending=len(released)-len(done),
                ideal_distance=sum(e['stride'] for e in released),
                completed_wait_seconds=float(sum((e['wait'] for e in done), F(0))),
                controller_utilisation=float(rho if controller == 'shared' else independent_load),
                moves_by_leg=[sum(e['leg'] == i+1 for e in done) for i in range(len(legs))])


def run(k: int, cost: F, phase_mode: str = 'staggered',
        controller: str = 'shared', horizons: Iterable[int] = (1, 5, 10)) -> dict:
    ts = tuple(F(x) for x in horizons)
    legs = make_legs(k, phase_mode)
    events = schedule(legs, max(ts), cost, controller)
    return dict(leg_count=k, coordination_seconds_per_other_leg=str(cost),
                phase_mode=phase_mode, controller=controller,
                legs=[dict(stride=l.stride, frequency=str(l.frequency), phase=str(l.phase)) for l in legs],
                snapshots=[snapshot(legs, events, T, cost, controller) for T in ts])


def test() -> None:
    for phase in ('aligned', 'staggered'):
        for k in range(1, 7):
            r = run(k, F(0), phase)
            base = (35, 37, 40, 47, 58, 71)[k-1]
            assert [s['distance'] for s in r['snapshots']] == [base, base*5, base*10]
            assert all(s['pending'] == 0 for s in r['snapshots'])
    assert [s['distance'] for s in run(4,F('0.03'))['snapshots']] == [42,230,465]
    assert [s['distance'] for s in run(6,F('0.03'))['snapshots']] == [20,185,375]
    assert [s['pending'] for s in run(6,F('0.03'))['snapshots']] == [7,28,55]
    # Each completed event must obey release/start/completion causality.
    for mode in ('shared', 'independent'):
        ev = schedule(make_legs(6),F(10),F('0.03'),mode)
        assert all(e['release'] <= e['start'] <= e['finish'] for e in ev)
    # No prime output > stride is possible for a fixed one-leg integer stride > 1.
    for stride in range(2, 15):
        for count in range(2, 30):
            assert not prime(stride*count)
    assert prime(37) and not prime(1) and factorise(350) == [[2,1],[5,2],[7,1]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('results.json'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    test()
    costs = tuple(F(x) for x in ('0','.01','.02','.03','.04','.05'))
    runs = [run(k,c,phase,controller)
            for controller in ('shared','independent')
            for phase in ('aligned','staggered')
            for c in costs for k in range(1,7)]
    payload = dict(model='Unicorn Gait Lab 0.2',date='2026-10-13',
                   description='Exact rational event simulation; arithmetic + queuing toy model; no empirical calibration.',
                   snapshot_count=sum(len(r['snapshots']) for r in runs),
                   run_count=len(runs),runs=runs)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'All checks passed. {len(runs)} runs; {payload["snapshot_count"]} snapshots -> {args.output}')


if __name__ == '__main__':
    main()
