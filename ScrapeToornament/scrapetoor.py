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
driver = webdriver.Chrome(executable_path=cd_path)

main_url_toor = "https://www.toornament.com"
trackernet_url = "https://rocketleague.tracker.network"


# Classes
class Tournament:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.stages = []
        self.teams = []

    def set_teams(self, teams):
        self.teams = teams

    # Function to get all sub-tournaments in a tournament
    def scrape_tournament_stages(self):
        # TODO: Add function to scrape stages for this tournament
        stages_url = self.url + '/stages/'
        driver.get(stages_url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")
        stages_soup = soup.find('div', attrs={'class': 'grid-flex mobile-vertical spacing-large'})
        stages_soup = stages_soup.findAll('div', attrs={'class': 'size-1-of-3 tablet-size-1-of-2 mobile-size-full'})
        
        for div in stages_soup:
            stage_url = div.find('a', href=True)['href'].text
            stage_name = div.find('div', attrs={'class': 'title'})
            stage_type = div.find('div', attrs={'class': 'item'})[0] # Does it work like this?
            stage_nteams = div.find('div', attrs={'class': 'item'})[1] # Does it work like this?
            
            newstage = Stage(stage_name, stage_url)
            newstage.type = stage_type
            newstage.nteams = stage_nteams
            self.stages.append(newstage)
            # TODO: test this function up until here

class Stage:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.type = []
        self.nteams = []
        self.teams = []

class Team:
    def __init__(self, name, url):
        self.name = name
        self.url = url

        self.nr_players = []
        self.players = []
        self.league = []

    def scrape_players(self):
        print("Scraping players in team " + self.name)

        # Open Team-Info-URL
        driver.get(self.url)

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
                steamid = steamid.replace(' Steam ID (ausschließlich Steam64Id):', '') \
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")
                xboxgt = xboxgt.replace(' Xbox Live Gamertag:', '') \
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")
                psnid = psnid.replace(' PSN ID:', '').replace('\n', ' ').replace('\r', '').replace(" ", "")
                nintendoid = nintendoid.replace(' Nintendo Network ID:', '') \
                    .replace('\n', ' ').replace('\r', '').replace(" ", "")

                # Add this player to this team's players-list
                self.players.append(Player(name, self, steamid, xboxgt, psnid, nintendoid))

                pnr = pnr + 1
        self.nr_players = pnr


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

    def scrape_stats(self):
        best_id_type = '-'
        self.url = '-'

        # If Steam-ID is available for this player, this should be used. If not, use another ID available.
        if len(self.steam_id) > 4:
            self.url = trackernet_url + "/profile/mmr/steam/" + self.steam_id
            best_id_type = "steam"
        elif self.xbox_id != '-' and self.xbox_id != 'n/a':
            self.url = trackernet_url + "/profile/mmr/xbox/" + self.xbox_id
            best_id_type = "xbox"
        elif self.psn_id != '-' and self.psn_id != 'n/a':
            self.url = trackernet_url + "/profile/mmr/ps/" + self.psn_id
            best_id_type = "psn"
        elif self.psn_id != '-' and self.psn_id != 'n/a':
            self.url = trackernet_url + "/profile/mmr/ps/" + self.psn_id
            best_id_type = "nintendo"
        else:
            print("Player " + self.name + " in Team " + self.team.name + " has no valid ID!")

        if best_id_type != '-':
            print("      Scraping player MMR for " + self.name + " with url " + self.url)
            # Open TRN-Player-Website
            driver.get(self.url)

            # Extract Players data
            content = driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            errorsoup = soup.find('div', attrs={'id': 'header'})
            if errorsoup is not None:
                errorsoup = errorsoup.find('h1').text
                if errorsoup == "Server Error":
                    self.mmr_1v1 = str(-2)
                    self.mmr_2v2 = str(-2)
                    self.mmr_3v3s = str(-2)
                    self.mmr_3v3 = str(-2)

                    print("Error for " + self.name + " in " + self.team.name + ". Can't access TRN.")

            # TODO: Make getting down to the final soup shorter...
            else:
                soup = soup.find('div', attrs={'class': 'trn-profile'}).find('div',
                                                                             attrs={'class': 'profile-main'})
                soup = soup.find('div', attrs={'class': 'content'}).find('div', attrs={'class': 'row'})
                soup = soup.find('div', attrs={'class': 'col-md-3'}).find('div',
                                                                          attrs={'class': 'card card-list'})

                try:
                    self.mmr_1v1 = soup.find('a', attrs={'data-id': '10'}).find('span', attrs={'class': 'badge'}).text
                except AttributeError:
                    self.mmr_1v1 = -3
                try:
                    self.mmr_2v2 = soup.find('a', attrs={'data-id': '11'}).find('span', attrs={'class': 'badge'}).text
                except AttributeError:
                    self.mmr_2v2 = -3
                try:
                    self.mmr_3v3s = soup.find('a', attrs={'data-id': '12'}).find('span', attrs={'class': 'badge'}).text
                except AttributeError:
                    self.mmr_3v3s = -3
                try:
                    self.mmr_3v3 = soup.find('a', attrs={'data-id': '13'}).find('span', attrs={'class': 'badge'}).text
                except AttributeError:
                    self.mmr_3v3 = -3

        else:
            self.mmr_1v1 = "-1"
            self.mmr_2v2 = "-1"
            self.mmr_3v3s = "-1"
            self.mmr_3v3 = "-1"


# Function to get team and player information from toornament.com
# Returns teams (an array of <Team> objects with Team-Name and URL)
def scrape_teams_from_participants_website(participants_url):
    # Extract data about Teams from website
    teams = []
    page = 0
    while True:
        page = page + 1
        print("   Scraping page " + str(page) + " of teams website.")
        participants_page_url = participants_url + "?page=" + str(page)
        driver.get(participants_page_url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        # Check if there are more pages
        errorsoup = soup.find('ul', attrs={'class': 'pagination-nav'})  # No navigation = only one page
        if errorsoup is None:
            errorsoup = 1
        else:
            errorsoup = soup.find('li', attrs={'class': 'arrow next disabled'})  # No further pages

        for div in soup.findAll('div', attrs={'class': 'size-1-of-4'}):
            team_name = div.find('div', attrs={'class': 'name'})
            team_url = main_url_toor + div.find('a', href=True)['href'] + "info"

            teams.append(Team(team_name.text, team_url))  # adds Team object to the return variable

        if errorsoup is not None:
            print("   Page" + str(page) + " was the last page.")
            break
    return teams


# TODO: use panda to re-format data
# def panda_format(teams):


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
            except UnicodeEncodeError:  # Some players enter Chinese symbols etc...
                print("Export error in player with URL " + player.url)
                writer.writerow([team.name] + [team.url] + ['NON-ASCII-ERROR'] + [player.url] +
                                [player.mmr_1v1] + [player.mmr_2v2] + [player.mmr_3v3s] + [player.mmr_3v3])
    print("Successfully exported to CSV.")
    print("\n")
    return csv_success


def import_teams_from_csv(csv_file_path):
    # Open CSV-File:
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')

        teams = []
        row_nr = 0
        last_team_name = ""
        for row in reader:
            if row_nr > 0:  # First row contains column titles
                this_team_name = row[0]
                if this_team_name != last_team_name:
                    # Get team info
                    # print("Importing team " + this_team_name)
                    team_url = row[1]
                    new_team = Team(this_team_name, team_url)
                    teams.append(new_team)
                # Get player-info
                new_player = Player(row[2], new_team, '-', '-', '-', '-')
                # ID is stored in URL...
                id_type = row[3].split('/')[len(row[3].split('/')) - 2]
                player_id = row[3].split('/')[len(row[3].split('/')) - 1]
                if id_type == 'steam':
                    new_player.steam_id = player_id
                else:
                    if id_type == 'xbox':
                        new_player.xbox_id = player_id
                    else:
                        if id_type == 'ps':
                            new_player.psn_id = player_id
                # print('   Importing ' + new_player.name + ' with id_type ' + id_type + ' and ID ' + player_id)
                new_team.players.append(new_player)

                last_team_name = this_team_name
            row_nr = row_nr + 1
    return teams
