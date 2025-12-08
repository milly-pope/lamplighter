from .core import build_ball, m_at_factory, apply_word


def run_tests():
    print('Running lamplighter tests...')
    # L2 sanity check pattern=[2], gens a,t,T
    gens = [
        {'name': 'a', 'word': [{'toggle': {'offset': 0, 'delta': 1}}]},
        {'name': 't', 'word': [{'move': 1}]},
        {'name': 'T', 'word': [{'move': -1}]},
    ]
    expected = {0: (1, 0), 1: (4, 3), 2: (10, 12), 3: (22, 30), 4: (44, 66)}
    for n in range(0, 5):
        V, E, dist, labels = build_ball(n, gens, block_pattern=[2], symmetrize=False)
        expV, expE = expected[n]
        print(f'n={n}: |V|={len(V)} expected={expV}, |E|={len(E)} expected={expE}')
        assert len(V) == expV, f"V size mismatch for n={n}"
        assert len(E) == expE, f"E size mismatch for n={n}"

    # Level-1 neighbors
    V, E, dist, labels = build_ball(1, gens, block_pattern=[2], symmetrize=False)
    root = V[0]
    # neighbors should include t, T, a
    names = [labels[e[2]] for e in E if e[0] == 0]
    assert 't' in names and 'T' in names and 'a' in names

    # restricted subgroup pattern [2,2] with s=+2
    gens2 = [
        {'name': 'a', 'word': [{'toggle': {'offset': 0, 'delta': 1}}]},
        {'name': 'b', 'word': [{'toggle': {'offset': 1, 'delta': 1}}]},
        {'name': 's', 'word': [{'move': 2}]},
        {'name': 'S', 'word': [{'move': -2}]},
    ]
    V2, E2, dist2, labels2 = build_ball(1, gens2, block_pattern=[2,2], symmetrize=False)
    names2 = [labels2[e[2]] for e in E2 if e[0] == 0]
    assert set(names2) == {'a', 'b', 's', 'S'}

    # check toggles order-2
    # apply 'b' 4 times at same site yields identity for mod 4
    gens34 = [
        {'name': 'b', 'word': [{'toggle': {'offset': 1, 'delta': 1}}]},
    ]
    # start p=0
    m_at = m_at_factory([2,4])
    p = 0
    tape = {}
    # apply b four times
    word = gens34[0]['word']
    for _ in range(4):
        p, tape = apply_word(word, p, tape, m_at)
    assert tape == {}, 'b^4 should be identity on empty tape for mod 4'

    print('All tests passed.')


if __name__ == '__main__':
    run_tests()
