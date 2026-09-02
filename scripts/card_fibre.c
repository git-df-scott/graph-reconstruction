/* Exhaustive one-card fibre search for reconstruction counterexamples.
 *
 * Any counterexample pair G, H of order n = m + 1 shares a card: G - v0 ~= C
 * ~= H - w0 for some order-m graph C.  So both are one-vertex extensions of
 * C, and the whole fibre {C + v0(N) : N subset of V(C)} can be settled at
 * once: two extensions with equal decks and non-isomorphic totals are a
 * counterexample, and if no such pair exists then no counterexample has a
 * card isomorphic to C.  That is McKay's method (Australas. J. Combin. 83,
 * 2022) applied to one card at a time, so a class of cards that can be
 * enumerated yields an exact theorem: no counterexample of order n has a
 * card in the class.
 *
 * Per extension the tool computes, in order and only for extensions still
 * tied with another one, (1) the degree sequence of G, (2) the multiset of
 * card degree sequences, (3) the multiset of nauty canonical forms of the
 * m cards G - u, u in V(C) (the card G - v0 = C is common to the fibre),
 * and (4) the canonical form of G.  Every key is a 64-bit hash; equal decks
 * give equal keys, so hashing can only add false hits, and every HIT line
 * is meant to be replayed by scripts/deck_fixed_sat.py or grc.same_deck.
 *
 * Extensions N and g(N), g an automorphism of C, give isomorphic G (extend g
 * by v0 -> v0), hence equal decks, so only one representative per orbit of
 * Aut(C) on subsets is kept (union-find over the generators nauty returns).
 * Extensions giving a regular, disconnected, or co-disconnected G are
 * skipped (those graphs are reconstructible) unless -a is given.
 * -k a:b restricts |N| to [a, b] (sound when C ranges over the cards of a
 * min-degree vertex, for example).  -T reads digraph6 tournaments and
 * extends by a vertex whose out-neighbourhood is N (positive control: the
 * hypomorphic non-isomorphic tournament pairs of order 5 and 6 must be
 * found from their common cards).
 *
 * -S c1,c2,... enumerates, instead of reading stdin, every graph of order
 * sum(c_i) invariant under a permutation of that cycle type (all unions of
 * its orbits on vertex pairs), once per isomorphism class, and runs the
 * fibre on each; the result is then the exact statement that no
 * counterexample of order sum(c_i) + 1 has a card with an automorphism of
 * that cycle type.  -1 / -2 stop after the degree stages (profiling only;
 * no HIT lines are produced).
 *
 * -C c1,c2,... enumerates every self-complementary graph having an
 * antimorphism of the given cycle type (all lengths divisible by 4, plus
 * at most one fixed point): the pairs fall into orbits of even length on
 * which edge and non-edge alternate, so each orbit contributes one bit.
 * Motivation: if G and its complement have the same deck at odd order n,
 * the complement involution on the n cards fixes one, so some card is
 * self-complementary; at order 17 (the first odd order with an even pair
 * count above 13) the fibre over the 703,760 self-complementary graphs of
 * order 16 settles that mechanism exactly.  -r i/k processes only the
 * orbit subsets congruent to i modulo k (parallel chunks; a graph reached
 * from several chunks is processed once per chunk).
 *
 * -d keeps only extensions in which the new vertex has minimum degree in
 * G (every vertex of C of degree |N| - 1 lies in N and none has smaller
 * degree).  Sound because v0 may be chosen as a minimum-degree vertex of
 * G, and the card matching preserves degrees, so H is also such an
 * extension of C.  With cards C of at most E edges this gives the exact
 * statement: no counterexample of order m + 1 with a minimum-degree card
 * of at most E edges.
 *
 * -x FILE pre-loads the isomorphism-class table of the -S / -C enumeration
 * with the graphs listed in FILE (graph6, first token per line), so a run
 * interrupted after writing its per-card lines resumes without repeating
 * those fibres; the enumeration itself is repeated.
 *
 * -m (near-miss mode) computes, exactly, the largest number of common
 * cards over all pairs of non-isomorphic extensions of C with equal degree
 * sequences (the card C itself counts as common), and prints
 * "MAX <C> common=<c>/<n> pairs=<k> <G1> <G2>" per card; c = n is a
 * counterexample.  This is the MaxSAT objective of deck_fixed_sat.py, but
 * over a whole fibre at once and in milliseconds, so it can drive a climb
 * over cards.
 *
 * -H skips controllable cards (Hong, Godsil-McKay: a graph with a
 * controllable card is reconstructible, so no counterexample has one).
 * Controllability is decided by the rank of the walk matrix
 * [1, A1, ..., A^(m-1) 1] modulo the prime 2^61 - 1; full rank modulo p
 * implies full rank over Q, so a skip is always sound, and a deficient
 * rank modulo p merely keeps the card.
 *
 * Input: one graph6 (or digraph6 with -T) line per card C on stdin.
 * Output: one line per card, "C fibre=<extensions kept> hits=<pairs>", and
 * for each pair a line "HIT <G1> <G2>" in graph6/digraph6 with v0 = m.
 *
 * Build:  gcc -O2 -DMAXN=32 -I$NAUTY -o card_fibre scripts/card_fibre.c \
 *             $NAUTY/nauty.c $NAUTY/nautil.c $NAUTY/naugraph.c \
 *             $NAUTY/schreier.c $NAUTY/naurng.c $NAUTY/nautinv.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "nauty.h"
#include "nautinv.h"

#define MAXV 20
typedef uint32_t rowt;

static int tour = 0, allext = 0, kmin = 0, kmax = 1000, stopstage = 9, maxmode = 0, hong = 0;
static long long skipped_ctrl = 0;
static int anti = 0, chunk_i = 0, chunk_k = 1, mindeg = 0, quiet = 0;

#define PRIME 2305843009213693951ULL   /* 2^61 - 1 */
static uint64_t mulmod(uint64_t a, uint64_t b) { return (uint64_t)(((unsigned __int128)a * b) % PRIME); }
static uint64_t powmod(uint64_t a, uint64_t e) { uint64_t r = 1; while (e) { if (e & 1) r = mulmod(r, a); a = mulmod(a, a); e >>= 1; } return r; }
/* 1 if the walk matrix of the (undirected) graph has full rank mod PRIME */
static int controllable_modp(int n, const rowt *rows) {
    uint64_t W[MAXV][MAXV], v[MAXV], w[MAXV];
    for (int i = 0; i < n; i++) v[i] = 1;
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) W[i][k] = v[i];
        for (int i = 0; i < n; i++) { uint64_t s = 0; for (int j = 0; j < n; j++) if (rows[i] >> j & 1) { s += v[j]; if (s >= PRIME) s -= PRIME; } w[i] = s; }
        memcpy(v, w, sizeof v);
    }
    int rank = 0;
    for (int c = 0; c < n && rank < n; c++) {
        int piv = -1;
        for (int r = rank; r < n; r++) if (W[r][c]) { piv = r; break; }
        if (piv < 0) continue;
        if (piv != rank) for (int j = 0; j < n; j++) { uint64_t t = W[piv][j]; W[piv][j] = W[rank][j]; W[rank][j] = t; }
        uint64_t inv = powmod(W[rank][c], PRIME - 2);
        for (int r = rank + 1; r < n; r++) if (W[r][c]) {
            uint64_t f = mulmod(W[r][c], inv);
            for (int j = c; j < n; j++) { uint64_t t = mulmod(f, W[rank][j]); W[r][j] = W[r][j] >= t ? W[r][j] - t : W[r][j] + PRIME - t; }
        }
        rank++;
    }
    return rank == n;
}

