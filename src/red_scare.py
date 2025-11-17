
#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable, Optional
from collections import deque
import sys
import os


@dataclass
class Graph:
    n: int
    m: int
    r: int
    s: str
    t: str
    vertices: List[str]
    red: Set[str]
    adj: Dict[str, List[str]]      # adjacency: v -> neighbors (directed as given)
    radj: Dict[str, List[str]]     # reverse adjacency for directed edges
    has_undirected: bool           # True if any "--" edge appears


def parse_graph(path: str) -> Graph:
    with open(path, "r") as f:
        first = f.readline().split()
        if len(first) != 3:
            raise ValueError(f"Bad first line in {path!r}: {first}")
        n, m, r = map(int, first)

        line = f.readline().split()
        if len(line) != 2:
            raise ValueError(f"Bad s,t line in {path!r}: {line}")
        s, t = line[0], line[1]

        vertices: List[str] = []
        red: Set[str] = set()

        # read <vertices> block
        for _ in range(n):
            line = f.readline()
            if not line:
                raise ValueError(f"Unexpected EOF in vertex list in {path!r}")
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            v = parts[0]
            vertices.append(v)
            if len(parts) > 1 and parts[1] == "*":
                red.add(v)

        # init adjacency
        adj: Dict[str, List[str]] = {v: [] for v in vertices}
        radj: Dict[str, List[str]] = {v: [] for v in vertices}
        name_set = set(vertices)

        has_undirected = False

        # read <edges> block
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Bad edge line in {path!r}: {line}")
            u, arrow, v = parts
            if u not in name_set or v not in name_set:
                raise ValueError(f"Unknown vertex name in {path!r}: {u}, {v}")

            if arrow == "--":
                has_undirected = True
                adj[u].append(v)
                adj[v].append(u)
                radj[u].append(v)
                radj[v].append(u)
            elif arrow == "->":
                adj[u].append(v)
                radj[v].append(u)
            else:
                raise ValueError(f"Unknown edge type {arrow!r} in {path!r}")

    if len(vertices) != n:
        raise ValueError(f"{path!r}: expected {n} vertices, got {len(vertices)}")

    return Graph(
        n=n,
        m=m,
        r=r,
        s=s,
        t=t,
        vertices=vertices,
        red=red,
        adj=adj,
        radj=radj,
        has_undirected=has_undirected,
    )


# ---------- Problem: None ----------

def solve_none(G: Graph) -> int:
    """Return length of shortest s–t path internally avoiding red vertices.
       Return -1 if no such path exists.
    """
    blocked: Set[str] = set(G.red)
    # s and t are allowed even if red (only internal vertices are forbidden)
    blocked.discard(G.s)
    blocked.discard(G.t)

    if G.s not in G.adj or G.t not in G.adj:
        return -1

    dq = deque()
    dq.append((G.s, 0))
    visited: Set[str] = {G.s}

    while dq:
        v, dist = dq.popleft()
        if v == G.t:
            return dist
        for u in G.adj[v]:
            if u in blocked:
                continue
            if u not in visited:
                visited.add(u)
                dq.append((u, dist + 1))

    return -1


# ---------- Problem: Some ----------

def bfs_reachable(start: str, adj: Dict[str, List[str]]) -> Set[str]:
    seen: Set[str] = set()
    dq = deque([start])
    seen.add(start)
    while dq:
        v = dq.popleft()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                dq.append(u)
    return seen


def solve_some(G: Graph) -> bool:
    """Return True if there is an s–t path that includes at least one red vertex."""
    # Set of vertices reachable from s (forward)
    reachable_from_s = bfs_reachable(G.s, G.adj)
    # Set of vertices that can reach t (reverse graph)
    can_reach_t = bfs_reachable(G.t, G.radj)

    for v in G.red:
        if v in reachable_from_s and v in can_reach_t:
            return True
    return False


# ---------- Problem: Few ----------

def solve_few(G: Graph) -> int:
    """Return minimum number of red vertices on any s–t path, or -1 if none.
       Uses Dijkstra-style shortest path with vertex costs (non-negative).
    """
    import heapq

    INF = 10**18
    dist: Dict[str, int] = {v: INF for v in G.vertices}
    # cost includes red(s) if s is red
    dist[G.s] = 1 if G.s in G.red else 0

    heap: List[Tuple[int, str]] = [(dist[G.s], G.s)]

    while heap:
        d, v = heapq.heappop(heap)
        if d != dist[v]:
            continue
        if v == G.t:
            return d
        for u in G.adj[v]:
            add = 1 if u in G.red else 0
            nd = d + add
            if nd < dist[u]:
                dist[u] = nd
                heapq.heappush(heap, (nd, u))

    return -1


