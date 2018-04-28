import requests
import json
import datetime
import nfl.config


class NflApi:
    def __init__(self):
        self.username = nfl.config.username
        self.password = nfl.config.password

    def full_schedule(self, season_name):
        response = requests.get(
            url="https://api.mysportsfeeds.com/v1.2/pull/nfl/{}/full_game_schedule.json".format(season_name),
            auth=(self.username, self.password)
        )
        full_schedule = json.loads(response.content.decode('utf-8'))
        return full_schedule

    def game_score(self, season_name, game_id, date, time):
        if date > str(datetime.datetime.today()):
            return 'The Game Will Be Played On {0}'.format(date)

        response = requests.get(
            url=" https://api.mysportsfeeds.com/v1.2/pull/nfl/{0}/scoreboard.json?fordate={1}".format(
                season_name,
                date.replace("-", "")),
            auth=(self.username, self.password)
        )

        if len(response.content) == 0:
            print('The Game Will Be Played At {}'.format(time))
            raise ValueError

        all_game_details = json.loads(response.content.decode('utf-8'))
        score_home = 0
        score_away = 0
        for all_games in all_game_details['scoreboard']['gameScore']:
            if int(all_games['game']['ID']) == game_id:
                for quarter_details in all_games['quarterSummary']['quarter']:
                    score_home += int(quarter_details['homeScore'])
                    score_away += int(quarter_details['awayScore'])

        return score_home, score_away