static uint64_t fnv(const void *p, size_t len, uint64_t h) {
    const unsigned char *s = p;
    for (size_t i = 0; i < len; i++) { h ^= s[i]; h *= 1099511628211ULL; }
    return h;
}
#define FNV0 14695981039346656037ULL

static int parse_g6(const char *s, rowt *rows) {
    int n, k = 0;
    if (tour) {
        if (s[0] != '&') return -1;
        s++;
    }
    n = s[0] - 63;
    if (n < 1 || n > MAXV) return -1;
    s++;
    for (int i = 0; i < n; i++) rows[i] = 0;
    int nb = tour ? n * n : n * (n - 1) / 2;
    if ((int)strlen(s) < (nb + 5) / 6) return -1;   /* truncated line */
    int have = 0, cur = 0;
    for (int b = 0; b < nb; b++) {
        if (!have) { cur = s[k++] - 63; have = 6; }
        have--;
        int bit = (cur >> have) & 1;
        if (tour) { int i = b / n, j = b % n; if (bit) rows[i] |= 1u << j; }
        else {
            /* column-wise upper triangle: for j=1..n-1, i=0..j-1 */
            int j = 1, t = b; while (t >= j) { t -= j; j++; }
            int i = t;
            if (bit) { rows[i] |= 1u << j; rows[j] |= 1u << i; }
        }
    }
    return n;
}

