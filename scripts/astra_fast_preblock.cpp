// Expand a residual core isomorphism into every compatible parent map.
// No graph invariants, hashes, or symmetry restrictions are used here.
#include <algorithm>
#include <cstdint>
#include <vector>

extern "C" int expand(int n, int d, const uint8_t *partial,
                       const int *difference, int *clauses, uint8_t *maps) {
    if (n - d != 3 || n > 64 || d < 0) return -1;
    std::vector<int> source, target;
    bool used[64] = {};
    for (int u = 0; u < d; ++u) {
        if (partial[u] == 255) source.push_back(u);
        else { if (partial[u] >= d) return -2; used[partial[u]] = true; }
    }
    int k = source.size();
    if (k > 3) return -3;
    for (int v = 0; v < d; ++v) if (!used[v]) target.push_back(v);
    if (int(target.size()) != k) return -4;
    for (int v = d; v < n; ++v) { source.push_back(v); target.push_back(v); }
    int count = 0, width = 2 * (3 * d + 3) + 1;
    do {
        bool valid = true;
        for (int i = 0; i < k; ++i) if (target[i] < d) valid = false;
        if (!valid) continue;
        uint8_t *tau = maps + count * n;
        std::copy(partial, partial + n, tau);
        for (unsigned i = 0; i < source.size(); ++i) tau[source[i]] = target[i];
        int *row = clauses + count * width;
        int length = 0, e = 0;
        for (int u = 0; u < n; ++u) for (int v = u + 1; v < n; ++v, ++e) {
            int literal = difference[(e * n + tau[u]) * n + tau[v]];
            if (literal == 2147483647) return -5;
            if (literal) row[++length] = literal;
        }
        if (length >= width) return -6;
        std::sort(row + 1, row + length + 1);
        length = std::unique(row + 1, row + length + 1) - row - 1;
        row[0] = length;
        ++count;
    } while (std::next_permutation(target.begin(), target.end()));
    return count;
}
