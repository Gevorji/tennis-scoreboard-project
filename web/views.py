import os.path
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlsplit, urlencode, parse_qs

from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import Player, Match
from web.tools.project_dir import PROJECT_NAME, PROJECT_DIRECTORY
from web.tools.viewstools import View, ViewHolder

view_holder = ViewHolder()


def populate_view_holder(views_dict):
    for _id, view_obj in views_dict.items():
        view_holder.add_view(_id, view_obj)


env = Environment(
    loader=FileSystemLoader(os.path.join(PROJECT_DIRECTORY, Path('web/static_content/layout/templates'))),
    autoescape=select_autoescape(),
    lstrip_blocks=True,
    trim_blocks=True
)


def http_status_enum_to_string(status: HTTPStatus):
    return f'{status.value} {status.phrase}'


def html_match_score(request_data: dict, match: Match):
    winner = match.match_score['winner']
    if not winner:
        tmpl = env.get_template('match-score.jinja')
    else:
        tmpl = env.get_template('winner-page.jinja')
        winner = {1: match.player1.name, 2: match.player2.name}[winner]
    response_data = dict(
        score=match.match_score, match_id=str(match.match_id),
        p1_name=match.player1.name, p2_name=match.player2.name,
        winner=winner
    )
    return tmpl.render(
        request_data=request_data, response_data=response_data
    )


def html_error_page(request_data: dict, response_data: dict):
    tmpl = env.get_template('error-page.jinja')
    return tmpl.render(request_data=request_data, response_data=response_data)


def html_matches_page(request_data: dict, matches):
    tmpl = env.get_template('matches.jinja')
    qs = parse_qs(request_data.get('QUERY_STRING'))
    query_components = {k: v for k, v in qs.items() if k != 'page'}
    pages_link_prefix = '/matches?' + urlencode({k: v[0] for k, v in query_components.items()})
    if len(query_components) != 0:
        pages_link_prefix += '&'
    response_data = dict(matches=matches, pages_link_prefix=pages_link_prefix)
    return tmpl.render(request_data=request_data, response_data=response_data)


def html_new_match(request_data: dict, data):
    tmpl = env.get_template('new_match.jinja')
    response_data = dict(data=data)
    return tmpl.render(request_data=request_data, response_data=response_data)


def html_index(request_data: dict, data):
    tmpl = env.get_template('index.jinja')
    response_data = dict(data=data)
    return tmpl.render(request_data=request_data, response_data=response_data)


views = {
    '/match_score': View(html_match_score, 'text/html'),
    'error-page': View(html_error_page, 'text/html'),
    '/matches': View(html_matches_page, 'text/html'),
    '/new_match': View(html_new_match, 'text/html'),
    '/': View(html_index, 'text/html')
}

populate_view_holder(views)
