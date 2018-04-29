from nfl.gamedetails import GameInfo
from nfl.api import NflApi
import json


def team_info(team):
    team_id = team['ID']
    team_name = team['Name']
    team_abbr = team['Abbreviation']
    team_city = team['City']

    return team_id, team_name, team_abbr, team_city


def game_info(game):
    game_id = int(game['id'])
    game_date = game['date']
    game_time = game['time']
    game_location = game['location']
    game_delayed_reason = game['delayedOrPostponedReason']

    return game_id, game_date, game_time, game_location, game_delayed_reason


def compile_game_details(season_name):
    full_schedule = NflApi(season_name).full_schedule()

    # get all games for that date
    set_game_dates = set()
    all_games_on_date = {}
    for game in full_schedule['fullgameschedule']['gameentry']:
        game_date = game['date']
        set_game_dates.add(game_date)

    for game in full_schedule['fullgameschedule']['gameentry']:
        if game['date'] not in all_games_on_date:
            all_games_on_date[game['date']] = [game['id']]
        else:
            all_games_on_date[game['date']].append(game['id'])

    # get all the games info for the unique dates - Reduce API calls
    for date in all_games_on_date:
        games_for_date = NflApi(season_name).all_games_on_date(date)
        for game in full_schedule['fullgameschedule']['gameentry']:
            if game['date'] == date:
                home_args = team_info(game['homeTeam'])
                away_args = team_info(game['awayTeam'])
                args = (*away_args, *home_args)
                game_id, game_date, game_time, game_location, game_delayed_reason = game_info(game)

                score_home, score_away = NflApi(season_name).game_score(game_id, game_date, games_for_date)

                game_instance = GameInfo(season_name,
                                         game_id,
                                         game_date,
                                         game_time,
                                         game_location,
                                         game_delayed_reason,
                                         score_home,
                                         score_away,
                                         *args)

                print(game_instance.game_id, ":", game_instance.winner())
                print(game_instance.winning_team)