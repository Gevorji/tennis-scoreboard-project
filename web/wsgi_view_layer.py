from http import HTTPStatus

from web.tools.viewstools import ViewHolder
from web.wsgi_app_bases.wsgi_middleware_base import WSGIMiddleware
from web.views import view_holder, http_status_enum_to_string


class TennisScoreboardViewLayer(WSGIMiddleware):

    def __init__(self, underlying_app, views: ViewHolder):
        self._views = views
        super().__init__(underlying_app)

    def process_data(self, data):
        rc = self.resp_ctxt
        status = rc.headers_set[0]

        if type(data) is bytes:
            return data

        if int(status) < 400:
            v = self._views.get_view(self.resp_ctxt.env['PATH_INFO'], 'text/html')
        else:
            v = self._views.get_view('error-page', 'text/html')
            data = (data, status)

        return v.apply(self.resp_ctxt.env, data).encode()

    def process_status(self, status: HTTPStatus):
        return http_status_enum_to_string(status)

    def modify_headers(self, env, headers):
        headers.append(('Content-type', 'text/html'))

