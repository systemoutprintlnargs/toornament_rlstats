from scrapetoor import *

# Input data
toornament_url = "https://www.toornament.com/en_US/tournaments/2859636902129573888/"
dir_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
save_directory = dir_parent_path.replace('\\', '/') + '/CSV_Output/'
csv_file_name = "main_output.csv"

# Scrape teams from toornament.com
teams_toor = scrape_teams(toornament_url)

# Scrape MMR from TRN
teams_final = scrape_stats(teams_toor)

# Export data to csv
save_success = export_teams_to_csv(teams_final, csv_file_name, save_directory)
