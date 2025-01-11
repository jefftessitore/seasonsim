from Team import Team
from Event import Event
from District import District
from EventRunner import EventRunner
from LeaderboardEntry import LeaderboardEntry
from RankEntry import RankEntry
from enum import Enum
import csv
import random
import inspect
import sys

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def preload_events(event_row_list):
    event_list = []
    for event in event_row_list:
        i = 0
        week = 0
        code = str('')
        team_list = []
        while i < len(event):
            if i == 0: # week
                week = int(event[i])
            elif i == 1: # event code
                code = code + event[i]
            else: # team list
                if is_number(event[i]):
                    team_list.append(int(event[i]))
                # else don't add to team list (blank space)
            i+=1
            # end of while loop
        #print('Week: ' + str(week) + ', Code: ' + code + ', Team List: ' + str(team_list))
        oEvent = Event(week,code,team_list)
        event_list.append(oEvent)
        if len(code) == 4 or code[:2].__eq__('MN') or code[:4].__eq__('TUIS'): # regional or MNDUx or TUISx
            regional_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('MD') or code[:2].__eq__('VA') or code[:2].__eq__('CH'):
            chs_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('MI'):
            fim_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('IN'):
            fin_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('TX'):
            fit_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('NJ') or code[:2].__eq__('PA'):
            fma_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('NC'):
            fnc_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('SC'):
            fsc_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('IS'):
            isr_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('ME') or code[:2].__eq__('NH') or code[:2].__eq__('CT') or code[:2].__eq__('MA') or code[:2].__eq__('RI') or code[:2].__eq__('NE'):
            ne_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('ON'):
            ont_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('GA'):
            pch_leaderboard.events.append(oEvent)
        elif code[:2].__eq__('WA') or code[:2].__eq__('OR') or code[:2].__eq__('PN'):
            pnw_leaderboard.events.append(oEvent)
        else:
            print(code + ' not assigned to district.\n')
        # end of for loop
    return event_list
    # end of method

def sort_events(event_list,sort_pass):
    if sort_pass == 0: # sort by week
        n = len(event_list)
        for i in range(n-1):
            min_idx = i
            for j in range(i+1,n):
                if event_list[j].iWeek < event_list[min_idx].iWeek:
                    min_idx = j
            if min_idx != i:
                event_list[i],event_list[min_idx]=event_list[min_idx],event_list[i]
    else: # sort by name
        n = len(event_list)
        for i in range(n-1):
            min_idx = i
            for j in range(i+1,n):
                if event_list[j].sCode < event_list[min_idx].sCode:
                    min_idx = j
            if min_idx != i:
                event_list[i],event_list[min_idx]=event_list[min_idx],event_list[i]        

def col_avg(list,col):
    sum = 0.0
    vals = 0.0
    for row in list:
        vals += 1.0
        sum += float(row[col])
    return sum/vals

def get_var_name(var): # Stolen from the internet
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame)[1]
    local_vars = caller_frame.frame.f_locals
    for name, value in local_vars.items():
        if value is var:
            return name

def display_leaderboards():
    i = 0
    print('Code - Leaderboard')
    for leaderboard in leaderboard_list:
        print(i,' - ',leaderboard.sIdentifier)
        i += 1
    chosenLB = int(input('Enter choice --> ').strip())%13 # takes input and moduluses(?) it with # available to prevent trolling
    print(leaderboard_list[chosenLB].sIdentifier)
    for team in leaderboard_list[chosenLB].teams:
        print(team)
    for event in leaderboard_list[chosenLB].events:
        print(event.sCode)
    #for entry in leaderboard_list[chosenLB].leaderboard:
    #    print(entry.teamNum)

def sort_leaderboard(leaderboard):
    n = len(leaderboard.leaderboard)
    for ind in range(n-1):
        min_ind = ind
        for j in range(ind+1,n):
            if leaderboard.leaderboard[j].total < leaderboard.leaderboard[min_ind].total:
                min_ind = j
        (leaderboard.leaderboard[ind],leaderboard.leaderboard[min_ind]) = (leaderboard.leaderboard[min_ind],leaderboard.leaderboard[ind])
    leaderboard.leaderboard.reverse()

