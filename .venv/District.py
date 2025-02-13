from Team import Team
from Event import Event
from LeaderboardEntry import LeaderboardEntry

class District:
    def __init__(self,sIdentifier):
        self.sIdentifier = sIdentifier
        self.teams = []
        self.events = []
        self.leaderboard = []
        self.isRegional = 0

    """
    :param self
    :returns: None
    """
    def build_leaderboard_list(self):
        self.isRegional = 1 if self.sIdentifier.__eq__('Regional') else 0
        for team in self.teams:
            entry = LeaderboardEntry(team,self.isRegional)
            self.leaderboard.append(entry)

    """
    :param self
    :returns: None
    """
    def update(self):
        for entry in self.leaderboard:
            entry.total = entry.dcmp # hard reset on update
            if len(entry.eventScores) >= 2:
                for i in range(2):
                    entry.total += entry.eventScores[i]
            else:
                for score in entry.eventScores:
                    entry.total += score