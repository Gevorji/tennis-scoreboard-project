import logging
import os.path
import sys
import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Callable

import services
import services.errors
from web import apploggers
from web.tools.project_dir import PROJECT_DIRECTORY
from web.views import view_holder
from web.wsgi_app_bases.wsgi_application_base import WSGIApplication, ResponseProcessingError
from web.wsgi_app_bases.wsgi_static_content_handler import WSGIStaticContentHandler
from web.wsgi_view_layer import TennisScoreboardViewLayer


class TennisScoreboardWsgiApp(WSGIApplication):
    _logger = logging.getLogger(apploggers.APP_LOGGER_NAME)

    def __call__(self, env, start_response):
        self._logger.debug(
            '=Request arrived at {}=\nEnvironment:{}'
            .format(env['SCRIPT_NAME'], '\n\t'.join(str(itm) for itm in env.items()))
        )
        self._logger.info(
            f'Starting response (current handler: for {env["SCRIPT_NAME"]}). Request at {env["PATH_INFO"]}'
        )

        res = super().__call__(env, start_response)

        self._logger.info(f'Finished response (current handler: for {env["SCRIPT_NAME"]})')

        return res

    def doGET(self):
        self.resp_ctxt.own_start_response(HTTPStatus.OK, ())

        yield

    def _delegate_wsgi_call(self, env: dict, start_response: Callable):
        self._logger.debug(f'Delegating call to {env["PATH_INFO"]}')

        return super()._delegate_wsgi_call(env, start_response)

    def do_error_response(self, e):
        self._logger.error(msg='', exc_info=sys.exc_info())
        return super().do_error_response(e)

    def set_logging_level(self, level):
        self._logger.setLevel(level)

    def switch_to_file_logging(self):
        self._logger = apploggers.APP_LOGGER_NAME_FOR_REMOTE_HOST
        apploggers.make_log_file_dir()

    def fetch_match(self, ident: uuid.UUID):
        match = services.DataStorageService.get_match_by_uuid(ident)
        if not match:
            raise ResponseProcessingError(HTTPStatus.NOT_FOUND, f'No match with id {ident.hex}')
        return match


core_app = TennisScoreboardWsgiApp()

static_content_handler = WSGIStaticContentHandler(
    core_app,
    directory=os.path.join(PROJECT_DIRECTORY, Path('web/static_content'))
)

app = TennisScoreboardViewLayer(static_content_handler, view_holder)


@core_app.at_route('/match_score', endpoint=True)
class MatchScoreHandler(TennisScoreboardWsgiApp):
    # TODO: add tiebreak and deuce indication to a score page
    # TODO: add headers for sets, games, current score to a score page

    def doGET(self):
        start_response = self.resp_ctxt.own_start_response
        ident = self._extract_uuid()
        match = self.fetch_match(ident)

        start_response(HTTPStatus.OK, ())
        yield match

    def doPOST(self):
        start_response = self.resp_ctxt.own_start_response
        env = self.resp_ctxt.env
        ident = self._extract_uuid()
        match = self.fetch_match(ident)

        pw = self._parse_qs(env, required_fields=('point_winner',))['point_winner']

        services.MatchScoreCalculationService.calculate(match.match_score, pw)
        services.DataStorageService.update_match_score(match.match_id, match.match_score)

        if match.match_score.get('winner'):
            match.winner_id = {1: match.player1_id, 2: match.player2_id}[match.match_score['winner']]
            services.DataStorageService.put_match(match)

        start_response(HTTPStatus.OK, ())
        yield match

    def _extract_uuid(self):
        env = self.resp_ctxt.env
        qs = self._parse_qs_from_url(env, required_fields=('uuid',))
        return uuid.UUID(hex=qs['uuid'])


@core_app.at_route('/matches', endpoint=True)
class MatchesHandler(TennisScoreboardWsgiApp):
    # TODO: make winner indication by laying out a start emoji to the left of winner name
    # TODO: make limit pages links layout (5-10 links)

    def doGET(self):
        env = self.resp_ctxt.env
        start_response = self.resp_ctxt.own_start_response
        qs = self._parse_qs_from_url(env)
        pl_name_filter, ongoing, finished = qs.get('player_name_filter'), bool(qs.get('ongoing')), bool(
            qs.get('finished'))

        allowed_params = set(['player_name_filter', 'ongoing', 'finished', 'page'])
        not_allowed_params = list(filter(lambda k: k not in allowed_params, qs.keys()))
        self._logger.debug(not_allowed_params)

        if not_allowed_params:
            raise ResponseProcessingError(
                HTTPStatus.BAD_REQUEST, f'Query parameters {", ".join(not_allowed_params)} are not allowed for that API'
            )

        n_rows = services.DataStorageService.count_matches(pl_name_filter, ongoing=ongoing, finished=finished)
        if n_rows == 0:
            start_response(HTTPStatus.OK, ())
            yield {'data': [], 'pages': [], 'active_page': None}
        query_boundaries = self.break_row_nums_on_pages(n_rows, 5)

        page_no = qs.get('page')
        if page_no is None:
            page_no = 1
        else:
            try:
                page_no = int(page_no)
            except ValueError:
                raise ResponseProcessingError(HTTPStatus.BAD_REQUEST, 'Wrong page number url-encoding: must be numeric')
            if page_no <= 0:
                page_no = 1
            elif page_no > len(query_boundaries):
                page_no = len(query_boundaries)

        objects_list = services.DataStorageService.get_matches_in_creation_ord(
            player_name_filter=pl_name_filter,
            slboundaries=query_boundaries[page_no - 1],
            finished=finished,
            ongoing=ongoing
        )

        start_response(HTTPStatus.OK, ())
        yield {
            'data': objects_list,
            'pages': query_boundaries,
            'active_page': page_no,
            'players_names': services.DataStorageService.get_all_players_names()
        }

    @staticmethod
    def break_row_nums_on_pages(n_rows: int, page_size: int):
        end_breakpoints = list(range(page_size, n_rows + 1, page_size))
        if n_rows % page_size != 0:
            end_breakpoints.append(n_rows)
        start_breakpoints = range(1, n_rows + 1, page_size)
        return tuple(zip(start_breakpoints, end_breakpoints))


@core_app.at_route('/new_match')
class NewMatchHandler(TennisScoreboardWsgiApp):

    def doGET(self):
        self.resp_ctxt.own_start_response(HTTPStatus.OK, ())

        yield {}

    def doPOST(self):
        env = self.resp_ctxt.env
        start_response = self.resp_ctxt.own_start_response

        qd = self._parse_qs(env, required_fields=('player1_name', 'player2_name'))

        p1_name, p2_name = qd['player1_name'], qd['player2_name']

        p1 = services.DataStorageService.get_player_by_name(p1_name)
        p2 = services.DataStorageService.get_player_by_name(p2_name)

        try:
            if not p1:
                p1 = services.PlayerInitializationService.create_new_player(p1_name)
                services.DataStorageService.put_player(p1)
            if not p2:
                p2 = services.PlayerInitializationService.create_new_player(p2_name)
                services.DataStorageService.put_player(p2)
        except services.errors.ApplicationError as e:
            raise ResponseProcessingError(HTTPStatus.BAD_REQUEST, e.args[0]) from e

        new_match = services.MatchInitializationService.create_new_match(p1, p2)

        services.DataStorageService.put_match(new_match)

        start_response(HTTPStatus.SEE_OTHER, (('Location', f'/match_score?uuid={new_match.match_id.hex}'),))

        yield {}
