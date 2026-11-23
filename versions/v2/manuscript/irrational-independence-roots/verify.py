import hashlib
import json
from fractions import Fraction


def polynomial_product(left, right):
    product = [0] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            product[left_degree + right_degree] += left_value * right_value
    return product


def clique(order):
    return [((1 << order) - 1) ^ (1 << vertex) for vertex in range(order)]


def combine(graphs, joined=False):
    order = sum(len(graph) for graph in graphs)
    all_vertices = (1 << order) - 1
    adjacency = []
    offset = 0
    for graph in graphs:
        block = ((1 << len(graph)) - 1) << offset
        outside = all_vertices ^ block if joined else 0
        adjacency.extend((neighbors << offset) | outside for neighbors in graph)
        offset += len(graph)
    return adjacency


def witness_128():
    return combine([combine([clique(4) for _ in range(4)]),
                    combine([[0, 0] for _ in range(34)], joined=True),
                    clique(44)], joined=True)


def substitution(adjacency, multiplier):
    order = len(adjacency) * multiplier
    graph = [0] * order
    for vertex, neighbors in enumerate(adjacency):
        lifted = ((1 << multiplier) - 1) << (vertex * multiplier)
        while neighbors:
            first = neighbors & -neighbors
            neighbors ^= first
            original = first.bit_length() - 1
            lifted |= ((1 << multiplier) - 1) << (original * multiplier)
        for representative in range(multiplier):
            position = vertex * multiplier + representative
            graph[position] = lifted ^ (1 << position)
    return graph


def parameter_graph(parameter, neutral=False):
    pair_size = 81 * parameter * parameter - 54 * parameter
    final_size = 27 * parameter * parameter + 41 * parameter
    return combine([
        combine([clique(3 * parameter) for _ in range(4)]),
        combine([clique(parameter), clique(pair_size + (0 if neutral else 1))]),
        clique(final_size - (0 if neutral else 1)),
    ], joined=True)


def independent_counts(adjacency):
    counts = [0] * (len(adjacency) + 1)

    def extend(candidates, cardinality):
        counts[cardinality] += 1
        while candidates:
            first = candidates & -candidates
            vertex = first.bit_length() - 1
            candidates ^= first
            extend(candidates & ~adjacency[vertex], cardinality + 1)

    extend((1 << len(adjacency)) - 1, 0)
    while len(counts) > 1 and counts[-1] == 0:
        counts.pop()
    return counts


