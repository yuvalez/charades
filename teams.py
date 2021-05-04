


class Teams:
    def __init__(self, teams=None):
        if teams is None:
            teams = []
        self.teams = {}
        self.score = {}
        for team in teams:
            self.teams[team] = []
            self.score[team] = []

    def add_team_member(self, team, member):
        self.teams[team].append(member)

    def add_team(self, team):
        self.teams[team] = []