static void write_g6(int n, const rowt *rows, char *out) {
    int k = 0;
    if (tour) out[k++] = '&';
    out[k++] = 63 + n;
    int nb = tour ? n * n : n * (n - 1) / 2, have = 0, cur = 0;
    for (int b = 0; b < nb; b++) {
        int bit;
        if (tour) bit = (rows[b / n] >> (b % n)) & 1;
        else { int j = 1, t = b; while (t >= j) { t -= j; j++; } bit = (rows[t] >> j) & 1; }
        cur = (cur << 1) | bit; have++;
        if (have == 6) { out[k++] = 63 + cur; have = 0; cur = 0; }
    }
    if (have) { cur <<= (6 - have); out[k++] = 63 + cur; }
    out[k] = 0;
}

static int connected(int n, const rowt *rows) {
    rowt seen = 1, frontier = 1, all = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    while (frontier) {
        rowt nxt = 0;
        for (int i = 0; i < n; i++) if (frontier >> i & 1) nxt |= rows[i];
        frontier = nxt & ~seen; seen |= nxt;
    }
    return seen == all;
}

typedef struct { uint32_t N; uint64_t k1, k2, k3, g; int alive; } ent;

#define MAXGEN 64
static int ngen = 0;
static int gens[MAXGEN][MAXV];
static void store_gen(int count, int *perm, int *orbits, int numorbits, int stabvertex, int n) {
    (void)count; (void)orbits; (void)numorbits; (void)stabvertex;
    if (ngen < MAXGEN) { for (int i = 0; i < n; i++) gens[ngen][i] = perm[i]; ngen++; }
}
static void aut_generators(int n, const rowt *rows) {
    graph g[MAXN];
    int lab[MAXN], ptn[MAXN], orbits[MAXN];
    static DEFAULTOPTIONS_GRAPH(og);
    static DEFAULTOPTIONS_DIGRAPH(od);
    statsblk stats;
    optionblk *op = tour ? &od : &og;
    op->getcanon = FALSE; op->userautomproc = store_gen;
    ngen = 0;
    for (int i = 0; i < n; i++) { EMPTYSET(&g[i], 1); for (int j = 0; j < n; j++) if (rows[i] >> j & 1) ADDELEMENT(&g[i], j); }
    densenauty(g, lab, ptn, orbits, op, &stats, 1, n, NULL);
}
static uint32_t *uf = NULL; static size_t ufcap = 0;
static uint32_t uf_find(uint32_t x) { while (uf[x] != x) { uf[x] = uf[uf[x]]; x = uf[x]; } return x; }
static void uf_union(uint32_t a, uint32_t b) { a = uf_find(a); b = uf_find(b); if (a < b) uf[b] = a; else if (b < a) uf[a] = b; }


static int cmp_ent(const void *a, const void *b) {
    const ent *x = a, *y = b;
    if (x->k1 != y->k1) return x->k1 < y->k1 ? -1 : 1;
    if (x->k2 != y->k2) return x->k2 < y->k2 ? -1 : 1;
    if (x->k3 != y->k3) return x->k3 < y->k3 ? -1 : 1;
    if (x->g != y->g) return x->g < y->g ? -1 : 1;
    return 0;
}

