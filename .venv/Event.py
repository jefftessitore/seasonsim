import csv

class Event:
    def __init__(self,iWeek,sCode,lTeamList):
        self.iWeek = iWeek
        #self.sName = sName
        self.sCode = sCode
        self.fMECAC = 0.0
        self.fSTDCAC = 0.0
        self.lTeamList = lTeamList

    """
    :param self
    :returns: None
    """
    def debugPrintAll(self):
        print('Event Week: ' + str(self.iWeek) + '\nEvent Code: ' + self.sCode + '\nEvent Team List: ' + str(self.lTeamList))

    """
    :param self
    :returns: None
    """
    def printTeamList(self):
        print(self.sCode + ' Team List:')
        for team in self.lTeamList:
            print(str(team))