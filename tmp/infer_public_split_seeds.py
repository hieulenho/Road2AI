from __future__ import annotations

import argparse
import json
import random
from collections import Counter

import numpy as np


N = 1012
HALF = 506

# Membership constraints inferred from score deltas and source-backed changes.
REQUIRED_PUBLIC = {755, 821, 659, 169}
LIKELY_PRIVATE = {50, 59, 95, 298, 671, 787}
XOR_PAIRS = [(67, 115), (587, 639), (660, 714)]
CORE18 = {
    16, 35, 89, 111, 135, 166, 182, 194, 221,
    473, 490, 568, 582, 616, 635, 641, 701, 923,
}


def valid(mask: set[int], strict_private: bool) -> bool:
    if not REQUIRED_PUBLIC <= mask:
        return False
    if strict_private and LIKELY_PRIVATE & mask:
        return False
    if any(((a in mask) + (b in mask)) != 1 for a, b in XOR_PAIRS):
        return False
    if sum(q in mask for q in CORE18) != 8:
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-seed", type=int, default=200_000)
    ap.add_argument("--strict-private", action="store_true")
    ap.add_argument("--method", choices=["numpy", "python"], default="numpy")
    ap.add_argument("--candidates", type=int, nargs="*", default=[])
    args = ap.parse_args()

    matches: list[dict[str, object]] = []
    counts = Counter()
    universe = list(range(1, N + 1))
    for seed in range(args.max_seed):
        if args.method == "numpy":
            order = np.random.RandomState(seed).permutation(N) + 1
            halves = (set(order[:HALF].tolist()), set(order[HALF:].tolist()))
        else:
            order = universe.copy()
            random.Random(seed).shuffle(order)
            halves = (set(order[:HALF]), set(order[HALF:]))
        for side, mask in enumerate(halves):
            if not valid(mask, args.strict_private):
                continue
            row = {"seed": seed, "side": side}
            if args.candidates:
                row["candidate_public"] = [q for q in args.candidates if q in mask]
                for q in args.candidates:
                    counts[q] += int(q in mask)
            matches.append(row)
    print(json.dumps({
        "method": args.method,
        "max_seed": args.max_seed,
        "strict_private": args.strict_private,
        "matches": matches[:200],
        "match_count": len(matches),
        "candidate_public_frequency": {
            str(q): counts[q] / len(matches) if matches else None
            for q in args.candidates
        },
    }, indent=2))


if __name__ == "__main__":
    main()
