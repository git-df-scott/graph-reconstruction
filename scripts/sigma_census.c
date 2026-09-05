/* Complete named-colour reconstruction census via local-map systems.
 *
 * A local-map system at order n is a tuple (sigma_0, ..., sigma_{n-1}) where
 * sigma_i is a permutation of {0..n-1} fixing i.  The equations
 *     G[u,v] = H[sigma_i(u), sigma_i(v)]   for all u,v != i
 * generate a partition of the 2*C(n,2) edge slots.  Two edge-coloured complete
 * graphs (G side, H side) coloured by the classes are hypomorphic as named
 * coloured graphs by construction.  An exact-label globalizer is a permutation
 * p with class(G,e) = class(H,p(e)) for every edge e, i.e. a colour-preserving
 * isomorphism.  A system with at least two classes and no globalizer is a
 * counterexample to reconstruction of edge-coloured complete graphs with named
 * colours at order n, and every such counterexample (with any number of
 * colours) arises from some system, because the generated partition is the
 * finest possible.
 *
 * Normalisation: relabel H by sigma_0^{-1} so that sigma_0 is the identity.
 * Reduction: conjugation by rho in Sym({2..n-1}) fixes indices 0 and 1 and
 * maps sigma_1 to rho sigma_1 rho^{-1}; we require sigma_1 to be lexicographically
 * minimal in that orbit.  Everything else is enumerated exhaustively.
 *
 * Usage: sigma_census N   (N = 5 or 6; N=5 must report zero hits, matching
 * the 7,962,624-system census recorded in docs/LAST_GLOBALIZER_STRIKE.md).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 7
#define MAXE 21

static int N, E;
static int eidx[MAXN][MAXN];
static int eu[MAXE], ev[MAXE];

/* all permutations of {0..N-1} */
static int perms[5040][MAXN];
static int nperms;
/* permutations fixing i */
static int fix[MAXN][720];
static int nfix[MAXN];

static void gen_perms(void) {
    int p[MAXN], used[MAXN];
    memset(used, 0, sizeof used);
    nperms = 0;
    /* iterative permutation generation via recursion */
    void rec(int k) {
        if (k == N) { memcpy(perms[nperms++], p, sizeof(int) * N); return; }
        for (int v = 0; v < N; v++) if (!used[v]) { used[v] = 1; p[k] = v; rec(k + 1); used[v] = 0; }
    }
    rec(0);
    for (int i = 0; i < N; i++) {
        nfix[i] = 0;
        for (int t = 0; t < nperms; t++) if (perms[t][i] == i) fix[i][nfix[i]++] = t;
    }
}

/* union-find on 2E slots */
static int parent[2 * MAXE];
static int find(int x) { while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; }
static void unite(int a, int b) { a = find(a); b = find(b); if (a != b) parent[a] = b; }

static int cls[2 * MAXE];
static int nclasses;

/* edge image table: eimg[t][e] = index of image of edge e under perm t */
static int eimg[5040][MAXE];

static long long systems = 0, hits = 0, identity_rescued = 0, multi_class = 0;
static int cur[MAXN]; /* current perm index per row */

static int has_globalizer(void) {
    /* identity */
    int ok = 1;
    for (int e = 0; e < E; e++) if (cls[e] != cls[E + e]) { ok = 0; break; }
    if (ok) { identity_rescued++; return 1; }
    /* vertex signatures: sorted class multiset at each vertex on each side */
    int sigG[MAXN][MAXN], sigH[MAXN][MAXN];
    for (int v = 0; v < N; v++) {
        int k = 0;
        for (int w = 0; w < N; w++) if (w != v) { sigG[v][k] = cls[eidx[v][w]]; sigH[v][k] = cls[E + eidx[v][w]]; k++; }
        /* insertion sort */
        for (int a = 1; a < N - 1; a++) { int x = sigG[v][a], b = a - 1; while (b >= 0 && sigG[v][b] > x) { sigG[v][b + 1] = sigG[v][b]; b--; } sigG[v][b + 1] = x; }
        for (int a = 1; a < N - 1; a++) { int x = sigH[v][a], b = a - 1; while (b >= 0 && sigH[v][b] > x) { sigH[v][b + 1] = sigH[v][b]; b--; } sigH[v][b + 1] = x; }
    }
    /* backtracking: map G vertex v -> H vertex w with equal signature, preserving classes */
    int map[MAXN], used[MAXN];
    memset(used, 0, sizeof used);
    int bt(int v) {
        if (v == N) return 1;
        for (int w = 0; w < N; w++) {
            if (used[w]) continue;
            if (memcmp(sigG[v], sigH[w], sizeof(int) * (N - 1))) continue;
            int good = 1;
            for (int u = 0; u < v; u++) if (cls[eidx[v][u]] != cls[E + eidx[w][map[u]]]) { good = 0; break; }
            if (!good) continue;
            map[v] = w; used[w] = 1;
            if (bt(v + 1)) return 1;
            used[w] = 0;
        }
        return 0;
    }
    return bt(0);
}

