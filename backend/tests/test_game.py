import copy
import pytest
from game import create_game, act, view, remaining, RuleError, COLORS


def config(n=2, size=25):
    counts=[(size-1)//n+(i<(size-1)%n) for i in range(n)]
    return dict(size=size,teams=[dict(name=f'Team {i}',color=COLORS[i],cards=counts[i]) for i in range(n)],civilians=0,assassins=1)


def game(n=2, size=25):
    return create_game(config(n,size),[f'PAROLA{i}' for i in range(100)])


def clue(g, number=1):
    return act(g,dict(kind='clue',word='Indizio',number=number))


@pytest.mark.parametrize('n',[2,3,4,5])
@pytest.mark.parametrize('size',[25,30])
def test_all_supported_boards(n,size):
    g=game(n,size)
    assert len(g['cards'])==size
    assert len({c['word'] for c in g['cards']})==size
    assert sum(remaining(g,i) for i in range(n))==size-1
    assert all('owner' not in c for c in view(g)['cards'])
    assert all('owner' in c for c in view(g,True)['cards'])


def test_wrong_card_ends_turn_and_counts_for_opponent():
    g=clue(game(3));active=g['active'];opponent=(active+1)%3
    index=next(i for i,c in enumerate(g['cards']) if c['owner']==opponent)
    before=remaining(g,opponent)
    result=act(g,dict(kind='reveal',card=index))
    assert result['active']==opponent and result['clue'] is None
    assert remaining(result,opponent)==before-1
    assert not g['cards'][index]['revealed']


def test_assassin_eliminates_and_neutralizes_unrevealed_cards():
    g=clue(game(3));team=g['active']
    i=next(i for i,c in enumerate(g['cards']) if c['owner']=='assassin')
    result=act(g,dict(kind='reveal',card=i))
    assert result['teams'][team]['eliminated']
    assert result['status']=='playing' and result['active']!=team
    secret=view(result,True)
    assert all(secret['cards'][i]['owner']=='civilian' for i,c in enumerate(g['cards']) if c['owner']==team)
    assert all('owner' not in c for c in view(result)['cards'] if not c['revealed'])


def test_last_team_wins_on_assassin():
    g=clue(game());i=next(i for i,c in enumerate(g['cards']) if c['owner']=='assassin')
    result=act(g,dict(kind='reveal',card=i))
    assert result['status']=='finished' and result['winner']!=g['active']


def test_guess_limit_and_zero():
    for number in (0,1):
        g=clue(game(),number);team=g['active']
        for _ in range(2):
            i=next(i for i,c in enumerate(g['cards']) if c['owner']==team and not c['revealed'])
            g=act(g,dict(kind='reveal',card=i))
        assert (g['active']==team)==(number==0)


def test_opponent_can_win_on_wrong_reveal():
    g=clue(game());other=1-g['active']
    cards=[i for i,c in enumerate(g['cards']) if c['owner']==other]
    for i in cards[:-1]:g['cards'][i]['revealed']=True
    result=act(g,dict(kind='reveal',card=cards[-1]))
    assert result['winner']==other


def test_invalid_actions():
    g=game()
    with pytest.raises(RuleError):act(g,dict(kind='reveal',card=0))
    g=clue(g)
    with pytest.raises(RuleError):clue(g)
    with pytest.raises(RuleError):act(g,dict(kind='reveal',card=-1))
    g['cards'][0]['revealed']=True
    with pytest.raises(RuleError):act(g,dict(kind='reveal',card=0))


def test_invalid_setup():
    c=config();c['civilians']=1
    with pytest.raises(RuleError):create_game(c,['word']*50)
    c=config();c['teams'][1]['color']=c['teams'][0]['color']
    with pytest.raises(RuleError):create_game(c,[str(i) for i in range(50)])
