from workers import asgi
from api import app

Default = asgi.entrypoint(app)
