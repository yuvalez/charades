from constants import *


class Teams:
    def __init__(self, num_of_teams=2):
        self.teams = {}
        self.score = {}
        for _ in range(num_of_teams):
            colors = list(map(get_color_from_name ,self.teams.keys()))
            team = name_generator()
            while get_color_from_name(team) in colors:
                team = name_generator()

            self.teams[team] = []
            self.score[team] = []

    def add_team_member(self, team, member):
        if member:
            self.teams[team].append(member)

    def add_team(self, team):
        self.teams[team] = []

    def is_members_in_teams(self):
        return any(filter(lambda x: len(x), self.teams.values()))