static void evaluate(void) {
    for (int s = 0; s < 2 * E; s++) parent[s] = s;
    for (int i = 0; i < N; i++) {
        int t = cur[i];
        for (int e = 0; e < E; e++) {
            if (eu[e] == i || ev[e] == i) continue;
            unite(e, E + eimg[t][e]);
        }
    }
    nclasses = 0;
    int label[2 * MAXE];
    for (int s = 0; s < 2 * E; s++) label[s] = -1;
    for (int s = 0; s < 2 * E; s++) { int r = find(s); if (label[r] < 0) label[r] = nclasses++; cls[s] = label[r]; }
    systems++;
    if (nclasses < 2) { identity_rescued++; return; }
    multi_class++;
    if (!has_globalizer()) {
        hits++;
        printf("ZERO-GLOBALIZER SYSTEM classes=%d rows:", nclasses);
        for (int i = 0; i < N; i++) { printf(" ("); for (int v = 0; v < N; v++) printf("%d%s", perms[cur[i]][v], v + 1 < N ? "," : ""); printf(")"); }
        printf("\n"); fflush(stdout);
    }
}

static int is_lexmin_sigma1(int t) {
    /* conjugate perms[t] by every rho in Sym({2..N-1}) (fixing 0,1); require perms[t] <= all conjugates */
    for (int r = 0; r < nperms; r++) {
        if (perms[r][0] != 0 || perms[r][1] != 1) continue;
        int rinv[MAXN]; for (int v = 0; v < N; v++) rinv[perms[r][v]] = v;
        /* conj[v] = rho(sigma(rho^{-1}(v))) */
        for (int v = 0; v < N; v++) {
            int c = perms[r][perms[t][rinv[v]]];
            if (c < perms[t][v]) return 0;
            if (c > perms[t][v]) break;
        }
    }
    return 1;
}

int main(int argc, char **argv) {
    N = argc > 1 ? atoi(argv[1]) : 5;
    if (N < 3 || N > MAXN) return 1;
    E = 0;
    for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) { eidx[u][v] = eidx[v][u] = E; eu[E] = u; ev[E] = v; E++; }
    gen_perms();
    for (int t = 0; t < nperms; t++) for (int e = 0; e < E; e++) eimg[t][e] = eidx[perms[t][eu[e]]][perms[t][ev[e]]];
    int id = -1; for (int t = 0; t < nperms; t++) { int ok = 1; for (int v = 0; v < N; v++) if (perms[t][v] != v) ok = 0; if (ok) id = t; }
    cur[0] = id;
    int s1list[720], ns1 = 0;
    for (int k = 0; k < nfix[1]; k++) if (is_lexmin_sigma1(fix[1][k])) s1list[ns1++] = fix[1][k];
    fprintf(stderr, "N=%d E=%d perms=%d fix-per-row=%d lexmin sigma_1 choices=%d\n", N, E, nperms, nfix[1], ns1);
    /* odometer over rows 2..N-1, outer loop over sigma_1 choices */
    for (int a = 0; a < ns1; a++) {
        cur[1] = s1list[a];
        int idx[MAXN]; for (int i = 2; i < N; i++) idx[i] = 0;
        while (1) {
            for (int i = 2; i < N; i++) cur[i] = fix[i][idx[i]];
            evaluate();
            int i = N - 1;
            while (i >= 2) { idx[i]++; if (idx[i] < nfix[i]) break; idx[i] = 0; i--; }
            if (i < 2) break;
        }
        fprintf(stderr, "sigma_1 choice %d/%d done: systems=%lld multi-class=%lld hits=%lld\n", a + 1, ns1, systems, multi_class, hits);
    }
    printf("N=%d systems=%lld multi-class=%lld identity-or-trivial=%lld zero-globalizer=%lld\n", N, systems, multi_class, identity_rescued, hits);
    return 0;
}
