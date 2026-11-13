# -*- coding: utf-8 -*-
"""Geometric reachability check for the utility concept segments (suggested by the Codex/Astra review).
Each axis-aligned box -> centre line; two segments of the same system are connected when their centre lines come within EPS
(end-end, T-branch, or a same-level crossing, which this model uses as a tee). Reports connected components per system. This is NOT a flow / hydraulic check."""
import json, csv, sys
import numpy as np
D = json.load(open("../data/campus.json")); U = D["util"]; S = D["usys"]; EPS = 1.6
def line(q):
    x, y, z, dx, dy, dz = q[:6]; c = np.array([x + dx / 2, y + dy / 2, z + dz / 2]); d = [dx, dy, dz]; ax = int(np.argmax(d)); w = sorted(d)[1]
    h = np.zeros(3); h[ax] = max(d[ax] - w, 0) / 2; return c - h, c + h
def dist_pt_seg(p, a, b):
    ab = b - a; L = ab @ ab; t = 0 if L == 0 else min(1, max(0, (p - a) @ ab / L)); return np.linalg.norm(p - (a + t * ab))
def seg_seg(a0, a1, b0, b1):
    # axis-aligned segments: distance between the two boxes spanned by the centre lines (covers end-end, T-branch and same-level crossing = tee)
    lo = np.maximum(np.minimum(a0, a1), np.minimum(b0, b1)); hi = np.minimum(np.maximum(a0, a1), np.maximum(b0, b1))
    return float(np.linalg.norm(np.maximum(lo - hi, 0)))
rows = []
for si, sy in enumerate(S):
    idx = [i for i, q in enumerate(U) if q[6] == si]
    if not idx: continue
    L = [line(U[i]) for i in idx]; n = len(idx); par = list(range(n))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            a0, a1 = L[i]; b0, b1 = L[j]
            if seg_seg(a0, a1, b0, b1) <= EPS: par[find(i)] = find(j)
    comp = {}
    for i in range(n): comp.setdefault(find(i), []).append(idx[i])
    sizes = sorted((len(v) for v in comp.values()), reverse=True)
    fabs = sorted({U[v[0]][7] or "campus" for v in comp.values()})
    rows.append([sy[0], n, len(comp), min(sizes), " ".join(map(str, sizes[:12])), " ".join(fabs)])
    print(sy[0].ljust(11), "segments", str(n).rjust(4), "components", str(len(comp)).rjust(3), "sizes", sizes[:10])
out = sys.argv[1] if len(sys.argv) > 1 else "utility_connectivity_check.csv"
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["system", "segments", "connected_components", "smallest_component", "component_sizes", "where"]); w.writerows(rows)
