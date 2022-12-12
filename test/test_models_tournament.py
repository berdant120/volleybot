from models.tournament import Tournament


def test_init():
    t = Tournament('abc', ['a', 'b', 'c', 'd', 'e'], None)

    assert t.name == 'abc'
    assert len(t.teams) == 2


def test_create_teams():
    t = Tournament('name', [1, 2, 3, 4, 5, 6, 7, 8, 9], 3, 'shname', ['a', 'b', 'c'])

    res1 = t.teams
    res2 = t._create_teams(3, ['a', 'b', 'c'])

    assert [len(x.players) for x in res1] == [3, 3, 3]
    assert [x.name for x in res1] == ['a', 'b', 'c']

    assert res1[0].players != res2[0].players
