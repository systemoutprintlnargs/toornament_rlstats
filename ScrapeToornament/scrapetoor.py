from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
#import time

# TODO: Team + Playerlists are done. Now get MMR from rlstats.com

# Get directory path and chromedriver.exe
dir_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
cd_path = dir_parent_path.replace('\\', '/') + '/_ExternalFiles/chromedriver.exe'
driver = webdriver.Chrome(executable_path=cd_path)


# Classes
class Team:
    def __init__(self, name, url):
        self.name = name
        self.url = url

        self.nr_players = []
        self.players = []


class Player:
    def __init__(self, name, team, steam_id, xbox_id, psn_id, nintendo_id):
        self.name = name
        self.team = team
        self.steam_id = steam_id
        self.xbox_id = xbox_id
        self.psn_id = psn_id
        self.nintendo_id = nintendo_id

        self.mmr_3v3 = []
        self.mmr_2v2 = []
        self.mmr_1v1 = []
        self.mmr_3v3s = []


# Function to get team and player information from toornament.com
# Returns teams (an array of <Team> objects, which contain corresponding player information)
def scrape_teams(tournament_url):
    # Initialize variables
    teams = []

    # Open URL to Teams-Overview
    main_url_toor = "https://www.toornament.com"
    participants_url = tournament_url + "/participants/"
    driver.get(participants_url)

    # Extract data about Teams from website
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    for div in soup.findAll('div', attrs={'class':'size-1-of-4'}):
        team_name=div.find('div', attrs={'class':'name'})
        team_url=div.find('a', href=True)['href']

        teams.append(Team(team_name.text, team_url))  # adds Team object to the return variable

    teams_test = teams  # [teams[1], teams[2]]  # TODO: change teams_test to teams when done!

    tnr = 0  # Team-Nr used for indexing
    for team in teams_test:  # TODO: change teams_test to teams when done!
        # Open Team-Info-URL
        team_info_url = main_url_toor + team.url + "info"
        driver.get(team_info_url)

        # Extract Players data
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        largesoup = soup.findAll('div', attrs={'class':'grid-flex vertical spacing-tiny'})  # finds player-data
        smallsoup = list(filter(None, largesoup))  # throws out None-Objects

        pnr = 0  # Player-Nr used for indexing
        for div in smallsoup:
            # Problem: 'grid-flex vertical spacing-tiny' tag is not exclusively used for player data! Sometimes = 'None'
            if div.find('div', attrs={'class': 'text secondary small steam_player_id'}) is not None:  # Workaround
                # Player found! Get relevant data and save it!
                name = div.find('div', attrs={'class':'text bold'}).text
                steamid = div.find('div', attrs={'class':'text secondary small steam_player_id'}).text
                xboxgt = div.find('div', attrs={'class': 'text secondary small xbox_live_player_id'}).text
                psnid = div.find('div', attrs={'class': 'text secondary small psn_player_id'}).text
                nintendoid = div.find('div', attrs={'class': 'text secondary small nintendo_network_player_id'}).text

                # Delete spaces, line breaks and other garbage
                name = name.replace('\n', ' ').replace('\r', '').replace(" ", "")
                steamid = steamid.replace(' Steam ID (ausschließlich Steam64Id):','').replace('\n', ' ').replace('\r', '').replace(" ", "")
                xboxgt = xboxgt.replace(' Xbox Live Gamertag:','').replace('\n', ' ').replace('\r', '').replace(" ", "")
                psnid = psnid.replace(' PSN ID:', '').replace('\n', ' ').replace('\r','').replace(" ", "")
                nintendoid = nintendoid.replace(' Nintendo Network ID:', '').replace('\n', ' ').replace('\r', '').replace(" ", "")

                # Add this player to this team's players-list
                team.players.append(Player(name, team, steamid, xboxgt, psnid, nintendoid))

                pnr = pnr + 1
        team.nr_players = pnr
        tnr = tnr + 1
    return teams_test  # TODO: change teams_test to teams when done!