# ---------- Problem: Alternate ----------

def solve_alternate(G: Graph) -> bool:
    """Return True if there is a path from s to t that alternates red/non-red."""
    dq = deque([G.s])
    seen: Set[str] = {G.s}

    is_red = G.red.__contains__

    while dq:
        v = dq.popleft()
        if v == G.t:
            return True
        for u in G.adj[v]:
            # edge must connect red <-> non-red
            if is_red(v) == is_red(u):
                continue
            if u not in seen:
                seen.add(u)
                dq.append(u)

    return False


# ---------- Problem: Many (restricted class: directed acyclic graphs) ----------

def has_directed_cycle(G: Graph) -> bool:
    """Detect if the directed version of G has a cycle."""
    # we follow G.adj as given (directed edges + both directions for undirected)
    # For Many we will only trust graphs with no undirected edges at all.
    visited: Dict[str, int] = {v: 0 for v in G.vertices}  # 0=unseen,1=visiting,2=done

    def dfs(v: str) -> bool:
        visited[v] = 1
        for u in G.adj[v]:
            if visited[u] == 1:
                return True
            if visited[u] == 0 and dfs(u):
                return True
        visited[v] = 2
        return False

    for v in G.vertices:
        if visited[v] == 0 and dfs(v):
            return True
    return False


def topo_order(G: Graph) -> List[str]:
    """Topological order for directed acyclic graph (G.adj)."""
    indeg = {v: 0 for v in G.vertices}
    for v in G.vertices:
        for u in G.adj[v]:
            indeg[u] += 1

    dq = deque([v for v in G.vertices if indeg[v] == 0])
    order: List[str] = []
    while dq:
        v = dq.popleft()
        order.append(v)
        for u in G.adj[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                dq.append(u)
    if len(order) != len(G.vertices):
        raise ValueError("Graph is not acyclic")
    return order


def solve_many(G: Graph) -> Optional[int]:
    """Return maximum number of red vertices on an s–t path.
       On general graphs this is NP-hard. We implement it only for
       a well-defined class: directed acyclic graphs with no '--' edges.
       If G is outside this class, return None.
    """
    # Restrict to purely directed graphs (no "--")
    if G.has_undirected:
        return None

    # Require acyclicity
    if has_directed_cycle(G):
        return None

    # Now G is a DAG; we can do DP in topological order.
    order = topo_order(G)
    NEG_INF = -10**18
    dp: Dict[str, int] = {v: NEG_INF for v in G.vertices}
    dp[G.s] = 1 if G.s in G.red else 0

    for v in order:
        if dp[v] == NEG_INF:
            continue
        base = dp[v]
        for u in G.adj[v]:
            val = base + (1 if u in G.red else 0)
            if val > dp[u]:
                dp[u] = val

    if dp[G.t] == NEG_INF:
        return -1
    return dp[G.t]


# ---------- CLI ----------

def solve_all(G: Graph) -> Tuple[int, bool, Optional[int], int, bool]:
    """Run all five problems and return a tuple:
       (none, some, many, few, alternate)
    """
    none_val = solve_none(G)
    some_val = solve_some(G)
    many_val = solve_many(G)
    few_val = solve_few(G)
    alt_val = solve_alternate(G)
    return none_val, some_val, many_val, few_val, alt_val


def main(argv: List[str]) -> None:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <graph-file>", file=sys.stderr)
        sys.exit(1)

    path = argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    G = parse_graph(path)

    none_val, some_val, many_val, few_val, alt_val = solve_all(G)

    print(f"File: {path}")
    print(f"n = {G.n}, m = {G.m}, r = {G.r}, s = {G.s}, t = {G.t}")
    print(f"|R| (from names) = {len(G.red)}")
    print(f"Has undirected edges: {G.has_undirected}")
    print()
    print("Results:")
    print(f"  None      (shortest s-t path avoiding internal red): {none_val}")
    print(f"  Some      (exists s-t path with >=1 red)           : {some_val}")
    print(f"  Many      (max #red on s-t path; DAG only)        : {many_val}")
    print(f"  Few       (min #red on s-t path)                  : {few_val}")
    print(f"  Alternate (exists alternating s-t path)           : {alt_val}")


if __name__ == "__main__":
    main(sys.argv)

