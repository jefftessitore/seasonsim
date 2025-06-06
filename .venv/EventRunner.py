from Team import Team
from Event import Event
from District import District
from RankEntry import RankEntry
from LeaderboardEntry import LeaderboardEntry
import csv
import sys
import copy
import numpy
import statistics
from random import random
from scipy.stats import beta
import scipy.special as sp
import scipy.linalg as la
import re
import os

# Run Match(es)
# Alliance Selection w/ OPR/cOPR tables
# Run Elim Match(es)
# Calculate Regional/District Points
# Modify Leaderboards
# Add Blue Banners/Silver Medals/Bronze Buttons

# Declare these up here so get_necessary_vars knows they exist WITHOUT this program running
class EventRunner:
    def __init__(self,eventCode,external_leaderboard_list,external_event_list,external_team_list,loaded_from_save):
        self.event_code = str(eventCode).strip()
        self.leaderboard_list = []
        self.leaderboard_object = None
        self.event_list = []
        self.team_list = [] # ALL teams
        self.teams_at_event = []
        self.schedule_list = []
        self.results_list_quals = []
        self.alliances = numpy.array([[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]])
        self.results_list_elims = []
        self.week = 0
        self.fileName = 'schedules/' + self.event_code + '.csv'
        self.get_necessary_vars(external_leaderboard_list,external_event_list,external_team_list)
        self.generate_schedule_list(self.fileName)
        self.region, self.leaderboard = self.find_event_region(self.event_code,self.leaderboard_list)
        self.rankings = []
        self.preload_rank_list()
        self.std = 0.0
        self.MECAC = self.calc_MECAC()
        self.a = 2.5
        self.b = 1.495 #week 1: 1.5
        self.qualsRan = 0
        self.points_from_event = []
        self.event_complete = 0
        self.selection_running = 0
        self.declined_teams = []
        self.declined_picks = []
        self.run_rest_quals = 0
        self.last_qual_ran = 0
        self.quals_toRun = len(self.schedule_list)
        self.loaded = loaded_from_save # 0 or 1
        if self.loaded:
            self.load_partial_event()
            self.qualsRan = len(self.results_list_quals)
        self.stringFlag = 0
        #print(self.MECAC)

    def get_event_lb(self):
        code = self.event_code
        if len(code) == 4 or code[:2].__eq__('MN') or code[:4].__eq__('TUIS'):  # regional or MNDUx or TUISx
            self.stringFlag = 1
            return self.leaderboard_list[0]
        elif code[:2].__eq__('MD') or code[:2].__eq__('VA') or code[:2].__eq__('CH'):
            return self.leaderboard_list[1]
        elif code[:2].__eq__('MI'):
            return self.leaderboard_list[2]
        elif code[:2].__eq__('IN'):
            return self.leaderboard_list[3]
        elif code[:2].__eq__('TX'):
            return self.leaderboard_list[4]
        elif code[:2].__eq__('NJ') or code[:2].__eq__('PA'):
            return self.leaderboard_list[5]
        elif code[:2].__eq__('NC'):
            return self.leaderboard_list[6]
        elif code[:2].__eq__('SC'):
            return self.leaderboard_list[7]
        elif code[:2].__eq__('IS'):
            return self.leaderboard_list[8]
        elif (code[:2].__eq__('ME') or code[:2].__eq__('NH') or code[:2].__eq__('CT') or code[:2].__eq__('MA') or
              code[:2].__eq__('RI') or code[:2].__eq__('NE')):
            return self.leaderboard_list[9]
        elif code[:2].__eq__('ON'):
            return self.leaderboard_list[10]
        elif code[:2].__eq__('GA'):
            return self.leaderboard_list[11]
        elif code[:2].__eq__('WA') or code[:2].__eq__('OR') or code[:2].__eq__('PN'):
            return self.leaderboard_list[12]
        else:
            print(code + 'is not a valid event code.\n')
            return None

    def event_get_lbe(self,teamNum):
        for leaderboard_entry in self.leaderboard_object.leaderboard:
            if int(leaderboard_entry.teamNum) == int(teamNum):
                return leaderboard_entry

    """
    :param self
    :returns: None
    """
    def get_necessary_vars(self,external_leaderboard_list,external_event_list,external_team_list):
        for leaderboard in external_leaderboard_list:
            self.leaderboard_list.append(leaderboard)
        for event in external_event_list:
            self.event_list.append(event)
        for team in external_team_list:
            self.team_list.append(team)
        self.leaderboard_object = self.get_event_lb()

    """
    :param self
    :param fileName: str containing full filepath of schedule csv
    :param schedule_list: reference to the specified schedule list to modify
    :returns: None
    """
    def generate_schedule_list(self,fileName):
        schedule_row_list = []
        with open(fileName) as schedule:
            reader = csv.reader(schedule)
            for row in reader:
                schedule_row_list.append(row)
        schedule.close()
        for match in schedule_row_list:
            self.schedule_list.append([match[0],match[1:4],match[-3:]]) # honestly no idea how this was working week 1

    """
    :param self
    :param teamNum: int containing team number
    :returns: team object matching team number
    """
    def find_team_object(self,teamNum):
        #print('Searching team ', str(teamNum).strip())
        for team in self.team_list:
            if int(team.iTeamNum) == int(str(teamNum).strip()):
                #print('Found team ', str(teamNum).strip())
                return team

    """
    :param self
    :param teamNum: int containing team number
    :returns: team object matching team number
    """
    def fast_fto(self,teamNum):
        for team in self.teams_at_event:
            #print(str(team.iTeamNum).strip())
            if str(team.iTeamNum).strip().__eq__(str(teamNum).strip()):
                return team

    """
    :param self
    :returns: None
    """
    def preload_rank_list(self):
        for team in self.eventObject.lTeamList:
            entry = RankEntry(team)
            self.rankings.append(entry)
            teamO = self.find_team_object(team)
            if teamO is None:
                continue
            self.teams_at_event.append(teamO)

    """
    :param self
    :param match: int containing match number
    :param type: integer boolean (int 0 or 1) specifying quals (0) vs. elims (1)
    :param results_list: reference to the specified results list to modify
    :returns: None
    """
    def run_match(self,match,type,results_list):
        #print('Made it into the method')
        if type == 0: # qual
            deck_score = 2
            hoist_score = 0
            raise_score = 2
        else: # elim
            deck_score = 3
            hoist_score = 10
            raise_score = 10
        match_num = match[0] # save match num
        red_alliance = match[1] # list of three teams on red
        blue_alliance = match[2] # list of three teams on blue
        #print('Match ' + str(match_num) + ' Red: ' + str(red_alliance) + ' Blue: ' + str(blue_alliance))
        # Vars
        red_autoMobile = 0
        red_autoDeck = 0
        red_autoHull = 0
        red_autoMast = 0
        red_autoNest = 0
        red_teleDeck = 0
        red_teleHull = 0
        red_teleMast = 0
        red_teleNest = 0
        red_endgameRaise = 0
        red_endgameHoist = 0
        red_endgameNav   = 0
        blue_autoMobile = 0
        blue_autoDeck = 0
        blue_autoHull = 0
        blue_autoMast = 0
        blue_autoNest = 0
        blue_teleDeck = 0
        blue_teleHull = 0
        blue_teleMast = 0
        blue_teleNest = 0
        blue_endgameRaise = 0
        blue_endgameHoist = 0
        blue_endgameNav   = 0
        # Red
        for team in red_alliance:
            #print('Finding team ',int(team.strip()))
            #if team is np.dtype('int64'):
            teamO = self.fast_fto(team)
            #else:
                #teamO = self.fast_fto(int(team.strip()))
            #print('Found team ',teamO.iTeamNum)
            team_devs = abs((self.MECAC - teamO.fCAC)/self.std) # corrected weeks 2+
            team_sign = (self.MECAC - teamO.fCAC) / self.std
            if team_devs >= 3.0: # nerfed for weeks 2+
                percent_adjust = 0.05
            elif team_devs >= 2.5:
                percent_adjust = 0.035
            elif team_devs >= 2.0:
                percent_adjust = 0.025
            elif team_devs >= 1.5:
                percent_adjust = 0.015
            elif team_devs >= 1.0:
                percent_adjust = 0.01
            elif team_devs >= 0.5:
                percent_adjust = 0.005
            else:
                percent_adjust = 0.0
            if team_sign > 0: # if team CAC is below MECAC
                percent_adjust = -1*percent_adjust # flip sign
            
            red_autoMobile += teamO.autoCross
            red_autoDeck += round(beta.rvs(self.a,self.b)*teamO.numAutoDeckAttempted)
            red_autoHull += round(beta.rvs(self.a,self.b)*teamO.numAutoHullAttempted)
            aNestsMade = round(beta.rvs(self.a,self.b)*teamO.numAutoNestAttempted)
            aNestsMissed = teamO.numAutoNestAttempted - aNestsMade
            for i in range(aNestsMissed):
                red_autoMast += 1 if random() < 0.95 else 0 # mast %age not adjusted
            red_autoNest += round(beta.rvs(self.a,self.b)*teamO.numAutoNestAttempted)
            
            red_teleDeck += round(beta.rvs(self.a,self.b)*teamO.numTeleDeckAttempted)
            red_teleHull += round(beta.rvs(self.a,self.b)*teamO.numTeleHullAttempted)
            tNestsMade = round(beta.rvs(self.a,self.b)*teamO.numTeleNestAttempted)
            tNestsMissed = teamO.numTeleNestAttempted - tNestsMade
            for i in range(tNestsMissed):
                red_teleMast += 1 if random() < 0.95 else 0 # mast %age not adjusted
            
            if red_endgameHoist < 2:
                red_endgameHoist += 1 if random() < (teamO.percentHoist + percent_adjust) else 0
            else:
                red_endgameNav += 1 if random() < (teamO.percentNav + percent_adjust) else 0
            red_endgameRaise += teamO.numRaise
            red_endgameRaise += 1 if random() < (teamO.percentRaise + percent_adjust) else 0
            #print('Red done')
            # end of for loop
        # Blue
        for team in blue_alliance:
            teamO = self.fast_fto(team)
            team_devs = abs((self.MECAC - teamO.fCAC) / self.std)  # corrected weeks 2+
            team_sign = (self.MECAC - teamO.fCAC) / self.std
            if team_devs >= 3.0:  # nerfed for weeks 2+
                percent_adjust = 0.05
            elif team_devs >= 2.5:
                percent_adjust = 0.035
            elif team_devs >= 2.0:
                percent_adjust = 0.025
            elif team_devs >= 1.5:
                percent_adjust = 0.015
            elif team_devs >= 1.0:
                percent_adjust = 0.01
            elif team_devs >= 0.5:
                percent_adjust = 0.005
            else:
                percent_adjust = 0.0
            if team_sign > 0:  # if team CAC is below MECAC
                percent_adjust = -1 * percent_adjust  # flip sign
                
            blue_autoMobile += teamO.autoCross
            blue_autoDeck += round(beta.rvs(self.a,self.b)*teamO.numAutoDeckAttempted)
            blue_autoHull += round(beta.rvs(self.a,self.b)*teamO.numAutoHullAttempted)
            aNestsMade = round(beta.rvs(self.a,self.b)*teamO.numAutoNestAttempted)
            aNestsMissed = teamO.numAutoNestAttempted - aNestsMade
            for i in range(aNestsMissed):
                blue_autoMast += 1 if random() < 0.95 else 0 # mast %age not adjusted
            blue_autoNest += round(beta.rvs(self.a,self.b)*teamO.numAutoNestAttempted)
            
            blue_teleDeck += round(beta.rvs(self.a,self.b)*teamO.numTeleDeckAttempted)
            blue_teleHull += round(beta.rvs(self.a,self.b)*teamO.numTeleHullAttempted)
            tNestsMade = round(beta.rvs(self.a,self.b)*teamO.numTeleNestAttempted)
            tNestsMissed = teamO.numTeleNestAttempted - tNestsMade
            for i in range(tNestsMissed):
                blue_teleMast += 1 if random() < 0.95 else 0 # mast %age not adjusted
            
            if blue_endgameHoist < 2:
                blue_endgameHoist += 1 if random() < (teamO.percentHoist + percent_adjust) else 0
            else:
                blue_endgameNav += 1 if random() < (teamO.percentNav + percent_adjust) else 0
            blue_endgameRaise += teamO.numRaise
            blue_endgameRaise += 1 if random() < (teamO.percentRaise + percent_adjust) else 0
            #print('Blue done')
            # end of for loop
        self.calculate_scores(type,match_num,red_alliance,blue_alliance,
                              red_autoMobile,red_autoDeck,red_autoHull,red_autoMast,red_autoNest,
                              blue_autoMobile,blue_autoDeck,blue_autoHull,blue_autoMast,blue_autoNest,
                              deck_score,
                              red_teleDeck,red_teleHull,red_teleMast,red_teleNest,
                              blue_teleDeck,blue_teleHull,blue_teleMast,blue_teleNest,
                              hoist_score,
                              red_endgameHoist,red_endgameRaise,red_endgameNav,
                              blue_endgameHoist,blue_endgameRaise,blue_endgameNav,
                              raise_score,1,None,None,None,match)
        # end of method

    def calculate_scores(self,type,match_num,red_alliance,blue_alliance,
                              red_autoMobile,red_autoDeck,red_autoHull,red_autoMast,red_autoNest,
                              blue_autoMobile,blue_autoDeck,blue_autoHull,blue_autoMast,blue_autoNest,
                              deck_score,
                              red_teleDeck,red_teleHull,red_teleMast,red_teleNest,
                              blue_teleDeck,blue_teleHull,blue_teleMast,blue_teleNest,
                              hoist_score,
                              red_endgameHoist,red_endgameRaise,red_endgameNav,
                              blue_endgameHoist,blue_endgameRaise,blue_endgameNav,
                              raise_score,fromRunMatch,given_result_array,given_scores,given_RPs,match):
        # Calculate scores
        if fromRunMatch == 1:
            red_autoScore = 2*red_autoMobile + 4*red_autoDeck + 9*red_autoHull + 3*red_autoMast + 10*red_autoNest
            blue_autoScore = 2*blue_autoMobile + 4*blue_autoDeck + 9*blue_autoHull + 3*blue_autoMast + 10*blue_autoNest
            red_teleScore = deck_score*red_teleDeck + 4*red_teleHull + 2*red_teleMast + 5*red_teleNest
            blue_teleScore = deck_score*blue_teleDeck + 4*blue_teleHull + 2*blue_teleMast + 5*blue_teleNest
            red_endgameScore = hoist_score*red_endgameHoist + raise_score*red_endgameRaise + 15*red_endgameNav
            blue_endgameScore = hoist_score*blue_endgameHoist + raise_score*blue_endgameRaise + 15*blue_endgameNav
            red_totalScore = int(red_autoScore + red_teleScore + red_endgameScore) # Typecasting just in case
            blue_totalScore = int(blue_autoScore + blue_teleScore + blue_endgameScore) # Typecasting just in case
            redwin = 0
            redloss = 0
            redtie = 0
            bluewin = 0
            blueloss = 0
            bluetie = 0
            red_bonusRP = 0
            blue_bonusRP = 0
            if red_totalScore == blue_totalScore:
                result = 'TIE'
                (redtie, bluetie) = (1, 1)
            elif red_totalScore > blue_totalScore:
                result = 'RED'
                (redwin, blueloss) = (1, 1)
            else: # red < blue
                result = 'BLUE'
                (redloss, bluewin) = (1, 1)
            #print('Result calculated')
            if type == 0: #qual
                red_bonusRP += 1 if red_endgameRaise >= 3 and (red_autoDeck + red_teleDeck) >= 25 else 0
                red_bonusRP += 1 if red_endgameHoist >= 2 else 0
                blue_bonusRP += 1 if blue_endgameRaise >= 3 and (blue_autoDeck + blue_teleDeck) >= 25 else 0
                blue_bonusRP += 1 if blue_endgameHoist >= 2 else 0
                if result.__eq__('TIE'):
                    red_totalRP = 1 + red_bonusRP
                    blue_totalRP = 1 + blue_bonusRP
                elif result.__eq__('RED'):
                    red_totalRP = 2 + red_bonusRP
                    blue_totalRP = blue_bonusRP
                else:
                    red_totalRP = red_bonusRP
                    blue_totalRP = 2 + blue_bonusRP
                for team in red_alliance:
                    rankEntry = self.find_rank_entry(team)
                    rankEntry.update_entry(int(redwin),int(redloss),int(redtie),int(red_totalRP),int(red_totalScore),int(red_endgameNav),int(red_endgameRaise),int(red_autoDeck+red_teleDeck),int(red_autoHull+red_teleHull),int(red_autoNest+red_teleNest),int(red_endgameHoist))
                for team in blue_alliance:
                    rankEntry = self.find_rank_entry(team)
                    rankEntry.update_entry(int(bluewin),int(blueloss),int(bluetie),int(blue_totalRP),int(blue_totalScore),int(blue_endgameNav),int(blue_endgameRaise),int(blue_autoDeck+blue_teleDeck),int(blue_autoHull+blue_teleHull),int(blue_autoNest+blue_teleNest),int(blue_endgameHoist))
                result_entry = []
                # Displayed
                result_entry.append(match_num)
                for team in red_alliance:
                    result_entry.append(int(team))
                for team in blue_alliance:
                    result_entry.append(int(team))
                redScoreString = str(red_totalScore)
                blueScoreString = str(blue_totalScore)
                for i in range(red_bonusRP):
                    redScoreString = redScoreString + '•'
                for i in range(blue_bonusRP):
                    blueScoreString = blueScoreString + '•'
                result_entry.append(redScoreString)
                result_entry.append(blueScoreString)
                result_entry.append(result) # Index 9
                # Never displayed, used in OPR calculations
                result_entry.append(red_endgameNav) # Index 10
                result_entry.append(red_endgameRaise)
                result_entry.append(red_autoDeck+red_teleDeck)
                result_entry.append(red_autoHull+red_teleHull)
                result_entry.append(red_autoNest+red_teleNest)
                result_entry.append(red_endgameHoist)
                result_entry.append(blue_endgameNav) # Index 16
                result_entry.append(blue_endgameRaise)
                result_entry.append(blue_autoDeck+blue_teleDeck)
                result_entry.append(blue_autoHull+blue_teleHull)
                result_entry.append(blue_autoNest+blue_teleNest)
                result_entry.append(blue_endgameHoist) # Index 21
                # Append result
                self.results_list_quals.append(result_entry)
                #print(result_entry) # debug
                if self.run_rest_quals == 0:
                    #print('Match#','Red_1','Red_2','Red_3','Blue1','Blue2','Blue3','Red_Score','BlueScore','Result')
                    print('Match Num: ',result_entry[0],
                          '\nRed: ',result_entry[1],result_entry[2],result_entry[3],
                          '\nBlue: ',result_entry[4],result_entry[5],result_entry[6],
                          '\nScores and Result: ',result_entry[7],result_entry[8],result_entry[9])
            else: # elim
                #print('Made it to else statement')
                result_entry = []
                match_num = int(match_num)
                result_entry.append(match_num)
                for team in red_alliance:
                    result_entry.append(int(team))
                for team in blue_alliance:
                    result_entry.append(int(team))
                result_entry.append(red_totalScore)
                result_entry.append(blue_totalScore)
                if red_totalScore == blue_totalScore:
                    result = 'TIE'
                    print('Tie, replaying')
                    self.run_match(match,1,self.results_list_elims) # rerun before appending kek
                elif red_totalScore > blue_totalScore:
                    result = 'RED'
                else: # red < blue
                    result = 'BLUE'
                result_entry.append(result)
                #print('Result entry appended')
                #print(result_entry)
                self.results_list_elims.append(result_entry)
        else: # from partial load
                redwin = int(given_result_array[0])
                redloss = int(given_result_array[1])
                redtie = int(given_result_array[2])
                bluewin = int(given_result_array[3])
                blueloss = int(given_result_array[4])
                bluetie = int(given_result_array[5])
                red_totalScore = int(given_scores[0])
                blue_totalScore = int(given_scores[1])
                red_totalRP = int(given_RPs[0])
                blue_totalRP = int(given_RPs[1])
                for team in red_alliance:
                    rankEntry = self.find_rank_entry(int(str(team).strip()))
                    rankEntry.update_entry(int(redwin),int(redloss),int(redtie),int(red_totalRP),int(red_totalScore),int(red_endgameNav),int(red_endgameHoist),int(red_teleDeck),int(red_teleHull),int(red_teleNest),int(red_endgameHoist))
                for team in blue_alliance:
                    rankEntry = self.find_rank_entry(int(str(team).strip()))
                    rankEntry.update_entry(int(bluewin),int(blueloss),int(bluetie),int(blue_totalRP),int(blue_totalScore),int(blue_endgameNav),int(blue_endgameHoist),int(blue_teleDeck),int(blue_teleHull),int(blue_teleNest),int(blue_endgameHoist))
        # end of method

    """
    :param self
    :param teamNum: int containing team number
    :returns: RankEntry object
    """
    def find_rank_entry(self,teamNum):
        for rank in self.rankings:
            if int(str(rank.teamNum).strip()) == int(str(teamNum).strip()):
                return rank

    def print_schedule(self):
        for match in self.schedule_list:
            print(match) # very badly formatted, placeholder for now

    def quals_menu(self,match_num):
        print('Next match: Qualification ',int(match_num)) # typecast JUST IN CASE
        print('n - Run next match')
        print('r - Show rankings')
        print('z - Run all remaining matches')
        print('s - Save event')
        print('p - Print schedule')

    """
    :param self
    :returns: None
    """
    def run_quals(self):
        match_num = self.last_qual_ran + 1
        cChoice = ''
        self.quals_toRun = len(self.schedule_list)
        while match_num <= self.quals_toRun:
            match = self.schedule_list[match_num-1] # grab match object
            if self.run_rest_quals == 0:
                self.quals_menu(match_num)
                cChoice = input('Enter choice --> ').strip()
                if cChoice is None:
                    continue
                else:
                    cChoice = cChoice[0]
                if cChoice == 'n':
                    self.run_match(match,0,self.results_list_quals)
                    self.last_qual_ran = match_num
                    match_num += 1
                    continue
                elif cChoice == 'r':
                    self.print_ranks()
                    continue
                elif cChoice == 'z':
                    self.run_rest_quals = 1
                    self.run_match(match,0,self.results_list_quals)
                    self.last_qual_ran = match_num
                    match_num += 1
                    continue
                elif cChoice == 's':
                    #self.save_partial_event()
                    break # break out of while loop (and quit method)
                elif cChoice == 'p':
                    self.print_schedule()
                    continue
                else:
                    print('Please enter a valid option.')
                    continue
            else:
                self.run_match(match,0,self.results_list_quals)
                self.last_qual_ran = match_num
                match_num += 1
            # end while loop
        if self.last_qual_ran == self.quals_toRun:
            self.qualsRan = 1
        else:
            print('Event ready to save on Qualification ',match_num)
        # end def run_quals

    """
    :param self
    :param event_code: event code to search
    :returns: integer containing the week # the event takes place in (1-8), or 0 if not found
    """
    def get_event_week(self,event_code):
        for event in self.event_list:
            #print(str(event_code).strip())
            #print(event.sCode.strip())
            if isinstance(event_code, str):
                testWith = str(event_code).strip()
            else:
                testWith = event_code.sCode.strip()
            if isinstance(event, str):
                testAgainst = str(event).strip()
            else:
                testAgainst = event.sCode.strip()
            if testWith.__eq__(testAgainst):
                #print('My event code is ',str(event_code).strip(),' and I matched ',event.sCode.strip())
                self.eventObject = copy.deepcopy(event)
                if self.stringFlag != 0:
                    return 1 # return non-zero value
                return event.iWeek
        return 0

    """
    :param self
    :param eventCode: event code to search
    :param leaderboard_list: reference to list of leaderboards
    :returns: leaderboard.sIdentifier/ERR matching leaderboard (or error case), refernce to the leaderboard object/None
    """
    def find_event_region(self,eventCode,leaderboard_list):
        #print(eventCode)
        for leaderboard in leaderboard_list:
            #print(leaderboard.sIdentifier)
            for event in leaderboard.events:
                #print(event.sCode)
                if isinstance(event, str):
                    testAgainst = str(event)
                else:
                    testAgainst = event.sCode
                if eventCode.__eq__(testAgainst):
                    self.week = self.get_event_week(event)
                    if self.week == 0 and self.stringFlag == 0:
                        return 'ERR', None
                    return leaderboard.sIdentifier, leaderboard
        return 'ERR', None

    """
    :param self
    :param to_sort: vector to sort
    :returns: None
    """
    def sel_sort(self,to_sort):
        n = len(to_sort)
        for ind in range(n-1):
            min_ind = ind
            for j in range(ind+1,n):
                if to_sort[j] < to_sort[min_ind]:
                    min_ind = j
            (to_sort[ind],to_sort[min_ind]) = (to_sort[min_ind],to_sort[ind])

    """
    :param self
    :returns: MECAC, a float containing the (trimmed) mean Calculated Average Contribution (which really should be max)
    """
    def calc_MECAC(self):
        collated = []
        for team in self.teams_at_event:
            collated.append(team.fCAC)
        self.std = numpy.std(collated)
        self.sel_sort(collated)
        #print(collated)
        #print(self.std)
        count = float(len(collated))
        trim = round(0.025*count)
        #print('Trimmed ' + str(trim) + ' off each end.')
        trimmed = collated[trim:-trim]
        return statistics.mean(trimmed)

    """
    :param self
    :param resultType: a char specifying the results list to print
    :returns: None
    """
    def show_results(self,resultType):
        if resultType.__eq__('q'): #quals
            print('Match | RedS1 | RedS2 | RedS3 | BlueS1 | BlueS2 | BlueS3 | Red Score | Blue Score | Result')
            for result_entry in self.results_list_quals:
                print('{:5d} | {:5d} | {:5d} | {:5d} | {:6d} | {:6d} | {:6d} | {:9>s} | {:>s} | {:6>s}'.format(int(result_entry[0]),int(result_entry[1]),int(result_entry[2]),int(result_entry[3]),int(result_entry[4]),int(result_entry[5]),int(result_entry[6]),result_entry[7].rjust(9),result_entry[8].rjust(10),result_entry[9].rjust(6)))
        elif resultType.__eq__('a'): 
            self.show_alliances()
        elif resultType.__eq__('e'): #elims
            print('Match | RedS1 | RedS2 | RedS3 | BlueS1 | BlueS2 | BlueS3 | Red Score | Blue Score | Result')
            for result_entry in self.results_list_elims:
                print('{:5d} | {:5d} | {:5d} | {:5d} | {:6d} | {:6d} | {:6d} | {:9d} | {:10d} | {:6>s}'.format(int(result_entry[0]),int(result_entry[1]),int(result_entry[2]),int(result_entry[3]),int(result_entry[4]),int(result_entry[5]),int(result_entry[6]),int(result_entry[7]),int(result_entry[8]),result_entry[9].rjust(6)))
        else:
            print('Invalid result type. Returning to menu.')
            return None

    """
    :param self
    :returns: None
    """
    def print_ranks(self):
        self.rankings.sort(key=lambda x: (-x.RS, -x.Nav, -x.Anch, -x.Deck, -x.Hull, -x.Nest, -x.Sail))
        rankNum = 1
        print('Rank | Team# | Record   | #P | RP | Rank Score | Total Score | Nav | Anch | Deck | Hull | Nest | Sail')
        for rank in self.rankings:
            print('{:4d} | {:5d} | {:2d}-{:2d}-{:2d} | {:2d} | {:2d} | {:10.2f} | {:11d} | {:3d} | {:4d} | {:4d} | {:4d} | {:4d} | {:3d}'.format(rankNum,rank.teamNum,rank.wins,rank.losses,rank.ties,rank.totalMatches,rank.RP,rank.RS,rank.totalScore,rank.Nav,rank.Anch,rank.Deck,rank.Hull,rank.Nest,rank.Sail))
            rankNum += 1

    """
    :param self
    :returns: None
    """
    def calc_oprs(self):
        numpy.set_printoptions(threshold=sys.maxsize)
        opr_table = []
        A_matrix = []
        teamNums = []
        matchIndex = 0
        results_transpose = numpy.transpose(self.results_list_quals)
        teamOList_transpose = numpy.transpose(self.teams_at_event)
        red1_t = results_transpose[1]
        red2_t = results_transpose[2]
        red3_t = results_transpose[3]
        blue1_t = results_transpose[4]
        blue2_t = results_transpose[5]
        blue3_t = results_transpose[6]
        for teamO in self.teams_at_event:
            teamNums.append(int(teamO.iTeamNum))
        teamNums_transpose = numpy.transpose(teamNums)
        '''
        # start with red
        for result in self.results_list_quals:
            A_row = numpy.zeros(len(self.teams_at_event))
            # 1 if team was in red at all, 0 if not
            for i in range(len(self.teams_at_event)):
                teamNum = self.teams_at_event[i].iTeamNum
                for team1, team2, team3 in zip(red1_t,red2_t,red3_t):
                    if int(teamNum) == int(team1) or int(teamNum) == int(team2) or int(teamNum) == int(team3):
                        A_row[i] = int(1)
                    else:
                        A_row[i] = int(0)
            A_matrix.append(A_row)
            matchIndex += 1
        # repeat with blue
        for result in self.results_list_quals:
            A_row = numpy.zeros(len(self.teams_at_event))
            # 1 if team was in blue at all, 0 if not
            for i in range(len(self.teams_at_event)):
                teamNum = self.teams_at_event[i].iTeamNum
                for team1, team2, team3 in zip(blue1_t,blue2_t,blue3_t):
                    if int(teamNum) == int(team1) or int(teamNum) == int(team2) or int(teamNum) == int(team3):
                        A_row[i] = int(1)
                    else:
                        A_row[i] = int(0)
            A_matrix.append(A_row)
            matchIndex+=1
        A_matrix = numpy.array(A_matrix,dtype=int)
        print(A_matrix[0]) # Debug
        # Get OPRS
        table_row = []
        # Total Score OPR
        
        B_vector = numpy.array(results_transpose[7])
        B_vector = numpy.append(B_vector,results_transpose[8])
        B_vector = self.fixB(B_vector)
        B_vector = numpy.transpose(B_vector)
        print('B: ',B_vector) # Debug
        tot_in_order = la.pinv(A_matrix) @ B_vector
        print('OPRS: ',tot_in_order)
        # Print (will be moved)
        
        print('Team# | Total OPR')
        for i in range(len(teamNums)):
            table_row.append(teamNums[i])
            table_row.append(float(tot_in_order[i]))
            opr_table.append(table_row)
        opr_table.sort(key=lambda x: self.get_col_val(x,1), reverse=True)
        for row in opr_table:
            print('{:5d} | {:9.2f}'.format(int(row[0]),float(row[1])))'''
        # Just average/match for now based on alliance
        
        for i in range(len(teamNums)):
            sumTot = 0.0
            sumNav = 0.0
            sumAnch = 0.0
            sumDeck = 0.0
            sumHull = 0.0
            sumNest = 0.0
            sumSail = 0.0
            totalMatch = float(self.rankings[0].totalMatches) # nab #1 seed's total played since all are equal
            teamAvgRow = []
            for j in range(len(red1_t)):
                if int(teamNums[i]) == int(red1_t[j]) or int(teamNums[i]) == int(red2_t[j]) or int(teamNums[i]) == int(red3_t[j]):
                    sumTot += float(self.fixscore(results_transpose[7][j]))
                    sumNav += float(results_transpose[10][j])
                    sumAnch += float(results_transpose[11][j])
                    sumDeck += float(results_transpose[12][j])
                    sumHull += float(results_transpose[13][j])
                    sumNest += float(results_transpose[14][j])
                    sumSail += float(results_transpose[15][j])
                if int(teamNums[i]) == int(blue1_t[j]) or int(teamNums[i]) == int(blue2_t[j]) or int(teamNums[i]) == int(blue3_t[j]):
                    sumTot += float(self.fixscore(results_transpose[8][j]))
                    sumNav += float(results_transpose[16][j])
                    sumAnch += float(results_transpose[17][j])
                    sumDeck += float(results_transpose[18][j])
                    sumHull += float(results_transpose[19][j])
                    sumNest += float(results_transpose[20][j])
                    sumSail += float(results_transpose[21][j])
            teamAvgRow.append(int(teamNums[i]))
            teamAvgRow.append(float(sumTot)/float(totalMatch))
            teamAvgRow.append(float(sumNav)/float(totalMatch))
            teamAvgRow.append(float(sumAnch)/float(totalMatch))
            teamAvgRow.append(float(sumDeck)/float(totalMatch))
            teamAvgRow.append(float(sumHull)/float(totalMatch))
            teamAvgRow.append(float(sumNest)/float(totalMatch))
            teamAvgRow.append(float(sumSail)/float(totalMatch))
            #print('{:5d} | {:7.2f} | {:5.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f}'.format(int(teamNums[i]),avgMatch,avgNav,avgAnch,avgDeck,avgHull,avgNest,avgSail))
            opr_table.append(teamAvgRow)
        opr_table = numpy.array(opr_table)
        opr_table = opr_table[opr_table[:,1].argsort()[::-1]]
        return opr_table
        
        # End of method

    """
    :param self
    :param opr_table: 2D array containing OPR table to print
    :returns: None
    """
    def show_oprs(self,opr_table):
        print('Team# | ScorePM | NavPM | AnchPM | DeckPM | HullPM | NestPM | SailPM')
        if self.selection_running == 0:
            for row in opr_table:
                print('{:5d} | {:7.2f} | {:5.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f}'.format(int(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
        else:
            for row in opr_table:
                if not (int(row[0]) in self.alliances):
                    print('{:5d} | {:7.2f} | {:5.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f} | {:6.2f}'.format(
                        int(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    """
    :param self
    :param score: A string containing the resulting score (with RP bonus chars)
    :returns: an integer version of just the score
    """
    def fixscore(self,score):
        return int(''.join(digit for digit in score if digit.isalnum()))

    """
    :param self
    :param row: row of the array
    :param col: col of the array
    :returns: value at row[col] 
    """
    def get_col_val(self,row,col):
        return row[col]

    """
    :param self
    :returns: None
    """
    def show_alliances(self):
        print('Alliance # | Captain | Pick 1 | Pick 2')
        for i in range(8):
            alliance_str = 'Alliance {:1d}'.format(int(i+1))
            print('{:10} | {:7d} | {:6d} | {:6d}'.format(alliance_str.rjust(10),int(self.alliances[i][0]),int(self.alliances[i][1]),int(self.alliances[i][2])))

    """
    :param self
    :returns: None
    """
    def alliance_menu(self):
        print('p - Pick team')
        print('a - Show ranks')
        print('o - Show all by score per match')
        print('f - fill captain')

    """
    :param self
    :returns: None
    """
    def run_alliance_selection(self):
        self.selection_running = 1
        if self.qualsRan == 0:
            print('Quals not complete!')
            return None
        opr_table = self.calc_oprs()
        self.show_oprs(opr_table)
        picks = int(0)
        while picks < 24:
            #os.system('cls')
            if picks == 0:
                self.print_ranks()
            self.show_alliances()
            self.alliance_menu()
            cChoice = input('Enter Choice --> ').strip()
            if cChoice is None:
                continue
            else:
                cChoice = cChoice[0]
            if cChoice == 'a':
                self.print_ranks()
                continue
            elif cChoice == 'o':
                self.show_oprs(opr_table)
                continue
            elif cChoice == 'p':
                selection = input('Enter team number: ').strip()
                if selection is None: # if we received nothing
                    continue
                teamSelected = int(''.join(digit for digit in selection if digit.isalnum()))
                if self.fast_fto(teamSelected) is None: # in theory should return None only if fast_fto didn't find the teamNum
                    print('Invalid: Team not present at event!')
                    continue
                if teamSelected in self.alliances:
                    print('Invalid: Team already picked!')
                    continue
                if teamSelected in self.declined_teams:
                    print('Invalid: That team declined an invitation and is ineligible to be picked!')
                    continue
                if picks < 16:
                    response = input('Enter a for accept or d for decline --> ').strip()
                    if response is None:
                        continue
                    else:
                        response = response[0]
                    if response == 'd':
                        self.declined_teams.append(teamSelected)
                        self.declined_picks.append(int((picks/2)+1))
                        continue
                    elif response == 'a':
                        self.alliances[int((picks/2)%8)][1] = teamSelected
                        picks += 1
                        continue
                    else:
                        print('Invalid entry.')
                        continue
                elif picks >= 16:
                    self.alliances[int((23-picks)%8)][2] = teamSelected
                    picks += 1
                continue
            elif cChoice == 'f':
                if picks > 15: # oops...
                    print('Invalid: All captain spots filled!')
                    continue
                for rank in self.rankings:
                    # this if block below is horrific coding practice and I'm not sorry
                    if (rank.teamNum in self.alliances) == False:
                        teamNum = rank.teamNum
                        break
                self.alliances[int(((picks+1)/2)%8)][0] = teamNum
                picks += 1
                continue
            else:
                print('Please enter a valid choice')
                continue
        self.create_elims_bracket()
        self.selection_running = 0
        # End of method

    """
    :param self
    :returns: None
    """
    def create_elims_bracket(self):
        match1 = [int(1),[self.alliances[0][0],self.alliances[0][1],self.alliances[0][2]],[self.alliances[7][0],self.alliances[7][1],self.alliances[7][2]]]
        match3 = [int(3),[self.alliances[1][0],self.alliances[1][1],self.alliances[1][2]],[self.alliances[6][0],self.alliances[6][1],self.alliances[6][2]]]
        match4 = [int(4),[self.alliances[2][0],self.alliances[2][1],self.alliances[2][2]],[self.alliances[5][0],self.alliances[5][1],self.alliances[5][2]]]
        match2 = [int(2),[self.alliances[3][0],self.alliances[3][1],self.alliances[3][2]],[self.alliances[4][0],self.alliances[4][1],self.alliances[4][2]]]
        self.UBR1 = [match1,match2,match3,match4]

    """
    :param self
    :returns: None
    """
    def calc_event_points(self):
        pass
        '''
        self.event_info = [self.event_code,self.region,self.week]
        numTeams = len(self.teams_at_event)
        alpha = 1.07 # constant
        alpha_inv = 1.0/alpha # 1/alpha
        qp = 0
        for team in self.teams_at_event:
            rank = 0
            count = 0
            for rank in self.rankings:
                count += 1
                if int(team.iTeamNum) == int(rank.teamNum):
                    rank = count
                    break
            numerator = float(numTeams - 2*rank + 2.0)
            denominator = float(alpha*numTeams)
            firstTerm = sp.erfinv(numerator/denominator)
            secondTerm = 10.0/sp.erfinv(alpha_inv)
            qp = max(round(firstTerm*secondTerm + 12),4) # sometimes the rounding results in the last rank getting 3; this corrects the minimum to 4
            ap = 0
            ref_teamNum = 0
            for i in range(len(self.alliances)):
                #print('Finding reference for team {:5d}'.format(int(team.iTeamNum)))
                alliance = self.alliances[i]
                pos = 0
                for teamNum in alliance:
                    pos += 1
                    if teamNum == int(team.iTeamNum):
                        if pos < 3:
                            ap = 16 - i # first captain and first pick (i = 0, pos = 1, 2) get 16, 8th capt/fp (i = 7, pos = 1, 2) get 16-7=9 
                        else: # pos == 3 since only 3 teams per alliance in default case
                            ap = 1 + i # first second pick (i = 0, pos = 3) gets 1, 8th sp (i = 7, pos = 3) gets 1+7=8
                        ref_teamNum = int(alliance[0]) # get captain as index for elims points calculation
                        #print('Reference is: {:5d}'.format(ref_teamNum))
                    else: # is not our team
                        continue
                # team not found, ap = 0 (end of inner for loop)
            # end of middle for loop
            ep = 0 # Finals 1 is match 14, len(self.results_list_elims)-1 gives index of last final (and winner of event), 3rd place match is match 13, 4th place match 12
            # This is also the point where we add gold, silver, and bronze medals for teams
            win_result = self.results_list_elims[len(self.results_list_elims)-1][9]
            win_ref = int(self.results_list_elims[13][1]) if win_result.__eq__('RED') else int(self.results_list_elims[13][4])
            fin_ref = int(self.results_list_elims[13][4]) if win_result.__eq__('RED') else int(self.results_list_elims[13][1])
            third_res = self.results_list_elims[12][9]
            third_ref = int(self.results_list_elims[12][4]) if third_res.__eq__('RED') else int(self.results_list_elims[12][1])
            four_res = self.results_list_elims[11][9]
            four_ref = int(self.results_list_elims[11][4]) if four_res.__eq__('RED') else int(self.results_list_elims[11][1])
            #print('Winner ref: {:5d}\n2nd ref: {:5d}\n3rd ref: {:5d}\n4th ref: {:5d}'.format(win_ref,fin_ref,third_ref,four_ref))
            if int(ref_teamNum) == int(win_ref): 
                #print('{:5d} equals {:5d}'.format(ref_teamNum,win_ref))
                team.blueBanners += 1
                ep = 30
            elif int(ref_teamNum) == int(fin_ref):
                #print('{:5d} equals {:5d}'.format(ref_teamNum,fin_ref))
                team.silverMedals += 1
                ep = 20
            elif int(ref_teamNum) == int(third_ref):
                #print('{:5d} equals {:5d}'.format(ref_teamNum,third_ref))
                team.bronzeButtons += 1
                ep = 13
            elif int(ref_teamNum) == int(four_ref):
                #print('{:5d} equals {:5d}'.format(ref_teamNum,four_ref))
                ep = 7
            event_points = int(qp + ap + ep)
            for lbEntry in self.leaderboard.leaderboard:
                if int(lbEntry.teamNum) == int(team.iTeamNum):
                    lbEntry.eventScores.append(event_points)
            points_entry = [int(team.iTeamNum),event_points,int(qp),int(ap),int(ep)]
            self.points_from_event.append(points_entry)
            thisLbEntry = self.event_get_lbe(team.iTeamNum)
            if thisLbEntry is None:
                print(teamNum, 'is not eligible for points in this region.')
                continue
            thisLbEntry.eventScores.append(event_points)
        # end of outer for loop
        self.event_complete = 1
    # end of method
    '''

    """
    :param self
    :returns: None
    """
    def show_event_points(self):
        pass
        '''
        print('Team# | Total | Rank | Selection | Elims')
        for entry in self.points_from_event:
            print('{:5d} | {:6d} | {:4d} | {:9d} | {:5d}'.format(entry[0],entry[1],entry[2],entry[3],entry[4]))
        '''

    """
    :param self
    :returns: None
    """
    def elim_menu(self):
        print('n - Run next match')

    """
    :param self
    :param matchNum - Match number to search for
    :return index - Index in results list of match number
        --> The current behavior of ties is that they're added after the replayed match due to the recursive call,
            so I'm making use of that by returning the index of the first time a given match number appears
    """
    def get_index(self,matchNum):
        index = 0
        for result in self.results_list_elims:
            if int(result[0]) == int(matchNum):
                return index
            index += 1

    """
    :param self
    :returns: None
    """
    # Results - 0 = matchNum, 1-3 = red, 4-6 = blue, 7-8 = scores, 9 = result
    def run_elims(self):
        for match in self.UBR1:
            self.run_match(match,1,self.results_list_elims)
        matchNum = 5
        match_7_red = []
        match_7_blue = []
        match_8_red = []
        match_8_blue = []
        match_9_red = []
        match_9_blue = []
        match_10_red = []
        match_10_blue = []
        match_11_red = []
        match_11_blue = []
        match_12_red = []
        match_12_blue = []
        match_13_red = []
        match_13_blue = []
        finals_red = []
        finals_blue = []
        while matchNum < 17:
            if matchNum == 5:
                red_alliance = []
                blue_alliance = []
                if self.results_list_elims[self.get_index(1)][9].__eq__('RED'): # don't need to get_index because index 0 is always successful match 1
                    for i in range(3):
                        red_alliance.append(self.results_list_elims[self.get_index(1)][i+4])
                        match_7_red.append(self.results_list_elims[self.get_index(1)][i+1])
                else: # BLUE
                    for i in range(3):
                        red_alliance.append(self.results_list_elims[self.get_index(1)][i+1])
                        match_7_red.append(self.results_list_elims[self.get_index(1)][i+4])
                if self.results_list_elims[self.get_index(2)][9].__eq__('RED'):
                    for i in range(3):
                        blue_alliance.append(self.results_list_elims[self.get_index(2)][i+4])
                        match_7_blue.append(self.results_list_elims[self.get_index(2)][i+1])
                else: # BLUE
                    for i in range(3):
                        blue_alliance.append(self.results_list_elims[self.get_index(2)][i+1])
                        match_7_blue.append(self.results_list_elims[self.get_index(2)][i+4])
                match5 = [int(5),red_alliance,blue_alliance]
                self.run_match(match5,1,self.results_list_elims)
            elif matchNum == 6:
                red_alliance = []
                blue_alliance = []
                if self.results_list_elims[self.get_index(3)][9].__eq__('RED'):
                    for i in range(3):
                        red_alliance.append(self.results_list_elims[self.get_index(3)][i+4])
                        match_8_red.append(self.results_list_elims[self.get_index(3)][i+1])
                else: # BLUE
                    for i in range(3):
                        red_alliance.append(self.results_list_elims[self.get_index(3)][i+1])
                        match_8_red.append(self.results_list_elims[self.get_index(3)][i+4])
                if self.results_list_elims[self.get_index(4)][9].__eq__('RED'):
                    for i in range(3):
                        blue_alliance.append(self.results_list_elims[self.get_index(4)][i+4])
                        match_8_blue.append(self.results_list_elims[self.get_index(4)][i+1])
                else: # BLUE
                    for i in range(3):
                        blue_alliance.append(self.results_list_elims[self.get_index(4)][i+1])
                        match_8_blue.append(self.results_list_elims[self.get_index(4)][i+4])
                match6 = [int(6),red_alliance,blue_alliance]
                self.run_match(match6,1,self.results_list_elims)
            elif matchNum == 7:
                match7 = [int(7),match_7_red,match_7_blue]
                self.run_match(match7,1,self.results_list_elims)
            elif matchNum == 8:
                match8 = [int(8),match_8_red,match_8_blue]
                self.run_match(match8,1,self.results_list_elims)
            elif matchNum == 9:
                if self.results_list_elims[self.get_index(7)][9].__eq__('RED'): # Need loser of match 7
                    for i in range(3):
                        match_9_red.append(self.results_list_elims[self.get_index(7)][i+4])
                        match_11_red.append(self.results_list_elims[self.get_index(7)][i+1]) # Winner goes to match 11 red
                else: # BLUE
                    for i in range(3):
                        match_9_red.append(self.results_list_elims[self.get_index(7)][i+1])
                        match_11_red.append(self.results_list_elims[self.get_index(7)][i+4])
                if self.results_list_elims[self.get_index(6)][9].__eq__('RED'): # Need winner of match 6 (loser eliminated)
                    for i in range(3):
                        match_9_blue.append(self.results_list_elims[self.get_index(6)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_9_blue.append(self.results_list_elims[self.get_index(6)][i+4])
                match9 = [int(9),match_9_red,match_9_blue]
                self.run_match(match9,1,self.results_list_elims)
            elif matchNum == 10:
                if self.results_list_elims[self.get_index(8)][9].__eq__('RED'): # Need Loser of match 8
                    for i in range(3):
                        match_10_red.append(self.results_list_elims[self.get_index(8)][i+4])
                        match_11_blue.append(self.results_list_elims[self.get_index(8)][i+1])  # Winner goes to match 11 blue
                else: # BLUE
                    for i in range(3):
                        match_10_red.append(self.results_list_elims[self.get_index(8)][i+1])
                        match_11_blue.append(self.results_list_elims[self.get_index(8)][i+4])
                if self.results_list_elims[self.get_index(5)][9].__eq__('RED'): # Need winner of match 5 (Loser eliminated)
                    for i in range(3):
                        match_10_blue.append(self.results_list_elims[self.get_index(5)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_10_blue.append(self.results_list_elims[self.get_index(5)][i+4])
                match10 = [int(10),match_10_red,match_10_blue]
                self.run_match(match10,1,self.results_list_elims)
            elif matchNum == 11:
                match11 = [int(11),match_11_red,match_11_blue]
                self.run_match(match11,1,self.results_list_elims)
            elif matchNum == 12: 
                if self.results_list_elims[self.get_index(10)][9].__eq__('RED'): # Need winner of match 10 (Loser eliminated)
                    for i in range(3):
                        match_12_red.append(self.results_list_elims[self.get_index(10)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_12_red.append(self.results_list_elims[self.get_index(10)][i+4])
                if self.results_list_elims[self.get_index(9)][9].__eq__('RED'): # Need winner of match 9 (Loser eliminated)
                    for i in range(3):
                        match_12_blue.append(self.results_list_elims[self.get_index(9)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_12_blue.append(self.results_list_elims[self.get_index(9)][i+4])
                match12 = [int(12),match_12_red,match_12_blue]
                self.run_match(match12,1,self.results_list_elims)
            elif matchNum == 13: # Third place match
                if self.results_list_elims[self.get_index(11)][9].__eq__('RED'): # Need loser of match 11 (winner to finals)
                    for i in range(3):
                        match_13_red.append(self.results_list_elims[self.get_index(11)][i+4])
                        finals_red.append(self.results_list_elims[self.get_index(11)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_13_red.append(self.results_list_elims[self.get_index(11)][i+1])
                        finals_red.append(self.results_list_elims[self.get_index(11)][i+4])
                if self.results_list_elims[self.get_index(12)][9].__eq__('RED'): # Need winner of match 12 (Loser eliminated)
                    for i in range(3):
                        match_13_blue.append(self.results_list_elims[self.get_index(12)][i+1])
                else: # BLUE
                    for i in range(3):
                        match_13_blue.append(self.results_list_elims[self.get_index(12)][i+4])
                match13 = [int(13),match_13_red,match_13_blue]
                self.run_match(match13,1,self.results_list_elims)
            elif matchNum == 14: # Finals 1
                if self.results_list_elims[self.get_index(13)][9].__eq__('RED'): # Need winner of match 13 (Loser eliminated)
                    for i in range(3):
                        finals_blue.append(self.results_list_elims[self.get_index(13)][i+1])
                else: # BLUE
                    for i in range(3):
                        finals_blue.append(self.results_list_elims[self.get_index(13)][i+4])
                match14 = [int(14),finals_red,finals_blue]
                self.run_match(match14,1,self.results_list_elims)
            elif matchNum == 15: # Finals 2
                match15 = [int(15),finals_red,finals_blue]
                self.run_match(match15,1,self.results_list_elims)
            elif matchNum == 16: # Finals 3
                if self.results_list_elims[self.get_index(14)][9].__eq__(self.results_list_elims[self.get_index(15)][9]): # if the same alliance won both finals 1 and 2
                    matchNum = 17
                    continue
                else: # finals 3 needed
                    match16 = [int(16),finals_red,finals_blue]
                    self.run_match(match16,1,self.results_list_elims)
                    matchNum = 17
            else:
                continue
            matchNum += 1
            # end of while loop
        ### self.calc_event_points()
        # end of method

    """
    :param self
    :returns: String representation of event code
    """
    def save_partial_event(self):
        qFileName = 'Partial_Results/' + str(self.event_code) + 'Quals.csv'
        with open(qFileName,'w',newline='') as qfile:
            writer = csv.writer(qfile)
            writer.writerows(self.results_list_quals)
        qfile.close()
        if self.last_qual_ran == self.quals_toRun:
            aFileName = 'Partial_Results/' + str(self.event_code) + 'Alliances.csv'
            with open(aFileName, 'w', newline='') as afile:
                writer = csv.writer(afile)
                writer.writerows(self.alliances)
            afile.close()
        else:
            mFileName = 'Partial_Results/' + str(self.event_code) + 'Schedule.csv'
            with open(mFileName,'w',newline='') as mfile:
                writer = csv.writer(mfile)
                for match in self.schedule_list: # reverse engineered from generate_schedule_list method to allow for use on load
                    if len(match) > 0:
                        row = []
                        row.append(match[0])
                        for i in range(1,4):
                            row.append(match[1][i-1])
                        for j in range(4,7):
                            row.append(match[2][i-4])
                        writer.writerow(row)
                    else:
                        continue
            mfile.close()
        rFileName = 'Partial_Results/' + str(self.event_code) + 'Ranks.csv'
        with open(rFileName,'w',newline='') as rfile:
            writer = csv.writer(rfile)
            rankNum = 1
            for rank in self.rankings:
                row = [rankNum, rank.teamNum, rank.wins, rank.losses, rank.ties, rank.totalMatches, rank.RP, rank.RS,
                        rank.totalScore, rank.Nav, rank.Anch, rank.Deck, rank.Hull, rank.Nest, rank.Sail]
                rankNum += 1
                writer.writerow(row)
        rfile.close()
        # elims next
        return self.event_code

    def load_partial_event(self):
        qFileName = 'Partial_Results/' + str(self.event_code) + 'Quals.csv'
        mFileName = 'Partial_Results/' + str(self.event_code) + 'Schedule.csv'
        rFileName = 'Partial_Results/' + str(self.event_code) + 'Ranks.csv'
        q_results_list = []
        with open(qFileName) as qual_results:
            reader = csv.reader(qual_results)
            for row in reader:
                q_results_list.append(row)
        qual_results.close()
        for result in q_results_list:
            result_entry = []
            for i in range(0,22):
                result_entry.append(result[i]) # can load it straight when partially done
            self.results_list_quals.append(result_entry)
        curMatch = 1
        deck_score = 2
        hoist_score = 0
        raise_score = 2
        for result in self.results_list_quals:
            win_result = str(result[9]).strip()
            red_alliance = result[1:4]
            blue_alliance = result[4:7]
            red_bonusRP = 0
            blue_bonusRP = 0
            red_scoreString = str(result[7]).strip()
            blue_scoreString = str(result[8]).strip()
            red_bonusRP = red_scoreString.count('•')
            blue_bonusRP = blue_scoreString.count('•')
            if red_bonusRP > 0:  # if bullet character present in string
                red_totalScore = int(red_scoreString[:red_scoreString.find('•')])
            else:
                red_totalScore = int(red_scoreString)
            if blue_bonusRP > 0:
                blue_totalScore = int(blue_scoreString[:blue_scoreString.find('•')])
            else:
                blue_totalScore = int(blue_scoreString)
            redwin = 0
            redloss = 0
            redtie = 0
            bluewin = 0
            blueloss = 0
            bluetie = 0
            if win_result.__eq__('TIE'):
                (redtie, bluetie) = (1, 1)
                red_totalRP = 1 + red_bonusRP
                blue_totalRP = 1 + blue_bonusRP
            elif win_result.__eq__('RED'):
                (redwin, blueloss) = (1, 1)
                red_totalRP = 2 + red_bonusRP
                blue_totalRP = blue_bonusRP
            else:  # result.__eq__('BLUE')
                (redloss, bluewin) = (1, 1)
                red_totalRP = red_bonusRP
                blue_totalRP = 2 + blue_bonusRP
            # these will all be given straight
            red_endgameNav = float(str(result[10]).strip())
            red_endgameRaise = float(str(result[11]).strip())
            red_totalDeck = float(str(result[12]).strip())
            red_totalHull = float(str(result[13]).strip())
            red_totalNest = float(str(result[14]).strip())
            red_endgameHoist = float(str(result[15]).strip())
            blue_endgameNav = float(str(result[16]).strip())
            blue_endgameRaise = float(str(result[17]).strip())
            blue_totalDeck = float(str(result[18]).strip())
            blue_totalHull = float(str(result[19]).strip())
            blue_totalNest = float(str(result[20]).strip())
            blue_endgameHoist = float(str(result[21]).strip())
            self.calculate_scores(0,curMatch,red_alliance,blue_alliance,
                                  0,0,0,0,0,0,0,0,0,0,
                                  deck_score,red_totalDeck,red_totalHull,0,red_totalNest,blue_totalDeck,blue_totalHull,0,blue_totalNest,
                                  hoist_score,red_endgameHoist,red_endgameRaise,red_endgameNav,blue_endgameHoist,blue_endgameRaise,blue_endgameNav,
                                  raise_score,0,[redwin,redloss,redtie,bluewin,blueloss,bluetie],[red_totalScore,blue_totalScore],[red_totalRP,blue_totalRP],None)
            curMatch += 1
        self.last_qual_ran = len(self.results_list_quals)
        if os.path.exists(mFileName): # match schedule exists, quals are NOT done
            pass # already preloading match schedule!
        else: # match schedule does not exist, quals are done!
            aFileName = 'Partial_Results/' + str(self.event_code) + 'Alliances.csv'
            with open(aFileName) as alliances:
                reader = csv.reader(alliances)
                i = 0
                for row in reader:
                    self.alliances[i] = row
                    i += 1
            alliances.close()

        ''' #Don't actually need because changed to scoring on separate method
        ranks_list = []
        with open(rFileName) as current_ranks:
            reader = csv.reader(current_ranks)
            for row in reader:
                ranks_list.append(row)
        current_ranks.close()
        for rank in ranks_list:
            entry = RankEntry(int(rank[1])) # index 1 holds team number
            entry.wins = int(rank[2])
            entry.losses = int(rank[3])
            entry.ties = int(rank[4])
            entry.totalMatches = int(rank[5])
            entry.RP = int(rank[6])
            entry.RS = float(rank[7])
            entry.totalScore = int(rank[8])
            entry.Nav = int(rank[9])
            entry.Anch = int(rank[10])
            entry.Deck = int(rank[11])
            entry.Hull = int(rank[12])
            entry.Nest = int(rank[13])
            entry.Sail = int(rank[14])
            self.rankings.append(entry)
            '''
        # elims next
        # end of method

    """
    :param self
    :returns: None
    """
    def save_event(self):
        qFileName = 'Official_Results/' + str(self.event_code) + 'Quals.csv'
        aFileName = 'Official_Results/' + str(self.event_code) + 'Alliances.csv'
        eFileName = 'Official_Results/' + str(self.event_code) + 'Elims.csv'
        rFileName = 'Official_Results/' + str(self.event_code) + 'Ranks.csv'
        dFileName = 'Official_Results/' + str(self.event_code) + 'Declines.csv'
        ### pFileName = 'Official_Results/' + str(self.event_code) + 'Points.csv'
        with open(qFileName,'w',newline='') as qfile:
            writer = csv.writer(qfile)
            row1 = ['#','Red_1','Red_2','Red_3','Blue1','Blue2','Blue3','Red_Score','BlueScore','Result',
                    'RedNav','RedRaise','RedDeck','RedHull','RedNest','RedHoist',
                    'BlueNav','BlueRaise','BlueDeck','BlueHull','BlueNest','BlueHoist']
            writer.writerow(row1)
            writer.writerows(self.results_list_quals)
        qfile.close()
        with open(aFileName,'w',newline='') as afile:
            writer = csv.writer(afile)
            row1 = ['Captn','Pick1','Pick2']
            writer.writerow(row1)
            writer.writerows(self.alliances)
        afile.close()
        with open(eFileName,'w',newline='') as efile:
            writer = csv.writer(efile)
            row1 = ['#', 'Red_1', 'Red_2', 'Red_3', 'Blue1', 'Blue2', 'Blue3', 'Red_Score', 'BlueScore', 'Result']
            writer.writerow(row1)
            writer.writerows(self.results_list_elims)
        efile.close()
        with open(rFileName,'w',newline='') as rfile:
            writer = csv.writer(rfile)
            rankNum = 1
            row1 = ['Rank','Team#','W','L','T','#P','RP','Rank Score','Total Score','Nav','Anch','Deck','Hull','Nest','Sail']
            writer.writerow(row1)
            for rank in self.rankings:
                row = [rankNum, rank.teamNum, rank.wins, rank.losses, rank.ties, rank.totalMatches, rank.RP, rank.RS,
                        rank.totalScore, rank.Nav, rank.Anch, rank.Deck, rank.Hull, rank.Nest, rank.Sail]
                rankNum += 1
                writer.writerow(row)
        rfile.close()
        with open(dFileName,'w',newline='') as dfile:
            writer = csv.writer(dfile)
            if len(self.declined_teams) > 0:
                row1 = ['Decliner','Captain Num Declined']
                writer.writerow(row1)
                for decliner,declinee in zip(self.declined_teams,self.declined_picks):
                    row = [decliner,declinee]
                    writer.writerow(row)
            else:
                row1 = ['No','Declines']
                writer.writerow(row1)
        dfile.close()
        '''
        with open(pFileName,'w',newline='') as pfile:
            writer = csv.writer(pfile)
            row1 = ['Team#', 'Total', 'Rank', 'Selection', 'Elims']
            writer.writerow(row1)
            writer.writerows(self.points_from_event)
        '''
    # end of program