Vertex = Tuple[int, int]
Edge = Tuple[Vertex, Vertex]
Triangle = Tuple[Vertex, Vertex, Vertex]
Color = str

COLORS: Tuple[Color, ...] = ("r", "g", "b")


def _vkey(v: Vertex) -> Tuple[int, int]:
    return v[0], v[1]


def _canon_edge(a: Vertex, b: Vertex) -> Edge:
    return (a, b) if _vkey(a) < _vkey(b) else (b, a)


def _ordered_pair(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a < b else (b, a)


def _clip_prob(p: float, upper: float = 0.499999) -> float:
    return min(upper, max(0.0, float(p)))


@dataclass(frozen=True)
class TriangulatedTorus:
    L: int
    vertices: List[Vertex]
    edges: List[Edge]
    triangles: List[Triangle]
    edge_index_of: Dict[Edge, int]
    vertex_to_edges: Dict[Vertex, Tuple[int, ...]]
    edge_to_triangles: Dict[int, Tuple[int, ...]]
    triangle_to_edges: List[Tuple[int, int, int]]

    @staticmethod
    def build(L: int) -> "TriangulatedTorus":
        verts: List[Vertex] = [(x, y) for y in range(L) for x in range(L)]
        tris: List[Triangle] = []
        for y in range(L):
            for x in range(L):
                v00 = (x, y)
                v10 = ((x + 1) % L, y)
                v01 = (x, (y + 1) % L)
                v11 = ((x + 1) % L, (y + 1) % L)
                tris.append((v00, v10, v11))
                tris.append((v00, v01, v11))

        edge_index_of: Dict[Edge, int] = {}
        triangle_to_edges: List[Tuple[int, int, int]] = []

        def get_edge_index(a: Vertex, b: Vertex) -> int:
            edge = _canon_edge(a, b)
            if edge not in edge_index_of:
                edge_index_of[edge] = len(edge_index_of)
            return edge_index_of[edge]

        for a, b, c in tris:
            eab = get_edge_index(a, b)
            ebc = get_edge_index(b, c)
            eca = get_edge_index(c, a)
            triangle_to_edges.append((eab, ebc, eca))

        edges = [None] * len(edge_index_of)
        for edge, index in edge_index_of.items():
            edges[index] = edge

        vertex_to_edges_lists: Dict[Vertex, List[int]] = {v: [] for v in verts}
        for edge_index, (a, b) in enumerate(edges):
            vertex_to_edges_lists[a].append(edge_index)
            vertex_to_edges_lists[b].append(edge_index)

        edge_to_triangles_lists: Dict[int, List[int]] = {
            edge_index: [] for edge_index in range(len(edges))
        }
        for triangle_index, (e0, e1, e2) in enumerate(triangle_to_edges):
            edge_to_triangles_lists[e0].append(triangle_index)
            edge_to_triangles_lists[e1].append(triangle_index)
            edge_to_triangles_lists[e2].append(triangle_index)

        return TriangulatedTorus(
            L=L,
            vertices=verts,
            edges=edges,
            triangles=tris,
            edge_index_of=edge_index_of,
            vertex_to_edges={
                v: tuple(sorted(edge_indices))
                for v, edge_indices in vertex_to_edges_lists.items()
            },
            edge_to_triangles={
                edge_index: tuple(sorted(triangles))
                for edge_index, triangles in edge_to_triangles_lists.items()
            },
            triangle_to_edges=triangle_to_edges,
        )


@dataclass(frozen=True)
class FaceZStabilizer:
    color: Color
    face_index: int
    edge_indices: Tuple[int, int, int]


@dataclass(frozen=True)
class VertexXCliffordStabilizer:
    color: Color
    vertex: Vertex
    x_edges: Tuple[int, ...]
    cz_edge_pairs: Tuple[Tuple[int, int], ...]
    cz_colors: Tuple[Color, Color]


@dataclass(frozen=True)
class D4Stabilizers:
    lat: TriangulatedTorus
    face_Z: List[FaceZStabilizer]
    vertex_X: List[VertexXCliffordStabilizer]


@dataclass(frozen=True)
class DressingPairEvent:
    qubits: Tuple[int, int]
    multiplicity: int


def edge_color_to_qubit(edge_index: int, color: Color) -> int:
    color_offset = {"r": 0, "g": 1, "b": 2}[color]
    return 3 * edge_index + color_offset


def qubit_to_edge_color(q: int) -> Tuple[int, Color]:
    return q // 3, COLORS[q % 3]


def build_d4_stabilizers(lat: TriangulatedTorus) -> D4Stabilizers:
    face_Z: List[FaceZStabilizer] = []
    for face_index, edge_indices in enumerate(lat.triangle_to_edges):
        for color in COLORS:
            face_Z.append(
                FaceZStabilizer(
                    color=color,
                    face_index=face_index,
                    edge_indices=edge_indices,
                )
            )

    cz_pairs_by_color: Dict[Color, Dict[Vertex, List[Tuple[int, int]]]] = {
        color: {vertex: [] for vertex in lat.vertices}
        for color in COLORS
    }

    for v0, v1, v2 in lat.triangles:
        e01 = lat.edge_index_of[_canon_edge(v0, v1)]
        e12 = lat.edge_index_of[_canon_edge(v1, v2)]
        cz_pairs_by_color["r"][v0].append((e01, e12))
        # cup-product order a_r(01) a_b(12) for green (Kobayashi-Zhu-Hsin SM)
        cz_pairs_by_color["g"][v1].append((e12, e01))
        cz_pairs_by_color["b"][v2].append((e01, e12))

    partner_colors = {
        "r": ("g", "b"),
        "g": ("b", "r"),
        "b": ("r", "g"),
    }

    vertex_X: List[VertexXCliffordStabilizer] = []
    for vertex in lat.vertices:
        incident_edges = lat.vertex_to_edges[vertex]
        for color in COLORS:
            vertex_X.append(
                VertexXCliffordStabilizer(
                    color=color,
                    vertex=vertex,
                    x_edges=incident_edges,
                    cz_edge_pairs=tuple(cz_pairs_by_color[color][vertex]),
                    cz_colors=partner_colors[color],
                )
            )

    return D4Stabilizers(lat=lat, face_Z=face_Z, vertex_X=vertex_X)


def build_dual_x_observable_paths(lat: TriangulatedTorus) -> List[List[int]]:
    def edge_between(a: Vertex, b: Vertex) -> int:
        return lat.edge_index_of[_canon_edge(a, b)]

    obs_paths: List[List[int]] = []
    for color in COLORS:
        path_x_dual: List[int] = []
        for y in range(lat.L):
            e1 = edge_between((0, y), (1, y))
            e2 = edge_between((0, y), (1, (y + 1) % lat.L))
            path_x_dual.extend([edge_color_to_qubit(e1, color), edge_color_to_qubit(e2, color)])
        obs_paths.append(path_x_dual)

        path_y_dual: List[int] = []
        for x in range(lat.L):
            e1 = edge_between((x, 0), (x, 1))
            e2 = edge_between((x, 0), ((x + 1) % lat.L, 1))
            path_y_dual.extend([edge_color_to_qubit(e1, color), edge_color_to_qubit(e2, color)])
        obs_paths.append(path_y_dual)

    return obs_paths


def build_vertex_x_measurement_supports(stab: D4Stabilizers) -> List[List[int]]:
    x_stabs_qubits: List[List[int]] = []
    for v_stab in stab.vertex_X:
        x_stabs_qubits.append(
            [edge_color_to_qubit(edge_index, v_stab.color) for edge_index in v_stab.x_edges]
        )
    return x_stabs_qubits


def build_pairwise_dressing_events(stab: D4Stabilizers) -> List[DressingPairEvent]:
    counts: Dict[Tuple[int, int], int] = {}
    for v_stab in stab.vertex_X:
        color1, color2 = v_stab.cz_colors
        for edge1, edge2 in v_stab.cz_edge_pairs:
            q1 = edge_color_to_qubit(edge1, color1)
            q2 = edge_color_to_qubit(edge2, color2)
            counts[_ordered_pair(q1, q2)] = counts.get(_ordered_pair(q1, q2), 0) + 1
    return [
        DressingPairEvent(qubits=pair, multiplicity=counts[pair])
        for pair in sorted(counts)
    ]


def build_dressing_qubit_incidence(
    pair_events: Sequence[DressingPairEvent],
) -> Dict[int, int]:
    incidence: Dict[int, int] = {}
    for event in pair_events:
        q1, q2 = event.qubits
        incidence[q1] = incidence.get(q1, 0) + event.multiplicity
        incidence[q2] = incidence.get(q2, 0) + event.multiplicity
    return incidence


def summarize_geometry(stab: D4Stabilizers) -> Dict[str, float]:
    pair_events = build_pairwise_dressing_events(stab)
    incidence = build_dressing_qubit_incidence(pair_events)
    red_counts = [len(v_stab.cz_edge_pairs) for v_stab in stab.vertex_X if v_stab.color == "r"]
    return {
        "vertices": float(len(stab.lat.vertices)),
        "edges": float(len(stab.lat.edges)),
        "triangles": float(len(stab.lat.triangles)),
        "x_checks": float(len(stab.vertex_X)),
        "face_z_checks": float(len(stab.face_Z)),
        "unique_dressing_pairs": float(len(pair_events)),
        "max_dressing_incidence": float(max(incidence.values(), default=0)),
        "avg_red_pairs_per_vertex": float(sum(red_counts) / len(red_counts)),
    }

def _gf2_rank(rows: np.ndarray) -> int:
    M = (np.array(rows, dtype=np.uint8) & 1).copy()
    r = 0
    for c in range(M.shape[1]):
        piv = next((i for i in range(r, M.shape[0]) if M[i, c]), None)
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(M.shape[0]):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
        if r == M.shape[0]:
            break
    return r


def count_noncommuting_x_check_pairs(stab: D4Stabilizers) -> Tuple[int, int]:
    """dressed X チェック対の交換子を検査する。
    戻り値 = (演算子として非可換な対の数, 平坦（Z チェックが全て +1）な部分空間でも非可換な対の数)。
    正しい D4 符号では後者は 0（Kobayashi-Zhu-Hsin SM）。緑の CZ の向きを誤ると L=3 で 90 対が非可換になる。"""
    n = 3 * len(stab.lat.edges)
    data = []
    for vs in stab.vertex_X:
        sv = np.zeros(n, np.uint8)
        for e in vs.x_edges:
            sv[edge_color_to_qubit(e, vs.color)] ^= 1
        prs = [(edge_color_to_qubit(a, vs.cz_colors[0]), edge_color_to_qubit(b, vs.cz_colors[1])) for a, b in vs.cz_edge_pairs]
        data.append((sv, prs))
    F = np.zeros((len(stab.face_Z), n), np.uint8)
    for i, fz in enumerate(stab.face_Z):
        for e in fz.edge_indices:
            F[i, edge_color_to_qubit(e, fz.color)] ^= 1
    rF = _gf2_rank(F)
    op_nc = flat_nc = 0
    for A in range(len(data)):
        for B in range(A + 1, len(data)):
            (sA, pA), (sB, pB) = data[A], data[B]
            y = np.zeros(n, np.uint8)
            c = 0
            for (i, j), sv in [(pr, sB) for pr in pA] + [(pr, sA) for pr in pB]:
                y[i] ^= sv[j]
                y[j] ^= sv[i]
                c ^= int(sv[i]) & int(sv[j])
            if y.any() or c:
                op_nc += 1
                if c or _gf2_rank(np.vstack([F, y])) > rF:
                    flat_nc += 1
    return op_nc, flat_nc