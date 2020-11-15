# import native Python packages
import json
import random

# import third party packages
from bson.json_util import dumps
from flask import Blueprint, jsonify, make_response, request, url_for
import pandas

# import local stuff
from tarpeydev.db import get_dbmr
from tarpeydev.users import login_required


api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/index/random-quote', methods=['GET'])
def random_quote():
    client = get_dbmr()
    db = client.quotes
    quote_count = db.quotes.estimated_document_count()
    quote_id = str(random.randint(1, quote_count))
    quote = db.quotes.find_one({"_id": quote_id})
    return quote


@api_bp.route('/haveyouseenx/search', methods=['GET'])
def search(search_term=None):
    if search_term is None:
        search_term = request.args.get('query')
    if search_term is None:
        error = "You can't call this URL without a query!"
        return error, 569
    client = get_dbmr()
    db = client.backlogs
    # return all results if no search_term
    if search_term == '':
        results = list(db.annuitydew.find())
    else:
        results = list(db.annuitydew.find(
            {
                '$text': {
                    '$search': search_term
                }
            }
        ))
    if request.path.startswith('/api/'):
        return jsonify(results), 200
    else:
        return results


@api_bp.route('/mildredleague/<int:season>', methods=['GET'])
def season_data(season, api=False):
    client = get_dbmr()
    db = client.mildredleague
    # return all results if no search_term
    data = list(db.games.find({"season": season}))
    if not data:
        return "No data found!", 400
    elif request.path.startswith('/api/') or api is True:
        return jsonify(data), 200
    else:
        return data


@api_bp.route('/mildredleague/all-teams', methods=['GET'])
def all_teams_data(api=False):
    client = get_dbmr()
    db = client.mildredleague
    # return full history of mildredleague teams
    data = list(db.teams.find())
    if not data:
        return "No data found!", 400
    elif request.path.startswith('/api/') or api is True:
        return jsonify(data), 200
    else:
        return data


@api_bp.route('/mildredleague/boxplot/<int:season>/<int:against>', methods=['GET'])
def season_boxplot_transform(season, against):
    # read season and teams data from api
    games_data, response_code = season_data(season=season, api=True)
    teams_data, response_code = all_teams_data(api=True)
    season_df = pandas.DataFrame(games_data.json)
    # normalized score columns for two-week playoff games
    season_df['a_score_norm'] = (
        season_df['a_score'] / (
            season_df['week_e'] - season_df['week_s'] + 1
        )
    )
    season_df['h_score_norm'] = (
        season_df['h_score'] / (
            season_df['week_e'] - season_df['week_s'] + 1
        )
    )
    # we just want unique scores. so let's stack away and home.
    # this code runs to analyze Points For.
    if against == 0:
        score_df = season_df[['a_nick', 'a_score_norm']].rename(
            columns={'a_nick': 'name', 'a_score_norm': 'score'},
        ).append(
            season_df[['h_nick', 'h_score_norm']].rename(
                columns={'h_nick': 'name', 'h_score_norm': 'score'},
            ),
            ignore_index=True,
        )
        title_label = '(Points For)'
    # this code runs to analyze Points Against.
    if against == 1:
        score_df = season_df[['a_nick', 'h_score_norm']].rename(
            columns={'a_nick': 'name', 'h_score_norm': 'score'},
        ).append(
            season_df[['h_nick', 'a_score_norm']].rename(
                columns={'h_nick': 'name', 'a_score_norm': 'score'},
            ),
            ignore_index=True,
        )
        title_label = '(Points Against)'
    # let's sort by playoff rank instead
    # read season file, but we only need nick_name, season, and playoff_rank
    ranking_df = pandas.DataFrame(teams_data.json)[['nick_name', 'season', 'playoff_rank']]
    # merge this (filtered by season) into score_df so we can sort values
    score_df = score_df.merge(
        ranking_df.loc[ranking_df.season == int(season), ['nick_name', 'playoff_rank']],
        left_on=['name'],
        right_on=['nick_name'],
        how='left',
    ).sort_values(
        by='playoff_rank', ascending=True,
    )

    # convert back to json for writing to Mongo
    data = json.loads(score_df.to_json())
    if not data:
        return "No data found!", 400
    elif request.path.startswith('/api/'):
        return jsonify(data), 200
    else:
        return data


@api_bp.route('/users', methods=['POST'])
@login_required
def create():
    return


@api_bp.route('/users/<username>', methods=['GET'])
@login_required
def read(username):
    client = get_dbmr()
    db = client.users
    user = db.users.find_one({"_id": username})
    if user is not None:
        return user.get("_id")
    else:
        return "Error!"


@api_bp.route('/users', methods=['POST', 'PUT'])
@login_required
def update():
    return


@api_bp.route('/users', methods=['GET', 'DELETE'])
@login_required
def delete():
    return
