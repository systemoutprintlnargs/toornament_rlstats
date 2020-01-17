from selenium import webdriver
from bs4 import BeautifulSoup
# import pandas as pd
import os
# import sys
# import time
import csv

# Get directory path and chromedriver.exe
dir_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
cd_path = dir_parent_path.replace('\\', '/') + '/_ExternalFiles/chromedriver.exe'
print(cd_path)
driver = webdriver.Chrome(executable_path=cd_path)


# Classes
class Team:
    def __init__(self, name, url):
        self.name = name
        self.url = url

        self.nr_players = []
        self.players = []
        self.league = []


class Player:
    def __init__(self, name, team, steam_id, xbox_id, psn_id, nintendo_id):
        self.name = name
        self.team = team
        self.steam_id = steam_id
        self.xbox_id = xbox_id
        self.psn_id = psn_id
        self.nintendo_id = nintendo_id

        self.url = []
        self.mmr_3v3 = []
        self.mmr_2v2 = []
        self.mmr_1v1 = []
        self.mmr_3v3s = []


# Function to get team and player information from toornament.com
# Returns teams (an array of <Team> objects, which contain corresponding player information)
def scrape_teams(tournament_url):
    # TODO: Add league to teams (1, 2, 3)
    print("scrape_teams() started...")
    # Initialize variables
    teams = []

    # Open URL to Teams-Overview
    main_url_toor = "https://www.toornament.com"
    participants_url = tournament_url + "/participants/"

    # Extract data about Teams from website
    # TODO: Better to check for 404...
    page = 0
    while page > -1:
        page = page + 1
        print("   Scraping page" + str(page) + " of participants website.")
        participants_page_url = participants_url + "?page=" + str(page)
        driver.get(participants_page_url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        errorsoup = soup.find('li', attrs={'class': 'arrow next disabled'})

        for div in soup.findAll('div', attrs={'class': 'size-1-of-4'}):
            team_name = div.find('div', attrs={'class': 'name'})
            team_url = div.find('a', href=True)['href']

            teams.append(Team(team_name.text, team_url))  # adds Team object to the return variable

        if errorsoup is not None:
            print("   Page" + str(page) + " was the last page.")
            page = -1
            break

    # teams_test = [teams[1], teams[2]]  # TODO: change teams_test to teams when done!
    teams_test = teams  # TODO: change teams_test to teams when done!

    print("   Scraping players in teams...")
    tnr = 0  # Team-Nr used for indexing
    for team in teams_test:  # TODO: change teams_test to teams when done!
        print("      Scraping players in team " + team.name + " with team-nr " + str(tnr))

        # Open Team-Info-URL
        team_info_url = main_url_toor + team.url + "info"
        driver.get(team_info_url)

        # Extract Players data
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        largesoup = soup.findAll('div', attrs={'class': 'grid-flex vertical spacing-tiny'})  # finds player-data
        smallsoup = list(filter(None, largesoup))  # throws out None-Objects

        pnr = 0  # Player-Nr used for indexing
        for div in smallsoup:
            # Problem: 'grid-flex vertical spacing-tiny' tag is not exclusively used for player data! Sometimes = 'None'
            if div.find('div', attrs={'class': 'text secondary small steam_player_id'}) is not None:  # Workaround
                # Player found! Get relevant data and save it!
                name = div.find('div', attrs={'class': 'text bold'}).text
                steamid = div.find('div', attrs={'class': 'text secondary small steam_player_id'}).text
                xboxgt = div.find('div', attrs={'class': 'text secondary small xbox_live_player_id'}).text
                psnid = div.find('div', attrs={'class': 'text secondary small psn_player_id'}).text
                nintendoid = div.find('div', attrs={'class': 'text secondary small nintendo_network_player_id'}).text

                # Delete spaces, line breaks and other garbage
                name = name.replace('\n', ' ').replace('\r', '').replace(" ", "").replace(";", "-")
                steamid = steamid.replace(' Steam ID (ausschließlich Steam64Id):', '')\
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")
                xboxgt = xboxgt.replace(' Xbox Live Gamertag:', '')\
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")
                psnid = psnid.replace(' PSN ID:', '').replace('\n', ' ').replace('\r', '').replace(" ", "")
                nintendoid = nintendoid.replace(' Nintendo Network ID:', '')\
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")

                # Add this player to this team's players-list
                team.players.append(Player(name, team, steamid, xboxgt, psnid, nintendoid))

                pnr = pnr + 1
        team.nr_players = pnr
        tnr = tnr + 1
    print("All teams successfully scraped for players.")
    print("\n")
    return teams_test  # TODO: change teams_test to teams when done!


# Returns player-stats found on rl-trackernetwork for a list of teams
def scrape_stats(teams):
    print("Starting to scrape stats for players...")
    trackernet_url = "https://rocketleague.tracker.network"
    for the_team in teams:
        print("   Scraping stats for players in team " + the_team.name + ".")
        for the_player in the_team.players:
            best_id_type = '-'
            the_player.url = '-'

            # If Steam-ID is available for this player, this should be used. If not, use another ID available.
            if len(the_player.steam_id) > 4:
                the_player.url = trackernet_url + "/profile/mmr/steam/" + the_player.steam_id
                best_id_type = "steam"
            elif the_player.xbox_id != '-' and the_player.xbox_id != 'n/a':
                the_player.url = trackernet_url + "/profile/mmr/xbox/" + the_player.xbox_id
                best_id_type = "xbox"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                the_player.url = trackernet_url + "/profile/mmr/ps/" + the_player.psn_id
                best_id_type = "psn"
            elif the_player.psn_id != '-' and the_player.psn_id != 'n/a':
                the_player.url = trackernet_url + "/profile/mmr/ps/" + the_player.psn_id
                best_id_type = "nintendo"
            else:
                print("Player " + the_player.name + " in Team " + the_team.name + " has no valid ID!")

            if best_id_type != '-':
                print("      Getting player MMR for " + the_player.name + " with url " + the_player.url)
                # Open TRN-Player-Website
                driver.get(the_player.url)

                # Extract Players data
                content = driver.page_source
                soup = BeautifulSoup(content, features="html.parser")

                # TODO: Make getting down to the final soup shorter...
                errorsoup = soup.find('div', attrs={'id': 'header'})
                if errorsoup is not None:
                    errorsoup = errorsoup.find('h1').text
                    if errorsoup == "Server Error":
                        the_player.mmr_1v1 = str(-2)
                        the_player.mmr_2v2 = str(-2)
                        the_player.mmr_3v3s = str(-2)
                        the_player.mmr_3v3 = str(-2)

                        print("Error for " + the_player.name + " in " + the_team.name + ". Can't access TRN.")
                else:
                    soup = soup.find('div', attrs={'class': 'trn-profile'}).find('div', attrs={'class': 'profile-main'})
                    soup = soup.find('div', attrs={'class': 'content'}).find('div', attrs={'class': 'row'})
                    soup = soup.find('div', attrs={'class': 'col-md-3'}).find('div', attrs={'class': 'card card-list'})

                    try:
                        the_player.mmr_1v1 = soup.find('a', attrs={'data-id': '10'})\
                                                    .find('span', attrs={'class': 'badge'}).text
                    except AttributeError:
                        the_player.mmr_1v1 = -3
                    try:
                        the_player.mmr_2v2 = soup.find('a', attrs={'data-id': '11'})\
                                                    .find('span', attrs={'class': 'badge'}).text
                    except AttributeError:
                        the_player.mmr_2v2 = -3
                    try:
                        the_player.mmr_3v3s = soup.find('a', attrs={'data-id': '12'})\
                                                    .find('span', attrs={'class': 'badge'}).text
                    except AttributeError:
                        the_player.mmr_3v3s = -3
                    try:
                        the_player.mmr_3v3 = soup.find('a', attrs={'data-id': '13'})\
                                                    .find('span', attrs={'class': 'badge'}).text
                    except AttributeError:
                        the_player.mmr_3v3 = -3

            else:
                the_player.mmr_1v1 = "-1"
                the_player.mmr_2v2 = "-1"
                the_player.mmr_3v3s = "-1"
                the_player.mmr_3v3 = "-1"
    print("Stats for all players in teams successfully scraped.")
    print("\n")
    return teams


# TODO: use panda to re-format data
# def panda_format(teams):

# TODO: format teams-object into csv-file and export
def export_teams_to_csv(all_teams, csv_file_name, save_directory):
    print("Exporting to CSV...")
    csv_success = True
    # Create CSV-file and start writing
    writer = csv.writer(
        open(save_directory + csv_file_name, 'w', newline=''), delimiter=';')

    writer.writerow(['Team'] + ["Team-URL"] + ["Player"] + ["TRN-URL"] + ["MMR 1v1"] + ["MMR 2v2"] + ["MMR 3v3s"] +
                    ["MMR 3v3"])
    for team in all_teams:
        for player in team.players:
            try:
                writer.writerow([team.name] + [team.url] + [player.name] + [player.url] +
                                [player.mmr_1v1] + [player.mmr_2v2] + [player.mmr_3v3s] + [player.mmr_3v3])
            except UnicodeEncodeError:
                print("Export error in player " + player.name + ". Check URL " + player.url)
                print(team.name + ';' + team.url + ';' + player.name + ';' + player.url + ';' +
                      player.mmr_1v1 + ';' + player.mmr_2v2 + ';' + player.mmr_3v3s + ';' + player.mmr_3v3)
                writer.writerow([team.name] + [team.url] + [player.name] + [player.url] +
                                [player.mmr_1v1] + [player.mmr_2v2] + [player.mmr_3v3s] + [player.mmr_3v3])
    print("Successfully exported to CSV.")
    print("\n")
    return csv_success


# def import_teams_from_csv(csv_file_path)
# TODO: Add function that can re-create teams-list with players from CSV-file so web-scraping not necessary every time
