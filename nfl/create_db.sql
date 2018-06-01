use nfl;
create table games(
  id int not null,
  season_id int not null,
  game_start datetime not null,
  location varchar(255),
  home_team_id int not null,
  away_team_id int not null,
  score_home tinyint unsigned,
  score_away tinyint unsigned,
  primary key(id));


create table seasons(
  id int not null,
  season_year int not null,
  season_type varchar(255) not null,
  champion_team_id int(11),
  primary key(id)
);

create table teams(
  id int not null,
  name varchar(255) not null,
  abbr varchar(255) not null,
  city varchar(255) not null,
  primary key (id)
);
show databases;