def find_team(team_num,team_list):
    for teamO in team_list:
        if int(teamO.iTeamNum) == int(team_num):
            return teamO
    return None

def menu():
    print('MENU:')
    print('l - Load an event')
    print('q - Run Quals')
    print('p - Print ranks for current event')
    print('a - Run Alliance Selection (All Quals must be complete; must be run in one sitting)')
    print('e - Run Elims (Automatically calculates event points on completion)')
    print('r - Show match results')
    print('s - Show Points from event')
    print('i - Save in-progress event (must be run even if saved from event menu to ensure proper encoding of savefiles)')
    print('d - Print leaderboard (choice given upon selection)')
    print('f - Save event to csv')
    print('b - Batch save (WARNING! Uses a lot of file storage)')
    print('x - Exit the program')
    print('z - Debug Menu')

def debug_menu():
    print('r - Calculate ranks based on Quals csv')
    print('p - Calculate event points')
    print('t - Print team info')
    print('q - Run DCMP/CMP qualification')

def save_everything():
    with open('allteams.csv','w',newline='') as teamSave:
        writer = csv.writer(teamSave)
        for team in team_list:
            row = []
            row.append(str(team.iTeamNum))
            row.append(str(team.sDistrict))
            row.append(str(team.f2024AutoNotes))
            row.append(str(team.f2024AutoPoints))
            row.append(str(team.f2024SpeakerNotes))
            row.append(str(team.f2024AmpNotes))
            row.append(str(team.f2024AmplifiedNotes))
            row.append(str(team.f2024ParkPoints))
            row.append(str(team.f2024OnstagePoints))
            row.append(str(team.f2024TrapPoints))
            events = []
            for event in team.lEventList:
                events.append(str(event))
            if len(events) < 6: # makes all team saves have exactly 6 slots for events attending (maximum pre-DCMP/CMP) for easier parsing upon load
                for i in range(6-len(events)):
                    events.append(str(''))
            for e in events:
                row.append(e)
            # NOT part of team constructor
            row.append(str(team.bDistrict))
            row.append(str(team.iNumPrevEvents))
            row.append(str(team.iDeltaLastEvent))
            row.append(str(team.fBreakdownChance))
            row.append(str(team.fCAC))
            row.append(str(team.iDistrictCode))
            row.append(str(team.percentRaise))
            row.append(str(team.numRaise))
            row.append(str(team.percentNav))
            row.append(str(team.percentHoist))
            row.append(str(team.blueBanners))
            row.append(str(team.silverMedals))
            row.append(str(team.bronzeButtons))
            row.append(str(team.numAutoNestAttempted))
            row.append(str(team.numAutoHullAttempted))
            row.append(str(team.numAutoDeckAttempted))
            row.append(str(team.numTeleNestAttempted))
            row.append(str(team.numTeleHullAttempted))
            row.append(str(team.numTeleDeckAttempted))
            writer.writerow(row)
    teamSave.close()
    with open('allleaderboards.csv','w',newline='') as lbSave:
        #print('Saving leaderboards...')
        writer = csv.writer(lbSave)
        leaderboardrows = []
        #print(leaderboard_list)
        for leaderboard in leaderboard_list:
            #print(leaderboard.sIdentifier)
            row = []
            row.append(leaderboard.sIdentifier)
            for team in leaderboard.teams:
                #print(team)
                row.append(team)
            row.append(int(-99999)) # pad with -99999
            for eventO in leaderboard.events:
                #print(eventO.sCode)
                row.append(eventO.sCode)
            row.append(int(-99999))
            for entry in leaderboard.leaderboard:
                #print(entry.teamNum)
                row.append(entry.teamNum)
                for score in entry.eventScores:
                    #print(score)
                    row.append(score)
                row.append(99999) # +99999 to pad
                #print(entry.dcmp)
                row.append(entry.dcmp)
                #print(entry.dcmpQ)
                row.append(entry.dcmpQ)
                #print(entry.champQ)
                row.append(entry.champQ)
                #print(entry.total)
                row.append(entry.total)
                row.append(-99998) # need to pad each entry
            row.append(-99999) # look for last -99999
            #print(leaderboard.isRegional)
            row.append(leaderboard.isRegional)
            leaderboardrows.append(row) # You have GOT to be kidding me
        #print(leaderboardrows)
        writer.writerows(leaderboardrows)
    lbSave.close() # Agh
                
    status = [[1]]
    with open('donotchange.csv','w',newline='') as statusFile:
        writer = csv.writer(statusFile)
        writer.writerows(status)

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError

def internal_fre(ranks,team):
    for rank in ranks:
        if int(str(rank.teamNum).strip()) == int(str(team).strip()):
            return rank

def ranks_from_quals():
    eventInput = input('Event code to parse: ')
    eventInput = eventInput.strip()
    if eventInput is None:
        print('Please input an event code.')
        pass
    qfileName = 'Official_Results/' + eventInput + 'Quals.csv'
    qrows = []
    with open(qfileName) as qFile:
        reader = csv.reader(qFile)
        for row in reader:
            qrows.append(row)
    qFile.close()
    qrows = qrows[1:] # drop first row
    teams = []
    ranks = []
    for qrow in qrows: # first pass to get list of teams and preload ranks
        for i in range(1,7):
            if int(qrow[i].strip()) not in teams:
                teams.append(int(qrow[i].strip()))
            else:
                continue
    for team in teams:
        thisEntry = RankEntry(team)
        ranks.append(thisEntry)
    # INDICES:
    # 7: Red Score/RP pips (•)
    # 8: Blue Score/RP pips (•)
    # 9: Result as string
    # 10: Red Nav
    # 11: Red Raise
    # 12: Red Deck
    # 13: Red Hull
    # 14: Red Nest
    # 15: Red Hoist
    # 16: Blue Nav
    # 17: Blue Raise
    # 18: Blue Deck
    # 19: Blue Hull
    # 20: Blue Nest
    # 21: Blue Hoist
    for qrow in qrows: # second pass to actually get ranks
        # print(qrow)
        redScoreString = qrow[7].strip()
        blueScoreString = qrow[8].strip()
        win_result = qrow[9].strip()
        redNav = int(qrow[10].strip())
        redRaise = float(qrow[11].strip())
        redDeck = int(qrow[12].strip())
        redHull = int(qrow[13].strip())
        redNest = int(qrow[14].strip())
        redHoist = int(qrow[15].strip())
        blueNav = int(qrow[16].strip())
        blueRaise = float(qrow[17].strip())
        blueDeck = int(qrow[18].strip())
        blueHull = int(qrow[19].strip())
        blueNest = int(qrow[20].strip())
        blueHoist = int(qrow[21].strip())
        redTeams = []
        blueTeams = []
        for i in range(1,4):
            redTeams.append(int(qrow[i].strip()))
            blueTeams.append(int(qrow[i+3].strip()))
        redBonusRP = redScoreString.count('•')
        blueBonusRP = blueScoreString.count('•')
        if redBonusRP > 0:  # if bullet character present in string
            red_totalScore = int(redScoreString[:redScoreString.find('•')])
        else:
            red_totalScore = int(redScoreString)
        if blueBonusRP > 0:
            blue_totalScore = int(blueScoreString[:blueScoreString.find('•')])
        else:
            blue_totalScore = int(blueScoreString)
        redwin = 0
        redloss = 0
        redtie = 0
        bluewin = 0
        blueloss = 0
        bluetie = 0
        if win_result.__eq__('TIE'):
            (redtie, bluetie) = (1, 1)
            red_totalRP = 1 + redBonusRP
            blue_totalRP = 1 + blueBonusRP
        elif win_result.__eq__('RED'):
            (redwin, blueloss) = (1, 1)
            red_totalRP = 2 + redBonusRP
            blue_totalRP = blueBonusRP
        else:  # result.__eq__('BLUE')
            (redloss, bluewin) = (1, 1)
            red_totalRP = redBonusRP
            blue_totalRP = 2 + blueBonusRP
        for redTeam,blueTeam in zip(redTeams,blueTeams):
            redRankEntry = internal_fre(ranks,redTeam)
            blueRankEntry = internal_fre(ranks,blueTeam)
            redRankEntry.update_entry(redwin,redloss,redtie,red_totalRP,red_totalScore,redNav,redRaise,redDeck,redHull,redNest,redHoist)
            blueRankEntry.update_entry(bluewin,blueloss,bluetie,blue_totalRP,blue_totalScore,blueNav,blueRaise,blueDeck,blueHull,blueNest,blueHoist)
    ranks.sort(key=lambda x: (-x.RS, -x.Nav, -x.Anch, -x.Deck, -x.Hull, -x.Nest, -x.Sail))
    rFileName = 'Official_Results/' + eventInput + 'Ranks.csv'
    with open(rFileName, 'w', newline='') as rfile:
        writer = csv.writer(rfile)
        rankNum = 1
        row1 = ['Rank', 'Team#', 'W', 'L', 'T', '#P', 'RP', 'Rank Score', 'Total Score', 'Nav', 'Anch', 'Deck', 'Hull',
                'Nest', 'Sail']
        writer.writerow(row1)
        for rank in ranks:
            row = [rankNum, rank.teamNum, rank.wins, rank.losses, rank.ties, rank.totalMatches, rank.RP, rank.RS,
                   rank.totalScore, rank.Nav, rank.Anch, rank.Deck, rank.Hull, rank.Nest, rank.Sail]
            rankNum += 1
            writer.writerow(row)
    rfile.close()
    print('Successfully generated Ranks from Qual results for ',eventInput)

