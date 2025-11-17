#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

# Make sure we can import red_scare when run from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ""))

import red_scare  # type: ignore


def main() -> None:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    files = sorted(
        f for f in os.listdir(data_dir)
        if f.endswith(".txt") and f != "README.md"
    )

    # Header: instance name, n, A, F, M, N, S
    print("instance_name\tn\tA\tF\tM\tN\tS")

    for fname in files:
        path = os.path.join(data_dir, fname)
        try:
            G = red_scare.parse_graph(path)
            none_val, some_val, many_val, few_val, alt_val = red_scare.solve_all(G)

            # Map results to the table format
            A = "true" if alt_val else "false"
            F = str(few_val)
            # Many: NP-hard in general; we only solve DAGs with no undirected edges.
            # If our algorithm declines (returns None), mark as '?!' (hard).
            if many_val is None:
                M = "?!"
            else:
                M = str(many_val)
            N = str(none_val)
            S = "true" if some_val else "false"

            print(f"{fname}\t{G.n}\t{A}\t{F}\t{M}\t{N}\t{S}")
        except Exception as e:
            # If something completely breaks, mark whole row with '?'.
            print(f"{fname}\t?\t?\t?\t?\t?\t?")
            print(f"# ERROR on {fname}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
