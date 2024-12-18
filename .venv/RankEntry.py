class RankEntry:
    def __init__(self,teamNum):
        self.teamNum = teamNum
        self.wins = int(0)
        self.losses = int(0)
        self.ties = int(0)
        self.totalMatches = int(0)
        self.RP = int(0)
        self.totalScore = int(0)
        self.RS = 0.0
        self.Nav = int(0)
        self.Anch = int(0)
        self.Deck = int(0)
        self.Hull = int(0)
        self.Nest = int(0)
        self.Sail = int(0)

    """
    :param self
    :returns: None
    """
    def update_entry(self,win,loss,tie,RP,totalScore,Nav,Anch,Deck,Hull,Nest,Sail):
        self.wins += int(win)
        self.losses += int(loss)
        self.ties += int(tie)
        self.RP += int(RP)
        self.totalScore += int(totalScore)
        self.Nav += int(Nav)
        self.Anch += int(Anch)
        self.Deck += int(Deck)
        self.Hull += int(Hull)
        self.Nest += int(Nest)
        self.Sail += int(Sail)
        self.totalMatches += 1
        self.RS = float(self.RP)/float(self.totalMatches)