def root_remainder(coefficients, denominator):
    square = Fraction(-1, denominator)
    return [str(sum(Fraction(value) * square ** (degree // 2)
                    for degree, value in enumerate(coefficients)
                    if degree % 2 == parity)) for parity in range(2)]


def connected(adjacency):
    if not adjacency:
        return False
    seen = 1
    frontier = 1
    while frontier:
        first = frontier & -frontier
        frontier ^= first
        newly_seen = adjacency[first.bit_length() - 1] & ~seen
        seen |= newly_seen
        frontier |= newly_seen
    return seen.bit_count() == len(adjacency)


def graph_record(adjacency):
    return {'vertices': len(adjacency),
            'edges': sum(neighbors.bit_count() for neighbors in adjacency) // 2,
            'connected': connected(adjacency),
            'independent_counts': independent_counts(adjacency)}


def run():
    base = witness_128()
    original = graph_record(base)
    assert original == {'vertices': 128, 'edges': 7998, 'connected': True,
                        'independent_counts': [1, 128, 130, 256, 256]}
    assert all(not (neighbors >> vertex) & 1 for vertex, neighbors in enumerate(base))
    assert all(((base[left] >> right) & 1) == ((base[right] >> left) & 1)
               for left in range(128) for right in range(128))
    encoding = bytes((base[left] >> right) & 1
                     for left in range(128) for right in range(left + 1, 128))
    original['adjacency_sha256'] = hashlib.sha256(encoding).hexdigest()
    original['total_independent_sets'] = sum(original['independent_counts'])
    original['root_remainder'] = root_remainder(original['independent_counts'], 2)
    assert original['root_remainder'] == ['0', '0']
    assert polynomial_product([1, 0, 2], [1, 128, 128]) == original['independent_counts']
    old_extensions = []
    for multiplier in range(1, 4):
        for isolates in range(3):
            graph = combine([substitution(base, multiplier), [0] * isolates])
            record = graph_record(graph)
            expected = [value * multiplier ** degree
                        for degree, value in enumerate(original['independent_counts'])]
            for _ in range(isolates):
                expected = polynomial_product(expected, [1, 1])
            assert record['independent_counts'] == expected
            assert record['connected'] == (isolates == 0)
            assert root_remainder(expected, 2 * multiplier * multiplier) == ['0', '0']
            record['root_remainder'] = root_remainder(expected, 2 * multiplier * multiplier)
            old_extensions.append({'clique_size': multiplier, 'isolates': isolates, **record})
    witnesses = []
    neutral_graphs = []
    completions = []
    embeddings = []
    for parameter in range(1, 5):
        witness = parameter_graph(parameter)
        record = graph_record(witness)
        expected = [1, 108 * parameter ** 2, parameter + 81 * parameter ** 3,
                    108 * parameter ** 3, 81 * parameter ** 4]
        assert record['independent_counts'] == expected
        assert record['vertices'] == 108 * parameter ** 2 and record['connected']
        assert polynomial_product([1, 0, parameter],
                                  [1, 108 * parameter ** 2, 81 * parameter ** 3]) == expected
        assert root_remainder(expected, parameter) == ['0', '0']
        record['root_remainder'] = root_remainder(expected, parameter)
        witnesses.append({'n': parameter, **record})
        if parameter > 3:
            continue
        neutral = parameter_graph(parameter, neutral=True)
        neutral_record = graph_record(neutral)
        neutral_expected = expected[:]
        neutral_expected[2] -= parameter
        assert neutral_record['independent_counts'] == neutral_expected
        assert root_remainder(neutral_expected, parameter) == ['1', '0']
        assert neutral_record['vertices'] == 108 * parameter ** 2 and neutral_record['connected']
        neutral_record['root_remainder'] = root_remainder(neutral_expected, parameter)
        neutral_graphs.append({'n': parameter, **neutral_record})
        for isolates in range(4):
            padded = combine([witness, [0] * isolates])
            graph = combine([padded, neutral], joined=True)
            record = graph_record(graph)
            expected_completion = expected[:]
            for _ in range(isolates):
                expected_completion = polynomial_product(expected_completion, [1, 1])
            for degree, value in enumerate(neutral_expected):
                expected_completion[degree] += value
            expected_completion[0] -= 1
            assert record['independent_counts'] == expected_completion
            assert len(expected_completion) - 1 == 4 + isolates and record['connected']
            assert root_remainder(expected_completion, parameter) == ['0', '0']
            record['root_remainder'] = root_remainder(expected_completion, parameter)
            completions.append({'n': parameter, 'independence_number': 4 + isolates, **record})
        for name, inserted in [('path3', [2, 5, 2]), ('triangle', clique(3)),
                               ('edgeless2', [0, 0])]:
            graph = combine([combine([witness, inserted]), neutral], joined=True)
            record = graph_record(graph)
            offset = len(witness)
            mask = (1 << len(inserted)) - 1
            assert [((graph[offset + vertex] >> offset) & mask)
                    for vertex in range(len(inserted))] == inserted
            expected_embedding = polynomial_product(expected, independent_counts(inserted))
            for degree, value in enumerate(neutral_expected):
                expected_embedding[degree] += value
            expected_embedding[0] -= 1
            assert record['independent_counts'] == expected_embedding and record['connected']
            assert root_remainder(expected_embedding, parameter) == ['0', '0']
            record['root_remainder'] = root_remainder(expected_embedding, parameter)
            embeddings.append({'n': parameter, 'induced_graph': name, **record})
    return {'arithmetic': 'unbounded integers and exact rational fractions',
            'root_remainder_convention': 'constant and linear coefficients after z²=-1/n',
            'base_witness': original, 'clique_and_padding_checks': old_extensions,
            'parameter_witnesses': witnesses, 'neutral_graphs': neutral_graphs,
            'connected_completions': completions, 'induced_embeddings': embeddings,
            'scope': 'Exhaustive independent-subset enumeration of each listed graph; '
                     'exact coefficient, connectivity, induced-subgraph and root-remainder checks. '
                     'The all-parameter statements and tree consequences have written proofs.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