def get_event_points():
    pass

def get_team_info():
    pass

def run_cmp_quali(type):
    if type == 0:
        pass
    else:
        # regional quali
        pass

# Main Program
preloaded = 0
with open('donotchange.csv') as statusFile:
    reader = csv.reader(statusFile)
    for row in reader:
        print(row)
        if row[0] == '1':
            preloaded = 1

event_row_list = []
epa_row_list = []
team_row_list = []
district_list = ['Regional','CHS','FIM','FIN','FIT','FMA','FNC','FSC','ISR','NE','ONT','PCH','PNW']
with open('eventlists_transposed.csv') as eventFile:
    reader = csv.reader(eventFile)
    for row in reader:
        event_row_list.append(row)
eventFile.close()
#print(event_row_list[0])
if (preloaded == 0):
    with open('2024_epa_breakdown.csv',encoding='utf8') as epaFile:
        reader2 = csv.reader(epaFile)
        for row in reader2:
            epa_row_list.append(row)
    epaFile.close()
    epa_row_list = epa_row_list[1:] # Dump first row
    #print(epa_row_list[0])
    with open('teams.csv',encoding='utf8') as teamFile:
        reader3 = csv.reader(teamFile)
        for row in reader3:
            team_row_list.append(row[:10]) #cut out extraneous registration debug values
    teamFile.close()
    team_row_list = team_row_list[1:] # Dump first row
    #print(team_row_list[0])
    #print('Length of where BRBR is in theory: ' + str(len(event_row_list[0][1]))) #grabs four, this is perfect
    #print(district_list)
    leaderboard_list = [] # for easy saving/loading
    regional_leaderboard = District('Regional')
    chs_leaderboard = District('CHS')
    fim_leaderboard = District('FIM')
    fin_leaderboard = District('FIN')
    fit_leaderboard = District('FIT')
    fma_leaderboard = District('FMA')
    fnc_leaderboard = District('FNC')
    fsc_leaderboard = District('FSC')
    isr_leaderboard = District('ISR')
    ne_leaderboard = District('NE')
    ont_leaderboard = District('ONT')
    pch_leaderboard = District('PCH')
    pnw_leaderboard = District('PNW')
    leaderboard_list.append(regional_leaderboard)
    leaderboard_list.append(chs_leaderboard)
    leaderboard_list.append(fim_leaderboard)
    leaderboard_list.append(fin_leaderboard)
    leaderboard_list.append(fit_leaderboard)
    leaderboard_list.append(fma_leaderboard)
    leaderboard_list.append(fnc_leaderboard)
    leaderboard_list.append(fsc_leaderboard)
    leaderboard_list.append(isr_leaderboard)
    leaderboard_list.append(ne_leaderboard)
    leaderboard_list.append(ont_leaderboard)
    leaderboard_list.append(pch_leaderboard)
    leaderboard_list.append(pnw_leaderboard)
    
    team_list = []
    bRookiesStarted = False
    for raw_team in team_row_list:
        team_num = raw_team[0]
        team_district = raw_team[5]
        if int(team_num) < 10000:
            epa_index = 0
            for entry in epa_row_list:
                if int(entry[0]) == int(team_num):
                    break
                epa_index += 1
            auto_notes = epa_row_list[epa_index][5]
            auto_points = epa_row_list[epa_index][6]
            speaker_notes = epa_row_list[epa_index][10]
            amp_notes = epa_row_list[epa_index][9]
            amplified_notes = epa_row_list[epa_index][11]
            park_points = epa_row_list[epa_index][13]
            onstage_points = epa_row_list[epa_index][14]
            trap_points = epa_row_list[epa_index][16]
        else:
            if bRookiesStarted == False:
                avg_auto_notes = col_avg(epa_row_list,5)
                avg_auto_points = col_avg(epa_row_list,6)
                avg_speaker_notes = col_avg(epa_row_list,10)
                avg_amp_notes = col_avg(epa_row_list,9)
                avg_amplified_notes = col_avg(epa_row_list,11)
                avg_park_points = col_avg(epa_row_list,13)
                avg_onstage_points = col_avg(epa_row_list,14)
                avg_trap_points = col_avg(epa_row_list,16)
                bRookiesStarted = True
            auto_notes = round(avg_auto_notes*(float(random.randint(5,10))/10.0),1)
            auto_points = round(avg_auto_points*(float(random.randint(5,10))/10.0),1)
            speaker_notes = round(avg_speaker_notes*(float(random.randint(5,10))/10.0),1)
            amp_notes = round(avg_amp_notes*(float(random.randint(5,10))/10.0),1)
            amplified_notes = round(avg_amplified_notes*(float(random.randint(5,10))/10.0),1)
            park_points = round(avg_park_points*(float(random.randint(5,10))/10.0),2)
            onstage_points = round(avg_onstage_points*(float(random.randint(5,10))/10.0),1)
            trap_points = round(avg_trap_points*(float(random.randint(5,10))/10.0),1)
            # Technically these run every time I set up the season which is why I'm trying to get this all saved to a file
        team_events = raw_team[6:] # list of events
        oTeam = Team(team_num,team_district,float(auto_notes),float(auto_points),float(speaker_notes),float(amp_notes),float(amplified_notes),float(park_points),float(onstage_points),float(trap_points),team_events)
        oTeam.cleanEventList()
        if team_district.__eq__('Regional'):
            regional_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('CHS'):
            chs_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIM'):
            fim_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIN'):
            fin_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIT'):
            fit_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FMA'):
            fma_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FNC'):
            fnc_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FSC'):
            fsc_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('ISR'):
            isr_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('NE'):
            ne_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('ONT'):
            ont_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('PCH'):
            pch_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('PNW'):
            pnw_leaderboard.teams.append(int(team_num))
        team_list.append(oTeam)
        #end of for loop
    
    for leaderboard in leaderboard_list:
        leaderboard.build_leaderboard_list() # internal
    leaderboard_list[0].isRegional = 1
