from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Graph:
    """A finite simple graph represented by adjacency bitsets."""

    adj: tuple[int, ...]

    def __post_init__(self) -> None:
        n = len(self.adj)
        mask = (1 << n) - 1
        for v, row in enumerate(self.adj):
            if row & ~mask:
                raise ValueError("adjacency outside vertex set")
            if row & (1 << v):
                raise ValueError("loops are not allowed")
            for w in range(v):
                if bool(row & (1 << w)) != bool(self.adj[w] & (1 << v)):
                    raise ValueError("adjacency must be symmetric")

    @property
    def n(self) -> int:
        return len(self.adj)

    @property
    def m(self) -> int:
        return sum(row.bit_count() for row in self.adj) // 2

    @property
    def degrees(self) -> tuple[int, ...]:
        return tuple(row.bit_count() for row in self.adj)

    def edge(self, u: int, v: int) -> bool:
        return bool(self.adj[u] & (1 << v))

    def delete_vertex(self, removed: int) -> "Graph":
        if not 0 <= removed < self.n:
            raise IndexError(removed)
        keep = [v for v in range(self.n) if v != removed]
        return self.induced(keep)

    def induced(self, vertices: list[int] | tuple[int, ...]) -> "Graph":
        pos = {old: new for new, old in enumerate(vertices)}
        rows = [0] * len(vertices)
        for i, old_u in enumerate(vertices):
            for old_v in vertices:
                if old_v > old_u and self.edge(old_u, old_v):
                    j = pos[old_v]
                    rows[i] |= 1 << j
                    rows[j] |= 1 << i
        return Graph(tuple(rows))

    def permute(self, order: tuple[int, ...] | list[int]) -> "Graph":
        if sorted(order) != list(range(self.n)):
            raise ValueError("order must be a permutation")
        return self.induced(tuple(order))

    def complement(self) -> "Graph":
        mask = (1 << self.n) - 1
        return Graph(tuple((~row) & mask & ~(1 << v) for v, row in enumerate(self.adj)))

    @classmethod
    def from_edge_mask(cls, n: int, mask: int) -> "Graph":
        rows = [0] * n
        bit = 0
        for u in range(n):
            for v in range(u + 1, n):
                if mask & (1 << bit):
                    rows[u] |= 1 << v
                    rows[v] |= 1 << u
                bit += 1
        if mask >> bit:
            raise ValueError("edge mask is too large")
        return cls(tuple(rows))

    def edge_mask(self, order: tuple[int, ...] | None = None) -> int:
        order = order or tuple(range(self.n))
        value = 0
        bit = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if self.edge(order[i], order[j]):
                    value |= 1 << bit
                bit += 1
        return value

    @classmethod
    def from_graph6(cls, text: str) -> "Graph":
        """Parse an ordinary graph6 record (orders 0 through 62)."""

        text = text.strip()
        if text.startswith(">>graph6<<"):
            text = text[len(">>graph6<<") :]
        if not text:
            raise ValueError("empty graph6 record")
        n = ord(text[0]) - 63
        if not 0 <= n <= 62:
            raise ValueError("extended graph6 order is not supported by this small checker")
        bits: list[int] = []
        for character in text[1:]:
            value = ord(character) - 63
            if not 0 <= value < 64:
                raise ValueError("invalid graph6 character")
            bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
        required = n * (n - 1) // 2
        if len(bits) < required:
            raise ValueError("truncated graph6 record")
        rows = [0] * n
        cursor = 0
        for v in range(1, n):
            for u in range(v):
                if bits[cursor]:
                    rows[u] |= 1 << v
                    rows[v] |= 1 << u
                cursor += 1
        return cls(tuple(rows))

    def add_leaf(self, neighbor: int) -> "Graph":
        if not 0 <= neighbor < self.n:
            raise IndexError(neighbor)
        rows = list(self.adj) + [0]
        rows[neighbor] |= 1 << self.n
        rows[self.n] |= 1 << neighbor
        return Graph(tuple(rows))

    def to_graph6(self) -> str:
        if self.n > 62:
            raise ValueError("extended graph6 order is not supported")
        output = [chr(self.n + 63)]
        value = bits = 0
        for v in range(1, self.n):
            for u in range(v):
                value = (value << 1) | int(self.edge(u, v))
                bits += 1
                if bits == 6:
                    output.append(chr(value + 63))
                    value = bits = 0
        if bits:
            output.append(chr((value << (6 - bits)) + 63))
        return "".join(output)

    def attach_gadget(self, neighbor: int, gadget: "Graph", attachment_mask: int) -> "Graph":
        """Disjointly add `gadget` and join selected gadget vertices to one anchor."""

        if not 0 <= neighbor < self.n:
            raise IndexError(neighbor)
        if attachment_mask <= 0 or attachment_mask >= (1 << gadget.n):
            raise ValueError("attachment_mask must select a nonempty subset of gadget vertices")
        rows = list(self.adj) + [0] * gadget.n
        for u in range(gadget.n):
            for v in range(u + 1, gadget.n):
                if gadget.edge(u, v):
                    rows[self.n + u] |= 1 << (self.n + v)
                    rows[self.n + v] |= 1 << (self.n + u)
            if attachment_mask & (1 << u):
                rows[neighbor] |= 1 << (self.n + u)
                rows[self.n + u] |= 1 << neighbor
        return Graph(tuple(rows))
