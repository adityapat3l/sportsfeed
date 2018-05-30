from nfl.gamedetails import GameInfo
from nfl.api import NflApi
import json
import pymysql
import nfl.config
import pickle

def team_info(team):
    team_id = team['ID']
    team_name = team['Name']
    team_abbr = team.get('Abbreviation', None)
    team_city = team['City']

    return team_id, team_name, team_abbr, team_city


def game_info(game):
    game_id = int(game['id'])
    game_date = game['date']
    game_time = game['time']
    game_location = game['location']
    game_delayed_reason = game.get('delayedOrPostponedReason', None)

    return game_id, game_date, game_time, game_location, game_delayed_reason


def get_game_id_by_date(full_schedule):
    all_games_on_date = {}

    for game in full_schedule['fullgameschedule']['gameentry']:
        if game['date'] not in all_games_on_date:
            all_games_on_date[game['date']] = [game['id']]
        else:
            all_games_on_date[game['date']].append(game['id'])

    return all_games_on_date


def list_distinct_team_abbrv(full_schedule):
    teams_abbrv = []
    for game in full_schedule['fullgameschedule']['gameentry']:
        if game['homeTeam']['Abbreviation'] not in teams_abbrv:
            teams_abbrv.append(game['homeTeam']['Abbreviation'])

    return teams_abbrv


def compile_season_details_by_team(season_name, full_schedule):
    team_abbrv = list_distinct_team_abbrv(full_schedule)

    team_logs = []
    for team in team_abbrv:
        dict_team_info = {}
        team_api_data = NflApi(season_name).team_logs(team)
        dict_team_info['team'] = team
        dict_team_info['details'] = team_api_data
        team_logs.append(dict_team_info)
    #
    # with open('outfile', 'wb') as fp:
    #     pickle.dump(team_logs, fp)

    # with open('outfile', 'rb') as fp:
    #     team_logs = pickle.load(fp)

    game_instances_all = {}

    for team_season_details in team_logs:
        team_ab = team_season_details['team']
        game = team_season_details['details']['teamgamelogs']
        for _ in game:
            for game_details in game['gamelogs']:
                home_args = team_info(game_details['game']['homeTeam'])
                away_args = team_info(game_details['game']['awayTeam'])
                args = (*away_args, *home_args)
                game_id, game_date, game_time, game_location, game_delayed_reason = game_info(game_details["game"])

                score_home = game_details['stats']['PointsFor']['#text']
                score_away = game_details['stats']['PointsAgainst']['#text']

                game_instance = GameInfo(season_name,
                                         game_id,
                                         game_date,
                                         game_time,
                                         game_location,
                                         game_delayed_reason,
                                         score_home,
                                         score_away,
                                         *args)

                game_instances_all[game_instance.game_id] = game_instance

    return game_instances_all



    
def compile_season_details_by_date(season_name, full_schedule):

    # List of game_ids on given game_date
    dict_game_id_by_date = get_game_id_by_date(full_schedule)

    game_instances_all = {}

    for date in dict_game_id_by_date:
        game_details_for_date = NflApi(season_name).all_games_on_date(date)
        for game in full_schedule['fullgameschedule']['gameentry']:
            if game['date'] == date:
                home_args = team_info(game['homeTeam'])
                away_args = team_info(game['awayTeam'])
                args = (*away_args, *home_args)
                game_id, game_date, game_time, game_location, game_delayed_reason = game_info(game)

                score_home, score_away = NflApi(season_name).game_score(game_id, game_date, games_on_date
                                                                        =game_details_for_date)

                game_instance = GameInfo(season_name,
                                         game_id,
                                         game_date,
                                         game_time,
                                         game_location,
                                         game_delayed_reason,
                                         score_home,
                                         score_away,
                                         *args)
                game_instances_all[game_instance.game_id] = game_instance

                print(game_instance.game_id, ":", game_instance.winner())
                print(game_instance.winning_team)
            else:
                pass

    return game_instances_all


def add_game_information_to_db(season_name):
    full_schedule = NflApi(season_name).full_schedule()

    pull_method = input('How to input data(Date, Team)?: ').lower()
    while pull_method not in ["team", "date"]:
        pull_method = input('Invalid Input. Please choose either of the following options-(Date or Team): ').lower()

    if pull_method == 'date':
        game_instances = compile_season_details_by_date(season_name, full_schedule)
    else:
        game_instances = compile_season_details_by_team(season_name, full_schedule)

    for id in game_instances:
        pass


    mysql_conn = pymysql.connect(host=config.mysql_host, port=config.mysql_port, user=config.mysql_user,
                                 passwd=config.mysql_password, db=config.mysql_dbname)
    mysql_cur = mysql_conn.cursor()
    query = ''' '''

    mysql_cur.execute(query)
    mysql_cur.commit()
    mysql_cur.close()
    
    # return game_instances


# season_name = input('Please input the name of the season: ')
add_game_information_to_db('2017-regular')
# compile_season_details_by_team()
