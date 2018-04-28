import nfl.api

# Change to Kwargs
class Away:
    def __init__(self, id_away_team, name_away_team, abbr_away_team, city_away_team, *args):
        super().__init__(*args)
        self.id_away_team = id_away_team
        self.name_away_team = name_away_team
        self.abbr_away_team = abbr_away_team
        self.city_away_team = city_away_team


class Home:
    def __init__(self, id_home_team, name_home_team, abbr_home_team, city_home_team, *args):
        super().__init__(*args)
        self.id_home_team = id_home_team
        self.name_home_team = name_home_team
        self.abbr_home_team = abbr_home_team
        self.city_home_team = city_home_team


class GameInfo(Away, Home):
    def __init__(self, season_name, game_id, date, time, location, delayed_reason, *args):
        super().__init__(*args)
        self.season_name = season_name
        self.season_year = season_name.split('-')[0]
        self.season_type = season_name.split('-')[1]
        self.game_id = int(game_id)
        self.date = date
        self.time = time
        self.game_tz = "EST"
        self.location = location
        self.delayed_reason = delayed_reason
        self.winner = None
        self.score_home = 0
        self.score_away = 0
        self.game_details()

    def game_details(self):
        self.score_home, self.score_away = nfl.api.NflApi().game_score(self.season_name, self.game_id, self.date, self.time)















