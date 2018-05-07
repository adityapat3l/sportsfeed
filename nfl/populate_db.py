from nfl.gamedetails import GameInfo
from nfl.api import NflApi


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



def compile_season_details_by_date(season_name, full_schedule):
    full_schedule = NflApi(season_name).full_schedule()

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

                score_home, score_away = NflApi(season_name).game_score(game_id, game_date, game_details_for_date)

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

                # print(game_instance.game_id, ":", game_instance.winner())
                # print(game_instance.winning_team)
            else:
                pass

    return game_instances_all

def main():
    season_name = '2017-regular'
    full_schedule = NflApi(season_name).full_schedule()
    a = list_distinct_team_abbrv(full_schedule)
    print(a)
    print(len(a))
main()
# compile_season_details('2017-regular')