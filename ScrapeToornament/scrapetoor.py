from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
# import pandas as pd
import os
# import sys
# import time
import csv
import platform

# Get directory path and chromedriver.exe
dir_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
operating_system = platform.system()
print('OS found: ' + operating_system)
if operating_system == 'Windows':
    cd_path = dir_parent_path.replace('\\', '/') + '/_ExternalFiles/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=cd_path)
elif operating_system == 'Linux':
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    cd_path = dir_parent_path.replace('\\', '/') + '/_ExternalFiles/chromedriver'
    driver = webdriver.Chrome(executable_path=cd_path,  chrome_options=chrome_options)

main_url_toor = "https://www.toornament.com"
trackernet_url = "https://rocketleague.tracker.network"


# Classes
class Tournament:
    def __init__(self, **kwargs):
        # args -- tuple of anonymous arguments
        # kwargs -- dictionary of named arguments
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.game = kwargs.get('game')
        self.organizer = kwargs.get('organizer')
        self.location = kwargs.get('location')
        self.startdate = kwargs.get('startdate')
        self.enddate = kwargs.get('enddate')
        self.website = kwargs.get('website')
        self.perc_played = kwargs.get('perc_played')
        self.nteams = kwargs.get('nteams')

        self.stages = []
        self.teams = []

    def set_teams(self, teams):
        self.teams = teams
    
    # Function to get all sub-tournaments in a tournament
    def scrape_tournament_stages(self):
        stages_url = self.url + 'stages/'
        driver.get(stages_url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")
        stages_soup = soup.find('div', attrs={'class': 'grid-flex mobile-vertical spacing-large'})
        stages_soup = stages_soup.findAll('div', attrs={'class': 'size-1-of-3 tablet-size-1-of-2 mobile-size-full'})

        # Go through all stages and scrape their info
        for div in stages_soup:
            stage_url = main_url_toor + div.find('a', href=True)['href']
            stage_name = div.find('div', attrs={'class': 'title'}).text
            stage_type = div.findAll('div', attrs={'class': 'item'})[0].text

            teams_divs = div.findAll('div', attrs={'class': 'item'})[1].text
            # teams_divs is a bit weirdly formatted, needs some reformatting:
            teams_divs = teams_divs.replace('\n', "").replace(" ", "")
            teams_stringpos = teams_divs.find('Team')
            divs_stringpos = teams_divs.find('Division')
            if teams_stringpos > -1:
                stage_nteams = int(teams_divs[:(teams_stringpos)])
            else:
                stage_nteams = 0
            if divs_stringpos > -1:
                stage_ndivs = int(teams_divs[(teams_stringpos + 6):(divs_stringpos)])
            else:
                stage_ndivs = 1

            # Create new stage object and append to Tournament
            newstage = Stage(stage_name, stage_url)
            newstage.tournament = self
            newstage.type = stage_type
            newstage.nteams = stage_nteams
            newstage.ndivisions = stage_ndivs
            # TODO: Add divisions to stages
            self.stages.append(newstage)

        for stg in self.stages:
            stg.scrape_teams_in_stage()
            print('Scraping done, found these teams in stage:')
            for t in stg.teams:
                print(t.name)


class Stage:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.tournament = []
        self.type = []
        self.nteams = []
        self.ndivisions = []
        self.teams = []

    def scrape_teams_in_stage(self):
        print('Scraping teams in Stage ' + self.name)

        # Open stage url
        driver.get(self.url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        if self.type == 'Double Elimination':
            nodes_soup = soup.find('div', attrs={'class': 'bracket-nodes'})

            # Go through nodes and find new teams -> add to list
            team_names = []
            for node in nodes_soup:
                t1 = node.find('div', attrs={'class': 'opponent opponent-1'}).find('div', attrs={'class': 'name'}).text.strip()
                t2 = node.find('div', attrs={'class': 'opponent opponent-2'}).find('div', attrs={'class': 'name'}).text.strip()
                t1_found = False
                t2_found = False
                for t in team_names:
                    if t == t1:
                        t1_found = True
                    if t == t2:
                        t2_found = True
                if not t1_found:
                    team_names.append(t1)
                if not t2_found:
                    team_names.append(t2)

            # List with unique team names is done, now find respective team objects
            for tname in team_names:
                for team in self.tournament.teams:
                    if team.name == tname:
                        self.teams.append(team)

        if self.type == 'League':
            # TODO: Set up divisions in stage
            # TODO: Add teams to divisions


class Division:
    def __init__(self, name, stage):
        self.name = name
        self.stage = stage

        self.teams = []
        self.url = []

    def scrape_teams_from_division_url(self):
        # TODO: Scrape teams


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


def scrape_tournament_info(tournament_url):
    # Open Tournament-URL and extract website content
    driver.get(tournament_url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    
    tournament_soup = soup.find('div', attrs={'class': 'tournament format-header'})
    tournament_name = tournament_soup.find('div', attrs={'class': 'name'}).text
    platforms = []
    for span in tournament_soup.find('div', attrs={'class': 'platform'}).findAll('span', attrs={'class': 'badge'}):
        platforms.append(span.text)
    game = tournament_soup.find('div', attrs={'class': 'discipline'}).text
    organizer = tournament_soup.find('div', attrs={'class': 'organizer'}).find('span', attrs={'itemprop': 'name'}).text
    location = tournament_soup.find('div', attrs={'class': 'location'}).text
    startdate = tournament_soup.findAll('date-view')[0].text
    enddate = tournament_soup.findAll('date-view')[1].text
    website = tournament_soup.find('div', attrs={'class': 'website'}).text
    perc_played = tournament_soup.find('span', attrs={'class': 'played'}).text
    nteams = tournament_soup.find('div', attrs={'class': 'current'}).text

    tournament = Tournament(name=tournament_name, url=tournament_url, game=game, organizer=organizer,
                            location=location, startdate=startdate, enddate=enddate, website=website,
                            perc_played=perc_played, nteams=nteams)
    return tournament


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


def tear_down_webdriver():
    if driver is not None:
        driver.quit()
