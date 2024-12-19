import csv

class Team:
    def __init__(self, iTeamNum, sDistrict, f2024AutoNotes, f2024AutoPoints, f2024SpeakerNotes, f2024AmpNotes, f2024AmplifiedNotes, f2024ParkPoints, f2024OnstagePoints, f2024TrapPoints, lEventList):
        self.iTeamNum = iTeamNum
        self.sDistrict = sDistrict
        self.bDistrict = False if sDistrict.__eq__('Regional') else True # Set district flag to false if 'district' is regional, true otherwise
        self.f2024AutoNotes = f2024AutoNotes
        self.f2024AutoPoints = f2024AutoPoints
        self.f2024SpeakerNotes = f2024SpeakerNotes
        self.f2024AmpNotes = f2024AmpNotes
        self.f2024AmplifiedNotes = f2024AmplifiedNotes
        self.f2024ParkPoints = f2024ParkPoints
        self.f2024OnstagePoints = f2024OnstagePoints
        self.f2024TrapPoints = f2024TrapPoints
        self.bChampsQualified = bool(False)
        self.lEventList = lEventList
        self.iNumPrevEvents = 0
        self.iDeltaLastEvent = 0
        self.fBreakdownChance = 0.02 # Default value
        self.fCAC = 0.0 # Declare float
        self.iDistrictCode = -1
        self.tagDistrict()
        self.percentRaise = 0.0
        self.numRaise = 0.0
        self.percentNav = 0.0
        self.percentHoist = 0.0
        self.blueBanners = 0
        self.silverMedals = 0
        self.bronzeButtons = 0
        self.numAutoNestAttempted = 0
        self.numAutoHullAttempted = 0
        self.numAutoDeckAttempted = 0
        self.numTeleNestAttempted = 0
        self.numTeleHullAttempted = 0
        self.numTeleDeckAttempted = 0
        self.calcCAC()

    """
    :param self
    :returns: None
    """
    def debugPrintAll(self):
        print('Team Number: ' + str(self.iTeamNum) + '\n2024 Auto Notes: ' + str(self.f2024AutoNotes) + '\n2024 Auto Points: ' + str(self.f2024AutoPoints) + '\n2024 Speaker Notes: ' + str(self.f2024SpeakerNotes) + '\n2024 Amp Notes: ' + str(self.f2024AmpNotes) + '\n2024 Park Points: ' + str(self.f2024ParkPoints) + '\n2024 Onstage Points: ' + str(self.f2024OnstagePoints) + '\n2024 Trap Points: ' + str(self.f2024TrapPoints) + '\nChamps Qualified: ' + str(self.bChampsQualified))

    """
    :param self
    :returns: None
    """
    def tagDistrict(self):
        if self.sDistrict.__eq__('Regional'):
            self.iDistrictCode = 0
        elif self.sDistrict.__eq__('CHS'):
            self.iDistrictCode = 1
        elif self.sDistrict.__eq__('FIM'):
            self.iDistrictCode = 2
        elif self.sDistrict.__eq__('FIN'):
            self.iDistrictCode = 3
        elif self.sDistrict.__eq__('FIT'):
            self.iDistrictCode = 4
        elif self.sDistrict.__eq__('FMA'):
            self.iDistrictCode = 5
        elif self.sDistrict.__eq__('FNC'):
            self.iDistrictCode = 6
        elif self.sDistrict.__eq__('FSC'):
            self.iDistrictCode = 7
        elif self.sDistrict.__eq__('ISR'):
            self.iDistrictCode = 8
        elif self.sDistrict.__eq__('NE'):
            self.iDistrictCode = 9
        elif self.sDistrict.__eq__('ONT'):
            self.iDistrictCode = 10
        elif self.sDistrict.__eq__('PCH'):
            self.iDistrictCode = 11
        elif self.sDistrict.__eq__('PNW'):
            self.iDistrictCode = 12
        else:
            print('Check District Code for team: ' + str(self.iTeamNum))
            self.iDistrictCode = -1 #Redundantly set

    """
    :param self
    :returns: None
    """
    def cleanEventList(self):
        i = 0
        while i < len(self.lEventList):
            if self.lEventList[i].__eq__('*'):
                self.lEventList = self.lEventList[:i] # include up to this point
                return None # break out
            i += 1

    """
    :param self
    :returns: None
    """
    def calcCAC(self):
        self.percentRaise = (self.f2024TrapPoints/3.0)%1
        self.numRaise = (self.f2024TrapPoints/3.0)/1
        self.percentNav = self.f2024OnstagePoints/3.0
        self.percentHoist = self.f2024ParkPoints + (self.f2024OnstagePoints/3.0)
        endgameAvgC = float(10*(self.numRaise+self.percentRaise) + 15*self.percentNav)
        self.numTeleNestAttempted = round(self.f2024AmplifiedNotes*3.0)
        self.numTeleHullAttempted = round(self.f2024AmpNotes*3.0)
        self.numTeleDeckAttempted = round((self.f2024SpeakerNotes - self.f2024AmplifiedNotes)*3.0)
        teleTotalAttempts = self.numTeleNestAttempted + self.numTeleHullAttempted + self.numTeleDeckAttempted
        teleMaxC = 5*self.numTeleNestAttempted + 4*self.numTeleHullAttempted + 2*self.numTeleDeckAttempted
        preload = 1 if self.f2024AutoNotes >= 1 else 0
        self.autoCross = 1 if self.f2024AutoPoints >= 2 else 0
        if self.autoCross == 1:
            numAutoCycles = max(0,self.f2024AutoNotes-1)
            numAutoAttempt = preload + 3*numAutoCycles
        else:
            numAutoCycles = 0
            numAutoAttempt = 0
        if teleTotalAttempts <= 0:
            self.numAutoNestAttempted = 0
            self.numAutoHullAttempted = 0
            self.numAutoDeckAttempted = 0
        else:
            self.numAutoNestAttempted = round(numAutoAttempt*(self.numTeleNestAttempted/teleTotalAttempts))
            self.numAutoHullAttempted = round(numAutoAttempt*(self.numTeleHullAttempted/teleTotalAttempts))
            self.numAutoDeckAttempted = round(numAutoAttempt*(self.numTeleDeckAttempted/teleTotalAttempts))
        autoMaxC = 10*self.numAutoNestAttempted + 9*self.numAutoHullAttempted + 4*self.numAutoDeckAttempted + 2*self.autoCross
        self.fCAC = autoMaxC + teleMaxC + endgameAvgC