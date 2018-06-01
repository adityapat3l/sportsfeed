from nfl.gamedetails import GameInfo
from nfl.api import NflApi
from nfl.library import season_ids
import json
import pymysql
import nfl.config as config
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


def get_season_stats(season_name):
    season_stats_unformatted = NflApi(season_name).overall_season_standings()

    season_stats = []

    for record in season_stats_unformatted['overallteamstandings']['teamstandingsentry']:
        stats = dict()
        stats['rank'] = int(record['rank'])
        stats['team_id'] = int(record['team']['ID'])

        for key, value in record['stats'].items():
            try:
                stats[key] = int(value['#text'])
            except ValueError:
                stats[key] = float(value['#text'])

        season_stats.append(stats)

    return season_stats


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


def prepare_game_information(season_name):
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

    season_stats = get_season_stats(season_name)

    champ = 0

    for team_stats in season_stats:
        if team_stats['rank'] == 1:
            champ = team_stats['team_id']

    game_data = []
    season_data = []
    team_data = []

    for instance in game_instances:
        game_id = game_instances[instance].game_id
        season_id = season_ids[game_instances[instance].season_name]
        game_start = game_instances[instance].datetime
        location = game_instances[instance].location
        home_team_id = int(game_instances[instance].id_home_team)
        away_team_id = int(game_instances[instance].id_away_team)
        score_home = int(game_instances[instance].score_home)
        score_away = int(game_instances[instance].score_away)

        season_year = int(game_instances[instance].season_year)
        season_type = game_instances[instance].season_type
        winner = game_instances[instance].winning_team

        home_team_name = game_instances[instance].name_home_team
        home_team_abbr = game_instances[instance].abbr_home_team
        home_team_city = game_instances[instance].city_home_team

        away_team_name = game_instances[instance].name_away_team
        away_team_abbr = game_instances[instance].abbr_away_team
        away_team_city = game_instances[instance].city_away_team



        game_data.append((game_id, season_id, game_start, location, home_team_id, away_team_id, score_home, score_away))

        # Improve this
        season_data.append((season_id, season_year, season_type, champ))

        # Improve this
        team_data.append((home_team_id, home_team_name, home_team_abbr, home_team_city))
        team_data.append((away_team_id, away_team_name, away_team_abbr, away_team_city))

    # f = open('output_game.txt', 'w')
    # f.write(str(game_data))
    # f.close()
    #
    # f = open('output_season.txt', 'w')
    # f.write(str(season_data))
    # f.close()
    #
    # f = open('output_team.txt', 'w')
    # f.write(str(team_data))
    # f.close()

    return game_data, season_data, team_data


def add_to_db(game_data=None, season_data=None, team_data=None):
    mysql_conn = pymysql.connect(host=config.mysql_host, port=config.mysql_port, user=config.mysql_user,
                                 passwd=config.mysql_password)
    mysql_cur = mysql_conn.cursor()
    team_data_query = '''
                insert into nfl.teams (id, name, abbr, city) values {0}
                on duplicate key update id = id; '''.format(str(team_data).strip('[').strip(']'))

    season_data_query = '''insert into nfl.seasons (id, season_year, season_type, champion_team_id) values {0} 
                on duplicate key update id = id; '''.format(str(season_data).strip('[').strip(']'))

    game_data_query = '''insert into nfl.games (id, season_id, game_start, location, home_team_id, away_team_id,
                                  score_home, score_away) values {0}
                                   on duplicate key update id = id;'''.format(str(game_data).strip('[').strip(']'))

    mysql_cur.execute(team_data_query)
    mysql_cur.execute(season_data_query)
    mysql_cur.execute(game_data_query)
    mysql_conn.commit()
    mysql_conn.close()


season_name = input('Please input the name of the season: ')

while season_name not in season_ids:
    season_name = input('Please input a valid season: ')

game_data, season_data, team_data = prepare_game_information(season_name)
add_to_db(game_data=game_data, season_data=season_data, team_data=team_data)
