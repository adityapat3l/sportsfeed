from nfl.api import NflApi
import datetime

# Change to Kwargs
class Away:
    def __init__(self, id_away_team, name_away_team, abbr_away_team, city_away_team, *args):
        super().__init__(*args)
        self.id_away_team = id_away_team
        self.name_away_team = name_away_team
        self.abbr_away_team = abbr_away_team
        self.city_away_team = city_away_team

    def players_injured(self):
        pass


class Home:
    def __init__(self, id_home_team, name_home_team, abbr_home_team, city_home_team, *args):
        super().__init__(*args)
        self.id_home_team = id_home_team
        self.name_home_team = name_home_team
        self.abbr_home_team = abbr_home_team
        self.city_home_team = city_home_team

    def players_injured(self):
        pass


class GameInfo(Away, Home):
    def __init__(self, season_name, game_id, date, time, location, delayed_reason,
                 score_home='', score_away='', *args):
        super().__init__(*args)
        self.season_name = season_name
        self.season_year = season_name.split('-')[0]
        self.season_type = season_name.split('-')[1]
        if not isinstance(game_id, int):
            self.game_id = int(game_id)
        else:
            self.game_id = game_id
        self.date = date
        self.time = time
        dt = date + " " + time
        self.datetime = str(datetime.datetime.strptime(dt, '%Y-%m-%d %I:%M%p'))
        self.game_tz = "EST"
        self.location = location
        self.delayed_reason = delayed_reason
        if not score_away and not score_away:
            self.score_home = 0
            self.score_away = 0
            self.game_details()
        else:
            self.score_home = score_home
            self.score_away = score_away

        self.winning_team = self.winner()

    def game_details(self):
        self.score_home, self.score_away = NflApi(self.season_name).game_score(self.game_id, self.date)

    def winner(self):
        if self.score_home > self.score_away:
            self.winning_team = self.id_home_team
            return 'The ' + str(self.name_home_team) + ' won against the ' +\
                            str(self.name_away_team)
        elif self.score_home < self.score_away:
            self.winning_team = self.id_away_team
            return 'The ' + str(self.name_away_team) + ' won against the ' +\
                            str(self.name_home_team)
        else:
            self.winning_team = 'Tie'
            return 'Tied'

    def players_injured_count(self):
        pass

