# Returns player-stats found on rl-trackernetwork for a list of teams
def scrape_stats(teams):
    trackernet_url = "https://rocketleague.tracker.network"
    for the_team in teams:
        for the_player in the_team.players:
            best_id_type = '-'
            player_trn_url = '-'

            # If Steam-ID is available for this player, this should be used. If not, use another ID available.
            if len(the_player.steam_id) > 4:
                player_trn_url = trackernet_url + "/profile/mmr/steam/" + the_player.steam_id
                best_id_type = "steam"
            elif the_player.xbox_id != '-' and the_player.xbox_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/mmr/xbox/" + the_player.xbox_id
                best_id_type = "xbox"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/mmr/ps/" + the_player.psn_id
                best_id_type = "psn"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/mmr/ps/" + the_player.psn_id
                best_id_type = "nintendo"
            else:
                print("Player " + the_player.name + " in Team " + the_team.name + " has no valid ID!")

            if best_id_type != '-':
                # Open TRN-Player-Website
                driver.get(player_trn_url)

                # Extract Players data
                content = driver.page_source
                soup = BeautifulSoup(content, features="html.parser")

                # TODO: Make getting down to the final soup shorter...
                soup = soup.find('div', attrs={'class': 'trn-profile'}).find('div', attrs={'class': 'profile-main'})
                # TODO: https://rocketleague.tracker.network/profile/mmr/xbox/EviRaXEN ist 404 -> soup = NoneType
                soup = soup.find('div', attrs={'class': 'content'}).find('div', attrs={'class': 'row'})
                soup = soup.find('div', attrs={'class': 'col-md-3'}).find('div', attrs={'class': 'card card-list'})

                the_player.mmr_1v1 = soup.find('a', attrs={'data-id': '10'}).find('span', attrs={'class': 'badge'}).text
                the_player.mmr_2v2 = soup.find('a', attrs={'data-id': '11'}).find('span', attrs={'class': 'badge'}).text
                the_player.mmr_3v3s = soup.find('a', attrs={'data-id': '12'}).find('span', attrs={'class': 'badge'}).text
                the_player.mmr_3v3 = soup.find('a', attrs={'data-id': '13'}).find('span', attrs={'class': 'badge'}).text

            else:
                the_player.mmr_1v1 = "-1"
                the_player.mmr_2v2 = "-1"
                the_player.mmr_3v3s = "-1"
                the_player.mmr_3v3 = "-1"
    return teams


#def export_to_csv(teams_to_export):
    # TODO: use panda to export to csv


# Test Function
teams_toor = scrape_teams("https://www.toornament.com/en_US/tournaments/2859636902129573888")
# for theTeam in allTeams:
#     print("Team-Name = " + theTeam.name)
#     for thePlayer in theTeam.players:
#         print(" Player-Name = " + thePlayer.name)
#         print(" Player-SteamID = " + thePlayer.steam_id)
#         print(" Player-xboxID = " + thePlayer.xbox_id)
#         print(" Player-psnID = " + thePlayer.psn_id)
#         print(" Player-NintendoID = " + thePlayer.nintendo_id)
#     print()

# allTeams = []
# allTeams.append(Team("Test Team", "www.testteam_notreal.de"))
# allTeams[0].players.append(Player("Scrub Killa", allTeams[0], "76561198089298636", "-", "-", "-"))

teams_final = scrape_stats(teams_toor)

for theTeam in teams_final:
    print("Team-Name = " + theTeam.name)
    for thePlayer in theTeam.players:
        print("   Player-Name = " + thePlayer.name)
        print("      MMR_1v1 = " + thePlayer.mmr_1v1)
        print("      MMR_2v2 = " + thePlayer.mmr_2v2)
        print("      MMR_3v3s = " + thePlayer.mmr_3v3s)
        print("      MMR_3v3 = " + thePlayer.mmr_3v3)
    print()

#export_to_csv(allTeams)
