import sys
import os.path

from dotenv import dotenv_values


project_dir = os.path.abspath(os.path.join(f'{__file__}', '..\\..\\'))

sys.path.append(project_dir)
os.environ.update(dotenv_values(os.path.join(project_dir, r"services\tests\.env")))

from waitress import serve

import services
from web.wsgi_application import app

app.set_logging_level('DEBUG')
services.DataStorageService._sa_engine.echo = True

if __name__ == '__main__':
    serve(app, host='localhost', port=8000, expose_tracebacks=True, threads=1)