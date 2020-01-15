from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import sys
#import time

# TODO: Team + Playerlists are done. Now get MMR from rlstats.com

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


def scrape_teams(tournament_url):
    # Initialize variables
    teams = []

    # Open URL to Teams-Overview
    main_url_toor = "https://www.toornament.com"
    #tournament_url = main_url_toor + "/en_US/tournaments/2859636902129573888"
    participants_url = tournament_url + "/participants/"
    driver.get(participants_url)

    # Extract data about Teams from website
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    for div in soup.findAll('div', attrs={'class':'size-1-of-4'}):
        team_name=div.find('div', attrs={'class':'name'})
        team_url=div.find('a', href=True)['href']

        teams.append(Team(team_name.text, team_url))

    nr_teams = len(teams) # Number of teams in tournament (int)

    teams_test = [teams[1], teams[2]]  # For test pruposes only use two teams

    tnr = 0  # Team-Nr used for indexing
    for team in teams_test:  # TODO: change teams_test to teams when done!
        #print("team.name="+str(team.name))

        # Open Team-Info-URL
        team_info_url = main_url_toor + team.url + "info"
        #print("team_info_url="+team_info_url)
        driver.get(team_info_url)

        # Extract Players data
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        largesoup = soup.findAll('div', attrs={'class':'grid-flex vertical spacing-tiny'})
        smallsoup = list(filter(None, largesoup))

        pnr = 0  # Player-Nr used for indexing
        for div in smallsoup:
            # Problem: 'grid-flex vertical spacing-tiny' tag is not exclusively used for player data! Sometimes = 'None'
            if div.find('div', attrs={'class': 'text secondary small steam_player_id'}) is not None:  # Workaround
                # Player found! Save it!
                name = div.find('div', attrs={'class':'text bold'}).text
                steamid = div.find('div', attrs={'class':'text secondary small steam_player_id'}).text
                xboxgt = div.find('div', attrs={'class': 'text secondary small xbox_live_player_id'}).text
                psnid = div.find('div', attrs={'class': 'text secondary small psn_player_id'}).text
                nintendoid = div.find('div', attrs={'class': 'text secondary small nintendo_network_player_id'}).text

                # Delete spaces, line breaks and other garbage and append to list
                name = name.replace('\n', ' ').replace('\r', '').replace(" ", "")
                steamid = steamid.replace(' Steam ID (ausschließlich Steam64Id):','').replace('\n', ' ').replace('\r', '').replace(" ", "")
                xboxgt = xboxgt.replace(' Xbox Live Gamertag:','').replace('\n', ' ').replace('\r', '').replace(" ", "")
                psnid = psnid.replace(' PSN ID:', '').replace('\n', ' ').replace('\r','').replace(" ", "")
                nintendoid = nintendoid.replace(' Nintendo Network ID:', '').replace('\n', ' ').replace('\r', '').replace(" ", "")

                team.players.append(Player(name, team, steamid, xboxgt, psnid, nintendoid))

                pnr = pnr + 1
        team.nr_players = pnr
        tnr = tnr + 1
    return teams_test  # TODO: change teams_test to teams when done!


def scrape_stats(teams):
    trackernet_url = "https://rocketleague.tracker.network"
    for the_team in teams:
        for the_player in the_team.players:
            best_id_type = '-'
            player_trn_url = '-'

            if len(the_player.steam_id) > 4:
                player_trn_url = trackernet_url + "/profile/steam/" + the_player.steam_id
                best_id_type = "steam"
            elif the_player.xbox_id != '-' and the_player.xbox_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/xbox/" + the_player.xbox_id
                best_id_type = "xbox"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/ps/" + the_player.psn_id
                best_id_type = "psn"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                player_trn_url = trackernet_url + "/profile/ps/" + the_player.psn_id
                best_id_type = "nintendo"
            else:
                print("Player " + the_player.name + " in Team " + the_team.name + " has no valid ID!")

            if best_id_type != '-':
                # Open TRN-Player-Website
                driver.get(player_trn_url)

                # Extract Players data
                content = driver.page_source
                soup = BeautifulSoup(content, features="html.parser")

                # TODO: Get Player MMR and Stats

                # TODO: Save MMR and Stats in Player-Object

                # TODO: return Teams-Object with all changes in players


#def export_to_csv(teams_to_export):
    # TODO: use panda to export to csv


# Test Function
allTeams = scrape_teams("https://www.toornament.com/en_US/tournaments/2859636902129573888")

for theTeam in allTeams:
    print("Team-Name = " + theTeam.name)
    for thePlayer in theTeam.players:
        print(" Player-Name = " + thePlayer.name)
        print(" Player-SteamID = " + thePlayer.steam_id)
        print(" Player-xboxID = " + thePlayer.xbox_id)
        print(" Player-psnID = " + thePlayer.psn_id)
        print(" Player-NintendoID = " + thePlayer.nintendo_id)
    print()

#export_to_csv(allTeams)
