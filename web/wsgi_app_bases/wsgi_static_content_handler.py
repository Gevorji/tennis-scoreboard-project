import logging
import mimetypes
import os
import posixpath
import re
import urllib.parse
from http import HTTPStatus

from web.apploggers import APP_LOGGER_NAME
from web.wsgi_app_bases.wsgi_application_base import ResponseProcessingError
from web.wsgi_app_bases.wsgi_middleware_base import WSGIMiddleware


class WSGIStaticContentHandler(WSGIMiddleware):
    _logger = logging.getLogger(APP_LOGGER_NAME + '.static_content_handler')
    _logger.setLevel('DEBUG')
    _static_name_patterns = [
        re.compile(p) for p in ['.+\\.css', '.+\\.png', '.+\\.jpeg']
    ]

    def __init__(self, *args, directory=None, **kwargs):
        self._directory = directory or os.path.join(os.path.dirname(__file__))
        super().__init__(*args,**kwargs)

    def run_underlying_app(self, env, start_response):
        path = self.translate_path(env['PATH_INFO'])
        filename = os.path.basename(path)

        if self._is_static_content(filename):
            self._logger.debug('Static content request')
            env['wsgi.file_path'] = path
            return self.doGET(env, start_response)

        else:
            return self.underlying_layer(env, start_response)

    def doGET(self, env, start_response):
        path = env['wsgi.file_path']
        self._logger.debug(f'Requested file {path}')
        headers = []
        try:
            with open(path, 'rb') as f:
                mt = mimetypes.guess_type(path)[0] or 'application/octet-stream'
                headers.append(('Content-type', mt))
                headers.append(('Content-length', str(os.stat(path).st_size)))
                start_response(HTTPStatus.OK, headers)
                self._logger.debug('Starting giveaway')
                yield from f
        except OSError:
            raise ResponseProcessingError(HTTPStatus.NOT_FOUND, 'Content not found')

    def _is_static_content(self, filename: str):
        return True if list(filter(None, (re.match(p, filename) for p in self._static_name_patterns))) else False

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = self._directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