static void build_rows(int m, const rowt *crow, uint32_t N, rowt *rows) {
    /* v0 = m.  Graph: N adjacent to v0.  Tournament: N = out-neighbours of v0. */
    for (int i = 0; i < m; i++) rows[i] = crow[i];
    rows[m] = 0;
    for (int i = 0; i < m; i++) {
        if (N >> i & 1) { rows[m] |= 1u << i; if (!tour) rows[i] |= 1u << m; }
        else if (tour) rows[i] |= 1u << m;
    }
}

static uint64_t canon_hash(int n, const rowt *rows) {
    graph g[MAXN], canong[MAXN];
    int lab[MAXN], ptn[MAXN], orbits[MAXN];
    static DEFAULTOPTIONS_GRAPH(og);
    static DEFAULTOPTIONS_DIGRAPH(od);
    statsblk stats;
    optionblk *op = tour ? &od : &og;
    op->getcanon = TRUE;
    for (int i = 0; i < n; i++) { EMPTYSET(&g[i], 1); for (int j = 0; j < n; j++) if (rows[i] >> j & 1) ADDELEMENT(&g[i], j); }
    densenauty(g, lab, ptn, orbits, op, &stats, 1, n, canong);
    return fnv(canong, n * sizeof(graph), FNV0);
}

static void card_rows(int n, const rowt *rows, int u, rowt *out) {
    rowt lowmask = (1u << u) - 1;
    int k = 0;
    for (int w = 0; w < n; w++) {
        if (w == u) continue;
        rowt r = rows[w];
        out[k++] = (r & lowmask) | ((r >> (u + 1)) << u);
    }
}

static uint64_t degseq_hash(int n, const rowt *rows) {
    unsigned char cnt[MAXV + 1]; memset(cnt, 0, sizeof cnt);
    for (int i = 0; i < n; i++) cnt[__builtin_popcount(rows[i])]++;
    return fnv(cnt, n + 1, FNV0);
}


