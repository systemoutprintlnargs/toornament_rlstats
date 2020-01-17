from scrapetoor import *

test_scrape_teams = False
test_scrape_stats = False
test_csv_export = True
test_scrape_teams_stats = False
test_full = False

# Create 2 test teams with players
testTeams = []

testTeams.append(Team("Test Team", "www.testteam_notreal.de"))
testTeams[0].players.append(Player("Scrub Killa", testTeams[0], "76561198089298636", "-", "-", "-"))  # Steam player
testTeams[0].players.append(Player("MADMASSACRE510", testTeams[0], "-", "Madmassacre510", "-", "-"))  # Xbox player
testTeams[0].players.append(Player("Harmen501", testTeams[0], "-", "-", "harmen501", "-"))  # PS player

testTeams.append(Team("UED Wolverines", "www.testteam2_notreal.de"))
testTeams[1].players.append(Player("BonsaiBrudi", testTeams[0], "76561197970707838", "-", "-", "-"))
testTeams[1].players.append(Player("Gingerbread :)", testTeams[0], "76561198202712753", "-", "-", "-"))
testTeams[1].players.append(Player("Salzberg", testTeams[0], "76561198097929350", "-", "-", "-"))


if test_scrape_teams or test_scrape_teams_stats or test_full:
    # Test scrape_teams()
    teams_toor = scrape_teams("https://www.toornament.com/en_US/tournaments/2859636902129573888")

    print("scrape_teams() successful. Check output:\n")

    for theTeam in teams_toor:
        print("Team-Name = " + theTeam.name)
        for thePlayer in theTeam.players:
            print(" Player-Name = " + thePlayer.name)
            print(" Player-SteamID = " + thePlayer.steam_id)
            print(" Player-xboxID = " + thePlayer.xbox_id)
            print(" Player-psnID = " + thePlayer.psn_id)
            print(" Player-NintendoID = " + thePlayer.nintendo_id)
        print()
else:
    print("Skipping test of scrape_teams()...")


if test_scrape_stats or test_scrape_teams_stats or test_full:
    # Test scrape_stats
    try:
        if test_scrape_teams_stats:
            teams_tnr = teams_toor
        else:
            teams_tnr = testTeams
        teams_tnr = scrape_stats(teams_tnr)
    except:
        print("Error in scrape_stats")
    else:
        print("scrape_stats() successfull. Check output:\n")
        for theTeam in teams_tnr:
            print("Team-Name = " + theTeam.name)
            for thePlayer in theTeam.players:
                print("   Player-Name = " + thePlayer.name)
                print("      MMR_1v1 = " + thePlayer.mmr_1v1)
                print("      MMR_2v2 = " + thePlayer.mmr_2v2)
                print("      MMR_3v3s = " + thePlayer.mmr_3v3s)
                print("      MMR_3v3 = " + thePlayer.mmr_3v3)
            print()
else:
    print("Skipping test of scrape_stats()...")


# Add test-MMR values to players
t = 0
while t < 2:
    p = 0
    while p < 3:
        print("t=" + str(t) + ", p=" + str(p))
        testTeams[t].players[p].mmr_1v1 = str((t+1)*100 + p + 1)
        testTeams[t].players[p].mmr_2v2 = str((t+1)*100 + p + 2)
        testTeams[t].players[p].mmr_3v3s = str((t+1)*100 + p + 3)
        testTeams[t].players[p].mmr_3v3 = str((t+1)*100 + p + 4)
        p = p + 1
    t = t + 1

if test_csv_export or test_full:
    if test_full:
        save_teams = teams_tnr
    else:
        save_teams = testTeams

    save_directory = "C:/Users/Oliver/Documents/Projects/toornament_rlstats/CSV_Output/"
    csv_file_name = "test_output.csv"

    save_success = export_teams_to_csv(save_teams, csv_file_name, save_directory)
    print("Save successful?: " + str(save_success))
else:
    print("Skipping test of export_csv()...")
