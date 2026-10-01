"""D1 repository with atomic revision checks; SQLite adapter only for local development."""
import json
import os
import tempfile
from pathlib import Path


class Conflict(Exception):
    pass


class LocalStore:
    def __init__(self, path=None):
        import sqlite3
        self.db = sqlite3.connect(path or os.getenv('GAME_DB', str(Path(tempfile.gettempdir()) / 'nome-in-codice.sqlite')))
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA busy_timeout=5000')
        for migration in sorted((Path(__file__).parents[2] / 'migrations').glob('*.sql')):
            self.db.executescript(migration.read_text())

    async def words(self):
        return [r[0] for r in self.db.execute('SELECT word FROM words ORDER BY word')]

    async def get(self, code):
        row = self.db.execute('SELECT * FROM games WHERE id=?', (code,)).fetchone()
        return dict(row) if row else None

    async def insert(self, game, host_hash, spy_hash):
        import sqlite3
        try:
            self.db.execute('INSERT INTO games(id,state,revision,host_hash,spy_hash) VALUES(?,?,?,?,?)', (game['id'], json.dumps(game), 0, host_hash, spy_hash))
            self.db.commit()
        except sqlite3.IntegrityError as exc:
            self.db.rollback()
            raise Conflict from exc

    async def update(self, game, revision):
        result = self.db.execute('UPDATE games SET state=?,revision=? WHERE id=? AND revision=?', (json.dumps(game), game['revision'], game['id'], revision))
        self.db.commit()
        if result.rowcount != 1:
            raise Conflict


class D1Store:
    def __init__(self, db):
        self.db = db

    async def words(self):
        result = await self.db.prepare('SELECT word FROM words ORDER BY word').all()
        return [r.word for r in result.results]

    async def get(self, code):
        row = await self.db.prepare('SELECT * FROM games WHERE id=?').bind(code).first()
        if row is None:
            return None
        return {key: getattr(row, key) for key in ('id', 'state', 'revision', 'host_hash', 'spy_hash')}

    async def insert(self, game, host_hash, spy_hash):
        result = await self.db.prepare('INSERT OR IGNORE INTO games(id,state,revision,host_hash,spy_hash) VALUES(?,?,?,?,?)').bind(game['id'], json.dumps(game), 0, host_hash, spy_hash).run()
        if result.meta.changes != 1:
            raise Conflict

    async def update(self, game, revision):
        result = await self.db.prepare('UPDATE games SET state=?,revision=? WHERE id=? AND revision=?').bind(json.dumps(game), game['revision'], game['id'], revision).run()
        if result.meta.changes != 1:
            raise Conflict