static uint64_t mix64(uint64_t x) {   /* splitmix64 finaliser */
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
/* order-independent hash of a multiset: sum of mixed elements */
static uint64_t multiset_hash(const uint64_t *v, int m) {
    uint64_t h = 0;
    for (int i = 0; i < m; i++) h += mix64(v[i]);
    return mix64(h);
}
/* hash of the degree sequence of G - u from the degrees of G */
static uint64_t card_degseq_hash(int n, const rowt *rows, const unsigned char *deg, int u) {
    unsigned char cnt[MAXV + 1]; memset(cnt, 0, sizeof cnt);
    for (int w = 0; w < n; w++) if (w != u) cnt[deg[w] - (rows[w] >> u & 1)]++;   /* out-degree loses the arc w -> u */
    return fnv(cnt, n, FNV0);
}

static long long cards = 0, totalhits = 0;
static ent *E = NULL; static size_t cap = 0;

static int u64cmp(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }

static void nearmiss(int m, const rowt *crow, const char *s, size_t ne) {
    int n = m + 1;
    rowt rows[MAXV], card[MAXV];
    char g6a[256], g6b[256];
    uint64_t *H = malloc(ne * m * sizeof *H);
    uint64_t *G = malloc(ne * sizeof *G);
    int best = -1; long long npairs = 0; size_t ba = 0, bb = 0;
    for (size_t i = 0; i < ne;) {
        size_t j = i; while (j < ne && E[j].k1 == E[i].k1) j++;
        if (j - i >= 2) {
            for (size_t t = i; t < j; t++) {
                build_rows(m, crow, E[t].N, rows);
                for (int u = 0; u < m; u++) { card_rows(n, rows, u, card); H[t * m + u] = canon_hash(m, card); }
                qsort(H + t * m, m, sizeof *H, u64cmp);
                G[t] = canon_hash(n, rows);
            }
            for (size_t a = i; a < j; a++) for (size_t b = a + 1; b < j; b++) {
                if (G[a] == G[b]) continue;
                const uint64_t *x = H + a * m, *y = H + b * m;
                int p = 0, q = 0, c = 0;
                while (p < m && q < m) { if (x[p] == y[q]) { c++; p++; q++; } else if (x[p] < y[q]) p++; else q++; }
                c++;   /* the shared card C */
                if (c > best) { best = c; npairs = 1; ba = a; bb = b; }
                else if (c == best) npairs++;
            }
        }
        i = j;
    }
    if (best >= 0) {
        build_rows(m, crow, E[ba].N, rows); write_g6(n, rows, g6a);
        build_rows(m, crow, E[bb].N, rows); write_g6(n, rows, g6b);
        printf("MAX %s common=%d/%d pairs=%lld %s %s\n", s, best, n, npairs, g6a, g6b);
        if (best == n) totalhits++;
    } else printf("MAX %s common=0/%d pairs=0\n", s, n);
    fflush(stdout);
    cards++;
    free(H); free(G);
}

static void process_card(int m, const rowt *crow, const char *s) {
    rowt rows[MAXV], card[MAXV];
    char g6a[256], g6b[256];
    if (hong && !tour && controllable_modp(m, crow)) { skipped_ctrl++; if (!quiet) printf("%s controllable\n", s); cards++; return; }
        int n = m + 1;
    size_t need = (size_t)1 << m;
    if (need > cap) { cap = need; E = realloc(E, cap * sizeof *E); }
    size_t ne = 0;
    if (mindeg && !tour) {
        /* only neighbourhoods N of size k with every vertex of C of degree < k in N and none of degree < k - 1 */
        aut_generators(m, crow);
        if (need > ufcap) { ufcap = need; uf = realloc(uf, ufcap * sizeof *uf); }
        if (ngen) {
            for (uint32_t N = 0; N < need; N++) uf[N] = N;
            for (int gi = 0; gi < ngen; gi++) for (uint32_t N = 0; N < need; N++) {
                uint32_t M = 0; for (int i = 0; i < m; i++) if (N >> i & 1) M |= 1u << gens[gi][i];
                if (M != N) uf_union(N, M);
            }
        }
        int dc[MAXV], dmin = m;
        for (int i = 0; i < m; i++) { dc[i] = __builtin_popcount(crow[i]); if (dc[i] < dmin) dmin = dc[i]; }
        for (int k = (kmin > 1 ? kmin : 1); k <= dmin + 1 && k <= kmax && k <= m; k++) {
            rowt forced = 0, free = 0; int nf = 0, nfree = 0;
            for (int i = 0; i < m; i++) { if (dc[i] == k - 1) { forced |= 1u << i; nf++; } else { free |= 1u << i; nfree++; } }
            if (nf > k) continue;
            int r = k - nf;
            /* enumerate r-subsets of the free vertices via Gosper's hack on a compressed index */
            int idx[MAXV], t = 0; for (int i = 0; i < m; i++) if (free >> i & 1) idx[t++] = i;
            uint32_t sub = r ? (1u << r) - 1 : 0;
            while (1) {
                if (r && sub >= (1u << nfree)) break;
                uint32_t N = forced; for (int j = 0; j < nfree; j++) if (sub >> j & 1) N |= 1u << idx[j];
                if (ngen && uf_find(N) != N) goto next_sub;
                build_rows(m, crow, N, rows);
                if (!allext) {
                    int d0 = __builtin_popcount(rows[0]), reg = 1;
                    for (int i = 1; i < n; i++) if (__builtin_popcount(rows[i]) != d0) { reg = 0; break; }
                    if (!reg && connected(n, rows)) {
                        rowt co[MAXV]; rowt all = (1u << n) - 1;
                        for (int i = 0; i < n; i++) co[i] = all & ~rows[i] & ~(1u << i);
                        if (connected(n, co)) { E[ne].N = N; E[ne].k1 = degseq_hash(n, rows); E[ne].k2 = E[ne].k3 = E[ne].g = 0; E[ne].alive = 1; ne++; }
                    }
                } else { E[ne].N = N; E[ne].k1 = degseq_hash(n, rows); E[ne].k2 = E[ne].k3 = E[ne].g = 0; E[ne].alive = 1; ne++; }
              next_sub:
                if (!r) break;
                { uint32_t c = sub & -sub, rr = sub + c; sub = (((rr ^ sub) >> 2) / c) | rr; }
            }
        }
    } else {
        aut_generators(m, crow);
        if (need > ufcap) { ufcap = need; uf = realloc(uf, ufcap * sizeof *uf); }
        for (uint32_t N = 0; N < need; N++) uf[N] = N;
        for (int gi = 0; gi < ngen; gi++) {
            for (uint32_t N = 0; N < need; N++) {
                uint32_t M = 0;
                for (int i = 0; i < m; i++) if (N >> i & 1) M |= 1u << gens[gi][i];
                if (M != N) uf_union(N, M);
            }
        }
        for (uint32_t N = 0; N < need; N++) {
            if (uf_find(N) != N) continue;
            int k = __builtin_popcount(N);
            if (k < kmin || k > kmax) continue;
            if (mindeg) {
                int ok = 1;
                for (int i = 0; i < m && ok; i++) { int d = __builtin_popcount(crow[i]) + (N >> i & 1); if (d < k) ok = 0; }
                if (!ok) continue;
            }
            build_rows(m, crow, N, rows);
            if (!allext && !tour) {
                int d0 = __builtin_popcount(rows[0]), reg = 1;
                for (int i = 1; i < n; i++) if (__builtin_popcount(rows[i]) != d0) { reg = 0; break; }
                if (reg) continue;
                if (!connected(n, rows)) continue;
                rowt co[MAXV]; rowt all = (1u << n) - 1;
                for (int i = 0; i < n; i++) co[i] = all & ~rows[i] & ~(1u << i);
                if (!connected(n, co)) continue;
            }
            E[ne].N = N; E[ne].k1 = degseq_hash(n, rows); E[ne].k2 = E[ne].k3 = E[ne].g = 0; E[ne].alive = 1;
            ne++;
        }
    }
    qsort(E, ne, sizeof *E, cmp_ent);
    if (maxmode) { nearmiss(m, crow, s, ne); return; }
    if (stopstage < 2) { printf("%s fibre=%zu stage1\n", s, ne); cards++; return; }
    /* stage 2: card degree sequences, for runs of equal k1 */
    for (size_t i = 0; i < ne;) {
        size_t j = i; while (j < ne && E[j].k1 == E[i].k1) j++;
        if (j - i >= 2) {
            for (size_t t = i; t < j; t++) {
                build_rows(m, crow, E[t].N, rows);
                unsigned char deg[MAXV];
                for (int w = 0; w < n; w++) deg[w] = __builtin_popcount(rows[w]);
                uint64_t hs[MAXV];
                for (int u = 0; u < m; u++) hs[u] = card_degseq_hash(n, rows, deg, u);
                E[t].k2 = multiset_hash(hs, m);
            }
        } else E[i].alive = 0;
        i = j;
    }
    qsort(E, ne, sizeof *E, cmp_ent);
    if (stopstage < 3) { printf("%s fibre=%zu stage2\n", s, ne); cards++; return; }
    /* stage 3: canonical cards, for runs of equal (k1,k2) among alive */
    for (size_t i = 0; i < ne;) {
        size_t j = i; while (j < ne && E[j].k1 == E[i].k1 && E[j].k2 == E[i].k2) j++;
        if (E[i].alive && j - i >= 2) {
            for (size_t t = i; t < j; t++) {
                build_rows(m, crow, E[t].N, rows);
                uint64_t hs[MAXV];
                for (int u = 0; u < m; u++) { card_rows(n, rows, u, card); hs[u] = canon_hash(m, card); }
                E[t].k3 = multiset_hash(hs, m);
                E[t].g = canon_hash(n, rows);
            }
        } else for (size_t t = i; t < j; t++) E[t].alive = 0;
        i = j;
    }
    qsort(E, ne, sizeof *E, cmp_ent);
    long long hits = 0;
    for (size_t i = 0; i < ne;) {
        size_t j = i; while (j < ne && E[j].k1 == E[i].k1 && E[j].k2 == E[i].k2 && E[j].k3 == E[i].k3) j++;
        if (E[i].alive && j - i >= 2) {
            /* distinct g values in the run are candidate counterexamples */
            for (size_t a = i; a < j; a++) {
                if (a > i && E[a].g == E[a-1].g) continue;
                for (size_t b = a + 1; b < j; b++) {
                    if (E[b].g == E[b-1].g) continue;
                    if (E[b].g == E[a].g) continue;
                    build_rows(m, crow, E[a].N, rows); write_g6(n, rows, g6a);
                    build_rows(m, crow, E[b].N, rows); write_g6(n, rows, g6b);
                    printf("HIT %s %s\n", g6a, g6b);
                    hits++;
                }
            }
        }
        i = j;
    }
    if (!quiet || hits) { printf("%s fibre=%zu hits=%lld\n", s, ne, hits); fflush(stdout); }
    cards++; totalhits += hits;
    }

static uint64_t *hset = NULL; static size_t hcap = 0, hcnt = 0;
static int hset_add(uint64_t h) {   /* returns 1 if new */
    if (h == 0) h = 1;
    if (hcnt * 2 >= hcap) {
        size_t ncap = hcap ? hcap * 2 : (1u << 20);
        uint64_t *nh = calloc(ncap, sizeof *nh);
        for (size_t i = 0; i < hcap; i++) if (hset[i]) { size_t j = hset[i] & (ncap - 1); while (nh[j]) j = (j + 1) & (ncap - 1); nh[j] = hset[i]; }
        free(hset); hset = nh; hcap = ncap;
    }
    size_t j = h & (hcap - 1);
    while (hset[j]) { if (hset[j] == h) return 0; j = (j + 1) & (hcap - 1); }
    hset[j] = h; hcnt++; return 1;
}

static void enumerate_type(const char *spec) {
    int ct[MAXV], nc = 0, n = 0;
    const char *p = spec;
    while (*p) { ct[nc] = atoi(p); n += ct[nc]; nc++; while (*p && *p != ',') p++; if (*p == ',') p++; }
    if (n < 2 || n + 1 > MAXV) { fprintf(stderr, "bad cycle type\n"); exit(2); }
    int perm[MAXV], start = 0;
    for (int c = 0; c < nc; c++) { for (int i = 0; i < ct[c]; i++) perm[start + i] = start + (i + 1) % ct[c]; start += ct[c]; }
    rowt omask[64][MAXV], amask[64][MAXV]; int k = 0;
    unsigned char seen[MAXV][MAXV]; memset(seen, 0, sizeof seen);
    for (int a = 0; a < n; a++) for (int b = a + 1; b < n; b++) {
        if (seen[a][b]) continue;
        for (int i = 0; i < n; i++) omask[k][i] = amask[k][i] = 0;
        int x = a, y = b, pos = 0;
        while (1) {
            int u = x < y ? x : y, v = x < y ? y : x;
            if (seen[u][v]) break;
            seen[u][v] = 1;
            if (!anti || pos % 2 == 0) { omask[k][u] |= 1u << v; omask[k][v] |= 1u << u; }
            else { amask[k][u] |= 1u << v; amask[k][v] |= 1u << u; }
            x = perm[x]; y = perm[y]; pos++;
        }
        if (anti && pos % 2) { fprintf(stderr, "odd pair-orbit: not an antimorphism type\n"); exit(2); }
        k++;
        if (k > 40) { fprintf(stderr, "too many orbits\n"); exit(2); }
    }
    fprintf(stderr, "cycle type %s: n=%d pair-orbits=%d subsets=%llu\n", spec, n, k, 1ULL << k);
    rowt crow[MAXV]; char g6[256]; long long distinct = 0;
    for (uint64_t sub = (uint64_t)chunk_i; sub < (1ULL << k); sub += chunk_k) {
        for (int i = 0; i < n; i++) crow[i] = 0;
        for (int o = 0; o < k; o++) {
            if (sub >> o & 1) { for (int i = 0; i < n; i++) crow[i] |= omask[o][i]; }
            else if (anti) { for (int i = 0; i < n; i++) crow[i] |= amask[o][i]; }
        }
        if (!hset_add(canon_hash(n, crow))) continue;
        distinct++;
        write_g6(n, crow, g6);
        process_card(n, crow, g6);
    }
    fprintf(stderr, "cycle type %s: distinct graphs %lld\n", spec, distinct);
}

static const char *skipfile = NULL;
static void load_skiplist(void) {
    FILE *f = fopen(skipfile, "r"); if (!f) { fprintf(stderr, "cannot open %s\n", skipfile); exit(2); }
    char line[4096]; rowt crow[MAXV]; long long n = 0;
    while (fgets(line, sizeof line, f)) {
        char *s = line; size_t L = strcspn(s, " \t\r\n"); s[L] = 0;
        if (!L || *s == '#' || *s == 'H' || *s == 'M' || !strncmp(s, "cards=", 6) || !strncmp(s, "cycle", 5)) continue;
        int m = parse_g6(s, crow); if (m < 1) continue;
        if (hset_add(canon_hash(m, crow))) n++;
    }
    fclose(f);
    fprintf(stderr, "skip-list: %lld distinct cards pre-loaded\n", n);
}

int main(int argc, char **argv) {
    const char *spec = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-T")) tour = 1;
        else if (!strcmp(argv[i], "-a")) allext = 1;
        else if (!strcmp(argv[i], "-m")) maxmode = 1;
        else if (!strcmp(argv[i], "-d")) mindeg = 1;
        else if (!strcmp(argv[i], "-q")) quiet = 1;
        else if (!strcmp(argv[i], "-H")) hong = 1;
        else if (!strcmp(argv[i], "-1")) stopstage = 1;
        else if (!strcmp(argv[i], "-2")) stopstage = 2;
        else if (!strcmp(argv[i], "-k") && i + 1 < argc) { sscanf(argv[++i], "%d:%d", &kmin, &kmax); }
        else if (!strcmp(argv[i], "-S") && i + 1 < argc) spec = argv[++i];
        else if (!strcmp(argv[i], "-C") && i + 1 < argc) { spec = argv[++i]; anti = 1; }
        else if (!strcmp(argv[i], "-r") && i + 1 < argc) { sscanf(argv[++i], "%d/%d", &chunk_i, &chunk_k); }
        else if (!strcmp(argv[i], "-x") && i + 1 < argc) skipfile = argv[++i];
        else { fprintf(stderr, "usage: card_fibre [-T] [-a] [-k min:max] [-S cycletype | -C antimorphism-type] [-r i/k] [-m] [-H] [-d] [-q] [-1|-2] < cards\n"); return 2; }
    }
    if (skipfile) load_skiplist();
    if (spec) { enumerate_type(spec); fprintf(stderr, "cards=%lld hits=%lld controllable-skipped=%lld\n", cards, totalhits, skipped_ctrl); return 0; }
    char line[4096];
    rowt crow[MAXV];
    while (fgets(line, sizeof line, stdin)) {
        char *s = line; while (*s == ' ') s++;
        size_t L = strlen(s); while (L && (s[L-1] == '\n' || s[L-1] == '\r' || s[L-1] == ' ')) s[--L] = 0;
        if (!L || *s == '#') continue;
        int m = parse_g6(s, crow);
        if (m < 1 || m + 1 > MAXV) { fprintf(stderr, "bad line: %s\n", s); continue; }
        process_card(m, crow, s);
    }
    fprintf(stderr, "cards=%lld hits=%lld controllable-skipped=%lld\n", cards, totalhits, skipped_ctrl);
    return 0;
}
