import requests
import json
import datetime
import nfl.config


class NflApi:
    def __init__(self, season_name):
        self.username = nfl.config.username
        self.password = nfl.config.password
        self.season_name = season_name

    def get_api_data(self, url, payload=None):

        response = requests.get(
            url=url,
            auth=(self.username, self.password),
            params=payload
        )
        if response.status_code == 200:

            data = json.loads(response.content.decode('utf-8'))
            return data
        else:
            raise ValueError('Api Pull failed with status code: ' + str(response.status_code))

    def full_schedule(self):
        url = "https://api.mysportsfeeds.com/v1.2/pull/nfl/{}/full_game_schedule.json".format(self.season_name)
        response = self.get_api_data(url)
        return response

    def game_score(self, game_id, date, games_on_date=None):
        if not games_on_date:
            games_on_date = self.all_games_on_date(date)
        score_home = 0
        score_away = 0
        for all_games in games_on_date['scoreboard']['gameScore']:
            if int(all_games['game']['ID']) == game_id:
                for quarter_details in all_games['quarterSummary']['quarter']:
                    score_home += int(quarter_details['homeScore'])
                    score_away += int(quarter_details['awayScore'])

        return score_home, score_away

    def all_games_on_date(self, date):
        if date > str(datetime.datetime.today()):
            return 'The Game Will Be Played On {0}'.format(date)

        url = "https://api.mysportsfeeds.com/v1.2/pull/nfl/{0}/scoreboard.json?fordate={1}?force=false".format(
                                self.season_name,
                                date.replace("-", ""))
        params = {'fordate':date.replace("-",""), 'force':False}
        response = self.get_api_data(url)

        if not response:
            return 'There is no Data for the game'

        return response

    def full_season_details_by_team(self):
        url = "https://api.mysportsfeeds.com/v1.2/pull/nfl/{0}/team_gamelogs.json".format(self.season_name)
        response = self.get_api_data(url)

        return response


    def team_logs(self, team):
        url = "https://api.mysportsfeeds.com/v1.2/pull/nfl/{0}/team_gamelogs.json".format(self.season_name)
        params = {'team': team}

        response = self.get_api_data(url, params)


