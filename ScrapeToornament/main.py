from scrapetoor import *

# Input data
# tournament_url = "https://www.toornament.com/en_US/tournaments/2859636902129573888/"  # Uniliga 2019-2

# tournament_url = "https://www.toornament.com/en_GB/tournaments/3356365864224243712/"  # HHaie Tournament 2020

tournament_url = "https://www.toornament.com/en_GB/tournaments/3356365864224243712/"  # Uniliga 2020-1

dir_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
save_directory = dir_parent_path.replace('\\', '/') + '/CSV_Output/'
csv_file_name = "20200123_main_output.csv"

# Scrape teams from toornament.com
teams_toor = scrape_teams_from_participants_website(tournament_url + "participants/")

# Scrape MMR from TRN
for the_team in teams_toor:
    the_team.scrape_players()

    for the_player in the_team.players:
        the_player.scrape_stats()

# Export data to csv
save_success = export_teams_to_csv(teams_toor, csv_file_name, save_directory)
