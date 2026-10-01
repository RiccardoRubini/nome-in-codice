import hashlib
import json
import secrets
from typing import Literal
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from game import create_game, act, view, RuleError
from store import LocalStore, D1Store, Conflict

app = FastAPI(title='Nome in codice', docs_url=None, redoc_url=None, openapi_url=None)
_local_store = None


class Team(BaseModel):
    name: str = Field(min_length=1, max_length=24)
    color: str
    cards: int = Field(ge=1, le=30, strict=True)


class Setup(BaseModel):
    teams: list[Team] = Field(min_length=2, max_length=5)
    size: Literal[25, 30] = 25
    civilians: int = Field(ge=0, le=30, strict=True)
    assassins: int = Field(ge=0, le=28, strict=True)
    spy_code: str = Field(default='', max_length=80)


class Command(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal['clue', 'pass', 'reveal']
    revision: int = Field(ge=0, strict=True)
    card: int | None = None
    word: str = Field(default='', max_length=32)
    number: int = Field(default=1, ge=0, le=30, strict=True)


def digest(code):
    return hashlib.sha256(code.encode()).hexdigest()


def repository(request):
    global _local_store
    if 'env' in request.scope:
        return D1Store(request.scope['env'].DB)
    if _local_store is None:
        _local_store = LocalStore()
    return _local_store


@app.middleware('http')
async def headers(request, call_next):
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


async def load(request, code):
    if len(code) != 6 or not code.isalnum():
        raise HTTPException(404, 'Partita non trovata. Controlla il codice di 6 caratteri.')
    row = await repository(request).get(code.upper())
    if row is None:
        raise HTTPException(404, 'Partita non trovata. Controlla il codice di 6 caratteri.')
    return row, json.loads(row['state'])


def authorize(request, stored, header):
    supplied = request.headers.get(header, '')
    if not supplied or not secrets.compare_digest(digest(supplied), stored):
        raise HTTPException(403, 'Codice di accesso non valido.')


@app.get('/api/health')
async def health():
    return {'ok': True}


@app.post('/api/games', status_code=201)
async def new_game(config: Setup, request: Request):
    db = repository(request)
    code = config.spy_code.strip()
    if config.spy_code and len(code) < 8:
        raise HTTPException(422, 'Il codice Spymaster deve avere almeno 8 caratteri.')
    host_key = secrets.token_urlsafe(32)
    words = await db.words()
    for _ in range(5):
        try:
            game = create_game(config.model_dump(), words)
            await db.insert(game, digest(host_key), digest(code) if code else '')
            return {'game': view(game), 'host_key': host_key, 'spy_code': code}
        except RuleError as exc:
            raise HTTPException(422, str(exc)) from exc
        except Conflict:
            continue
    raise HTTPException(503, 'Impossibile creare la partita. Riprova tra un momento.')


@app.get('/api/games/{code}')
async def get_game(code: str, request: Request):
    _, game = await load(request, code)
    return view(game)


@app.get('/api/games/{code}/spy')
async def spy_game(code: str, request: Request):
    row, game = await load(request, code)
    if row['spy_hash']:
        authorize(request, row['spy_hash'], 'X-Spy-Code')
    return view(game, spy=True)


@app.get('/api/games/{code}/control')
async def control_game(code: str, request: Request):
    row, game = await load(request, code)
    authorize(request, row['host_hash'], 'X-Host-Key')
    return view(game)


@app.post('/api/games/{code}/actions')
async def action(code: str, command: Command, request: Request):
    row, game = await load(request, code)
    authorize(request, row['host_hash'], 'X-Host-Key')
    if game['revision'] != command.revision:
        raise HTTPException(409, 'Il tabellone è cambiato. Controllalo e riprova.')
    try:
        updated = act(game, command.model_dump())
        await repository(request).update(updated, command.revision)
    except RuleError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Conflict as exc:
        raise HTTPException(409, 'Un altro dispositivo ha aggiornato la partita. Riprova.') from exc
    return view(updated)
