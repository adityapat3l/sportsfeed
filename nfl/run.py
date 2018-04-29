from nfl.gamedetails import GameInfo


season_name = '2017-regular'
home_args = (1, "home", "H", "HOMER")
away_args = (2, "away", "A", "SIMPSON")
args = (*away_args, *home_args)
first = GameInfo(season_name,'40368', '2017-09-10', "1:00PM", "HOMER_GAME", None, *args)


print(first.game_id,
        first.score_home,
        first.score_away)


