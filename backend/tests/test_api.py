import asyncio
import json
import pytest
from fastapi.testclient import TestClient
import api
from store import LocalStore, Conflict
from game import COLORS


@pytest.fixture
def client(tmp_path):
    # TestClient handles requests in another thread; initialize SQLite there.
    import os
    os.environ['GAME_DB']=str(tmp_path/'test.sqlite')
    api._local_store=None
    with TestClient(api.app) as client:
        yield client
    api._local_store=None


def setup():
    return dict(size=25,teams=[dict(name='Volpe',color=COLORS[0],cards=8),dict(name='Falco',color=COLORS[1],cards=8)],civilians=8,assassins=1,spy_code='segretissimo')


def test_full_api_access_and_revision(client):
    response=client.post('/api/games',json=setup());assert response.status_code==201
    data=response.json();code=data['game']['id'];url=f'/api/games/{code}'
    public=client.get(url)
    assert public.headers['cache-control']=='no-store'
    assert all('owner' not in c for c in public.json()['cards'])
    assert client.get(url+'/spy').status_code==403
    assert client.get(url+'/spy',headers={'X-Spy-Code':'wrong'}).status_code==403
    assert all('owner' in c for c in client.get(url+'/spy',headers={'X-Spy-Code':'segretissimo'}).json()['cards'])
    cmd=dict(kind='clue',revision=0,word='Lontano',number=1)
    assert client.post(url+'/actions',json=cmd).status_code==403
    headers={'X-Host-Key':data['host_key']}
    assert client.post(url+'/actions',json=cmd,headers=headers).status_code==200
    assert client.post(url+'/actions',json=cmd,headers=headers).status_code==409
    assert client.get(url).json()['revision']==1
    assert client.get(url.lower()).status_code==200
    assert client.get('/api/games/AAAAAA').status_code==404


def test_spy_view_opens_without_code_when_unprotected(client):
    config = setup()
    config['spy_code'] = ''
    response = client.post('/api/games', json=config)
    assert response.status_code == 201
    created = response.json()
    assert created['spy_code'] == ''
    code = created['game']['id']
    public = client.get(f'/api/games/{code}').json()
    spy = client.get(f'/api/games/{code}/spy')
    assert spy.status_code == 200
    assert all('owner' not in card for card in public['cards'])
    assert all('owner' in card for card in spy.json()['cards'])


def test_dictionary_and_atomic_compare_and_swap(tmp_path):
    db=LocalStore(str(tmp_path/'store.sqlite'))
    async def scenario():
        words=await db.words();assert len(words)>=500 and len(words)==len(set(words))
        from game import create_game, act
        g=create_game(setup(),words)
        await db.insert(g,'h','s')
        a=act(g,dict(kind='pass'));b=act(g,dict(kind='pass'))
        await db.update(a,0)
        with pytest.raises(Conflict):await db.update(b,0)
        assert json.loads((await db.get(g['id']))['state'])['revision']==1
    asyncio.run(scenario())


def test_invalid_setup_is_rejected(client):
    s=setup();s['civilians']=0
    assert client.post('/api/games',json=s).status_code==422
    s=setup();s['teams'][1]['name']='Volpe'
    assert client.post('/api/games',json=s).status_code==422
    s=setup();s['spy_code']='abc'
    assert client.post('/api/games',json=s).status_code==422
    s=setup();s['spy_code']='        '
    assert client.post('/api/games',json=s).status_code==422
