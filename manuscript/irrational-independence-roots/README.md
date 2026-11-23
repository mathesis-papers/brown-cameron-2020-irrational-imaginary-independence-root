# Purely imaginary independence roots with rational squared imaginary part

This package contains the note **Extending Brown and Cameron's classification
of purely imaginary independence roots**, by Haobo Ma (ChronoAI Pte Ltd,
Singapore) and Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd,
Singapore), licensed CC BY 4.0.

## Result

For a nonzero real number `b` with rational `b²`, some finite simple graph
has independence root `ib` if and only if `b²=1/n` for a positive integer `n`.
The graph `G_n` defined in the note has order `108n²`, independence number four,
and polynomial

`I(G_n,x)=(1+nx²)(1+108n²x+81n³x²)`.

Its companion `J_n` satisfies

`I(J_n,x)=1+(1+nx²)(108n²x+81n³x²)`.

Joining `J_n` to a graph that already has the specified roots preserves those
roots and gives connectedness. This yields every independence number at least
four and induced connected supergraphs of arbitrary finite graphs.
Bencs's tree-transfer theorem gives infinitely many trees for each pair
`±i/√n`. The note also gives a smaller 128-vertex witness for `n=2`.

## Contents and build

- `note.tex`: complete mathematical argument, source-coverage table and bibliography.
- `metadata.json`: title, abstract, creator order, affiliations, license and statement link.
- `verify.py`: standard-library Python 3 exact finite checker.
- `verification.json`: deterministic output of that checker.

Build using **Tectonic 0.17.0**:

```sh
tectonic note.tex
```

Alternatively run `pdflatex note.tex` twice with a standard LaTeX distribution
including Latin Modern, AMS, geometry, booktabs, longtable and hyperref.
The bibliography is embedded in the source, so BibTeX is unnecessary.

Check the finite data with Python 3.10 or later:

```sh
python3 verify.py > verification-rebuilt.json
cmp verification.json verification-rebuilt.json
```

## Finite coverage

All calculations use unbounded integers and exact rational fractions.
Each graph is represented by its actual symmetric adjacency bit masks.
The independent-subset enumeration starts at the empty set; each recursive
extension chooses the least available vertex and retains later nonneighbors.
Every independent subset has a unique increasing ordering, so every subset
occurs exactly once and the zero tail is exhausted, rather than truncated.

The recorded instances comprise:

| Family | Parameters |
| --- | --- |
| 128-vertex witness `W` | All 771 independent subsets; coefficients `[1,128,130,256,256]`; 7,998 edges |
| Clique substitution and disjoint padding of `W` | Clique size 1–3; 0–2 isolated vertices |
| General witness `G_n` | `n=1,2,3,4` |
| Companion `J_n` | `n=1,2,3` |
| Connected graph `(G_n disjoint-union E_(a-4)) + J_n` | `n=1,2,3`; `a=4,5,6,7` |
| Connected induced supergraph `(G_n disjoint-union H) + J_n` | `n=1,2,3`; `H` is the three-vertex path, triangle, or edgeless two-vertex graph |

For each instance, the checker compares the enumerated coefficients with the
claimed polynomial and tests connectedness. The induced-supergraph cases
also compare all adjacency entries on the retained copy of `H`.
A root remainder records the constant and linear coefficients after reduction
by `z²=-1/n`. For `G_n` and the connected extensions it is `["0","0"]`;
for `J_n` it is `["1","0"]`. For the clique-scaled witness the denominator
is `2m²`. The infinite families and tree assertions follow from the written
proofs, rather than the finite ranges.

## Lean statement coverage

The exact source is
[IrrationalIndependenceRoot.lean at commit 1f6fb1ff47df504e8dce0cd5cda2403a7aaa622e](https://github.com/the-omega-institute/trureturing/blob/1f6fb1ff47df504e8dce0cd5cda2403a7aaa622e/D5/S3/StatisticalMechanics/HardCore/IrrationalIndependenceRoot.lean).

In namespace `D5.S3.StatisticalMechanics.HardCore.IrrationalIndependenceRoot`:

- `native_polynomial` states the exact factorization, degree and complete independent-set count sequence for `W`.
- `result` states the existence of a finite graph with an irrational imaginary independence root, using `W` and `b=1/√2`.

The all-`n` classification, connected completions, induced embeddings and tree
consequences have written proofs in the note. They are different statements
from those two declarations.

## Scientific sources

1. J. I. Brown and B. Cameron, *A note on purely imaginary independence roots*,
   Discrete Mathematics 343 (2020), 112113.
   DOI: https://doi.org/10.1016/j.disc.2020.112113.
   Exact posing version: https://arxiv.org/abs/2001.08881v2,
   Question 2, printed p. 11; Proposition 2.9, p. 8.
2. F. Bencs, *On trees with real-rooted independence polynomial*,
   Discrete Mathematics 341 (2018), 3321–3330.
   DOI: https://doi.org/10.1016/j.disc.2018.06.033.
   Tree transfer: https://arxiv.org/abs/1703.05409v1, Proposition 2.7(1).
3. B. R. K. Cameron, *On the roots of independence polynomials*, Ph.D. thesis,
   Dalhousie University, March 2019, Conjecture 6.2.4, printed p. 91.
   https://dalspace.library.dal.ca/server/api/core/bitstreams/c903bf10-142c-4ffe-965a-1927ad52197a/content.
4. J. I. Brown, C. A. Hickman and R. J. Nowakowski, *On the location of roots
   of independence polynomials*, Journal of Algebraic Combinatorics 19 (2004),
   273–282, Theorem 1. https://doi.org/10.1023/B:JACO.0000030703.39946.70.
5. B. Cameron, *Graph polynomials*, undated institutional questions page,
   fourth question, accessed November 19, 2026.
   https://www.smcs.upei.ca/~brcameron/graphpolys.html.

The fourth website question asks about imaginary parts of modulus greater
than one. The note rules out the rational-square subclass, not the full
question; possible imaginary parts with irrational square remain outside
the classification.
