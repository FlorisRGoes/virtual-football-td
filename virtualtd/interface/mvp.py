from virtualtd.generators.creator import LeagueGenerator
from virtualtd.simulators.model import CoachInstruction
from virtualtd.simulators.run import LeagueSimulator
from virtualtd.simulators.run import DecisionSimulator
from virtualtd.generators.creator import TransferMarktGenerator

LEAGUE_STRENGTH = 55
STRENGTH_SD = 25

PLAYER_NAMES = []
VIRTUAL_LEAGUE = LeagueGenerator(LEAGUE_STRENGTH, STRENGTH_SD).create_league()
for squad in VIRTUAL_LEAGUE.league_squads:
    for plr in squad.squad_players:
        PLAYER_NAMES.append(plr.player_name)

TRANSFERMARKT = TransferMarktGenerator(PLAYER_NAMES)
VIRTUAL_INSTRUCTION = CoachInstruction(75, 5, 20)

MY_TEAM = VIRTUAL_LEAGUE.league_squads[5].squad_name
SIM = LeagueSimulator(VIRTUAL_LEAGUE, MY_TEAM)

SIM.run_season_half(VIRTUAL_INSTRUCTION)
updated_squad = SIM.run_transfer_window()
BREAK_SIM = DecisionSimulator(updated_squad, MY_TEAM)
SIM.update_end_of_transfer_window(BREAK_SIM.updated_squad)

SIM.run_season_half(VIRTUAL_INSTRUCTION)
updated_squad = SIM.run_transfer_window()
BREAK_SIM = DecisionSimulator(updated_squad, MY_TEAM)
SIM.update_end_of_transfer_window(BREAK_SIM.updated_squad)

SIM.start_new_season()
