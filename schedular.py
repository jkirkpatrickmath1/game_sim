import random


def make_team(name):
    return {
        "name": name,
        "rp": 0,
        "auto": 0,
        "match": 0,
        "matches_played": 0
    }

def make_match(num, red, blue):
    return {
        "num": num,
        "red": red,     # list of team names
        "blue": blue
    }


def generate_matches(team_names, matches_per_team=4):
   
    matches = []
   
    team_play_counts = {name: 0 for name in team_names}
   
    match_num = 1
   
    while min(team_play_counts.values()) < matches_per_team:
       
        # set the smallest play count available
        min_play_count = min(team_play_counts.values())
       
        #list of teams that can play this 'round'
        available_teams = []
       
        #gets all available teams
        for names in team_play_counts:
            if team_play_counts[names] <= min_play_count:
                available_teams.append(names)
                # if len(available_teams) == 6:
                #     break
       
        #if we dont have enough teams
        print(available_teams)
        if len(available_teams) < 6:
            extras = [team for team in team_play_counts if team not in available_teams]
           
        # try to pick 3 teams for red alliance with no repeated teammates
        random.shuffle(available_teams)
       
        #sets up red team
        red = []
        #if first match fill first 3 teams
        if match_num == 1:
           
            red = [t for t in available_teams[0:3]]
           
        else:
           
            for t in available_teams:
               
                #if t not paired with anyone on the team from alst match
                if not (t in matches[-1]['red'] and any(r in matches[-1]['red'] for r in red)):
                    red.append(t)
                if len(red) == 3:
                    break
       
        #checks we have enough players, same as above but for extras
        if len(red) != 3:
            for team in extras:
                if not (t in matches[-1]['red'] and any(r in matches[-1]['red'] for r in red)):
                    red.append(team)
                if len(red) == 3:
                    break
       
   
        # remove chosen red from available teams
       
        for t in red:
            if t in available_teams:
                available_teams.remove(t)
            else:
                extras.remove(t)

        # pick 3 for blue alliance similarly
        blue = []
       
        #if first match fill first 3 teams
        if match_num == 1:
            blue = [t for t in available_teams[0:3]]
           
        else:
            #same as red but for blue
            for t in available_teams:
                if not (t in matches[-1]['blue'] and any(b in matches[-1]['blue'] for b in blue)):
                    blue.append(t)
                if len(blue) == 3:
                    break

        #checks we have enough players, red again
        if len(blue) != 3:
            for team in extras:
                if not (t in matches[-1]['blue'] and any(b in matches[-1]['blue'] for b in blue)):
                    blue.append(team)
                if len(blue) == 3:
                    break
               
        #okay,supder duper edge case were we dont have enough still
        if len(blue) != 3:
            for team in extras:
                if team not in blue:
                    blue.append(team)
                if len(blue) == 3:
                    break
   
       
        # increment play counts
        for t in red + blue:
            team_play_counts[t] += 1

        # create match
        new_match = make_match(match_num, red, blue)
        matches.append(new_match)
        match_num += 1
   
    #print(matches)
    return matches