# end if preload == 0
else:
    #print('Preloading from save...')
    teamSaveRows = []
    with open('allteams.csv') as teamSaveFile:
        saveReader1 = csv.reader(teamSaveFile)
        for row in saveReader1:
            teamSaveRows.append(row)
    teamSaveFile.close()
    team_list = [] # list of team OBJECTS
    for team_data in teamSaveRows:
        num = int(team_data[0]) 
        dist = team_data[1]
        f2024AN = float(team_data[2])
        f2024AP = float(team_data[3])
        f2024SN = float(team_data[4])
        f2024AM = float(team_data[5])
        f2024NA = float(team_data[6])
        f2024PP = float(team_data[7])
        f2024OP = float(team_data[8])
        f2024TP = float(team_data[9])
        tEL = []
        for i in range(6):
            if len(str(team_data[i+10]))>0:
                tEL.append(str(team_data[i+10]))
        # constructor done, create team now
        loadedTeam = Team(num,dist,f2024AN,f2024AP,f2024SN,f2024AM,f2024NA,f2024PP,f2024OP,f2024TP,tEL)
        # constructor defaults values, we override
        loadedTeam.bDistrict = str_to_bool(team_data[16])
        loadedTeam.iNumPrevEvents = int(team_data[17])
        loadedTeam.iDeltaLastEvent = int(team_data[18])
        loadedTeam.fBreakdownChance = float(team_data[19])
        loadedTeam.fCAC = float(team_data[20])
        loadedTeam.iDistrictCode = int(team_data[21])
        loadedTeam.percentRaise = float(team_data[22])
        loadedTeam.numRaise = float(team_data[23])
        loadedTeam.percentNav = float(team_data[24])
        loadedTeam.percentHoist = float(team_data[25])
        loadedTeam.blueBanners = int(team_data[26])
        loadedTeam.silverMedals = int(team_data[27])
        loadedTeam.bronzeButtons = int(team_data[28])
        loadedTeam.numAutoNestAttempted = int(team_data[29])
        loadedTeam.numAutoHullAttempted = int(team_data[30])
        loadedTeam.numAutoDeckAttempted = int(team_data[31])
        loadedTeam.numTeleNestAttempted = int(team_data[32])
        loadedTeam.numTeleHullAttempted = int(team_data[33])
        loadedTeam.numTeleDeckAttempted = int(team_data[34])
        # end of row
        team_list.append(loadedTeam)
    # end of for loop
    #print('Loaded {:4d} teams'.format(len(team_list)))
    # do leaderboards next / events?
    lbSaveRows = []
    with open('allleaderboards.csv') as lbSaveFile:
        saveReader2 = csv.reader(lbSaveFile)
        for row in saveReader2:
            lbSaveRows.append(row)
    lbSaveFile.close()
    leaderboard_list = []
    # We instantiate these on our own and as a bonus it tells us the correct order in the save file
    regional_leaderboard = District('Regional')
    chs_leaderboard = District('CHS')
    fim_leaderboard = District('FIM')
    fin_leaderboard = District('FIN')
    fit_leaderboard = District('FIT')
    fma_leaderboard = District('FMA')
    fnc_leaderboard = District('FNC')
    fsc_leaderboard = District('FSC')
    isr_leaderboard = District('ISR')
    ne_leaderboard = District('NE')
    ont_leaderboard = District('ONT')
    pch_leaderboard = District('PCH')
    pnw_leaderboard = District('PNW')
    leaderboard_list.append(regional_leaderboard)
    leaderboard_list.append(chs_leaderboard)
    leaderboard_list.append(fim_leaderboard)
    leaderboard_list.append(fin_leaderboard)
    leaderboard_list.append(fit_leaderboard)
    leaderboard_list.append(fma_leaderboard)
    leaderboard_list.append(fnc_leaderboard)
    leaderboard_list.append(fsc_leaderboard)
    leaderboard_list.append(isr_leaderboard)
    leaderboard_list.append(ne_leaderboard)
    leaderboard_list.append(ont_leaderboard)
    leaderboard_list.append(pch_leaderboard)
    leaderboard_list.append(pnw_leaderboard)
    for team in team_list:
        team_num = team.iTeamNum
        team_district = team.sDistrict.strip()
        if team_district.__eq__('Regional'):
            regional_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('CHS'):
            chs_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIM'):
            fim_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIN'):
            fin_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FIT'):
            fit_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FMA'):
            fma_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FNC'):
            fnc_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('FSC'):
            fsc_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('ISR'):
            isr_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('NE'):
            ne_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('ONT'):
            ont_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('PCH'):
            pch_leaderboard.teams.append(int(team_num))
        elif team_district.__eq__('PNW'):
            pnw_leaderboard.teams.append(int(team_num))

    for leaderboard,lbRow in zip(leaderboard_list,lbSaveRows):
        #print(lbRow)
        i = 0
        leaderboard.sIdentifier = lbRow[i]
        i += 2 # skip -99999
        teams = []
        while int(lbRow[i]) != -99999 and i < len(lbRow):
            teams.append(int(lbRow[i]))
            i += 1
        i += 1 # skip -99999
        eventCodes = []
        while (len(str(lbRow[i])) == 4 or len(str(lbRow[i])) == 5) and int(lbRow[i] != -99999):
            eventCodes.append(str(lbRow[i]))
            i += 1
        i += 2 # skip next -99999
        rowIsRegional = int(lbRow[-1])
        i += 1
        if i == len(lbRow):
            leaderboard.leaderboard = None
            continue
        entries = []
        while i < len(lbRow) and int(lbRow[i]) != -99999: # we padded with +99999 and -99998 so we should be fine here
            teamNum = int(lbRow[i]) # expecting teamNum of first entry here
            thisEntry = LeaderboardEntry(teamNum,rowIsRegional)
            while int(lbRow[i]) != 99999: #+99999
                thisEntry.eventScores.append(int(lbRow[i]))
                i += 1
            thisEntry.dcmp = int(lbRow[i])
            i += 1
            thisEntry.dcmpQ = int(lbRow[i])
            i += 1
            thisEntry.champQ = int(lbRow[i])
            i += 1
            thisEntry.total = int(lbRow[i])
            i += 1 # should be on the -99998 now, check
            if int(lbRow[i]) != -99998:
                print('Unexpected shift on entry %5d',teamNum)
            entries.append(thisEntry)
            i += 1 # repeat while loop
        leaderboard.teams = teams.copy()
        leaderboard.events = eventCodes.copy()
        leaderboard.leaderboard = entries.copy()
        leaderboard.isRegional = rowIsRegional
    # end of for loop
    leaderboard_list[0].isRegional = 1 # override because yes
    # need to fill empty entries
    for leaderboard in leaderboard_list:
        if leaderboard.leaderboard is None:
            leaderboard.leaderboard = []
            leaderboard.build_leaderboard_list()
#end else
event_list = preload_events(event_row_list)
sort_events(event_list,1)
sort_events(event_list,0)
#Opens menu for actual running
eventChoice = str('')
cChoice = ''
finished_events = []
in_progress_events = []
while True: 
    menu()
    cChoice = input('Enter choice --> ').strip()
    if cChoice is None:
        print('No entry detected. Please try again.')
        continue
    else:
        cChoice = cChoice[0]
    if cChoice == 'l': # load an event
        eventChoice = input('Enter Event Code: ').strip()
        if eventChoice in in_progress_events:
            eventRunning = EventRunner(eventChoice,leaderboard_list,event_list,team_list,1)
        else:
            eventRunning = EventRunner(eventChoice,leaderboard_list,event_list,team_list,0)
    elif cChoice == 'q': # Run quals at event
        eventRunning.run_quals()
    elif cChoice == 'p': # Print ranks at event
        eventRunning.print_ranks()
    elif cChoice == 'a': # Run Alliance Selection at event
        eventRunning.run_alliance_selection()
    elif cChoice == 'e': # Run Elims
        eventRunning.run_elims()
    elif cChoice == 'r': # Show results
        resultType = input('Enter q, a, or e for quals, alliance selection, and elims results, respectively: ')
        eventRunning.show_results(resultType)
    elif cChoice == 's': # Show points from event
        eventRunning.show_event_points()
    elif cChoice == 'i': # Save in-progress event
        eventCode = eventRunning.save_partial_event()
        in_progress_events.append(eventCode)
    elif cChoice == 'd': # Show district leaderboards
        display_leaderboards()
    elif cChoice == 'f': # Save event to csv
        eventRunning.save_event()
        finished_events.append(eventRunning)
    elif cChoice == 'b': # Batch save
        save_everything()
    elif cChoice == 'x': # Exit program
        sys.exit('User exit program.')
    elif cChoice == 'z': # Debug Menu
        debug_menu()
        debugChoice = input('Enter debug option--> ').strip()
        if debugChoice is None:
            continue
        else:
            debugChoice = debugChoice[0]
        if debugChoice == 'r': # ranks
            ranks_from_quals()
        elif debugChoice == 'p': # points
            get_event_points()
        elif debugChoice == 't': # team info
            get_team_info()
        elif debugChoice == 'q': # run dcmp/cmp quali
            run_cmp_quali(1) # hard-code to CMP for now (dcmps auto-run cmp quali so this is only for regional pools)
        else:
            print('Please enter valid debug choice.')
            continue
    else:
        print('Invalid choice, please try again.')
# end of program
