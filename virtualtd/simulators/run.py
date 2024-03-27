import random
from typing import Tuple
from typing import List
from typing import Dict

import pandas as pd

from virtualtd.simulators.predictors import LineUpPredictor
from virtualtd.simulators.predictors import MatchPredictor
from virtualtd.simulators.predictors import ValuePredictor
from virtualtd.simulators.model import CoachInstruction
from virtualtd.generators.model import League
from virtualtd.generators.model import Squad
from virtualtd.generators.model import SquadHierarchy
from virtualtd.generators.model import Position
from virtualtd.generators.model import Player


class MatchSimulator:
    """Simulator to predict the number of expected points for both teams in a match.

    Extra Information:
    -----------------
    The simulator allows the user to simulate the outcome of a match based on n predictions of the line-up and the
    related result. This simulation results in a number of expected points per team in the match.

    Parameters:
    ----------
    home_team_line_up: LineUpPredictor
        Home team squad to get the line-up for.
    away_team_line_up: LineUpPredictor
        Away team squad to get the line-up for.
    n_iterations: int = 10
        Rounds to simulate

    Methods:
    -------
    simulate_line_up() -> Tuple[float, float]
        Simulate the skill level of the line-up n times.
    simulate_match() -> Tuple[float, float]
        Simulate a match n times to get the number of expected points.
    """

    def __init__(self, home_team_line_up: LineUpPredictor, away_team_line_up: LineUpPredictor, n_iterations: int = 10):
        """Simulate a match based on two line-ups and a number of iterations."""
        self._home_team_line_up = home_team_line_up
        self._away_team_line_up = away_team_line_up
        self._n = n_iterations

    def simulate_line_up(self) -> Tuple[float, float]:
        """Simulate the skill level of the line-up n times."""
        home_team_skill = []
        away_team_skill = []
        for i in range(0, self._n, 1):
            home = self._home_team_line_up.get_set_line_up()
            away = self._away_team_line_up.get_set_line_up()
            home_team_skill.append(home.skill_level.mean())
            away_team_skill.append(away.skill_level.mean())

        return sum(home_team_skill) / len(home_team_skill), sum(home_team_skill) / len(home_team_skill)

    def simulate_match(self) -> Tuple[float, float]:
        """Simulate a match n times to get the number of expected points."""
        home_xp = []
        away_xp = []
        outcomes = []
        home_team_skill, away_team_skill = self.simulate_line_up()
        match_predictor = MatchPredictor(home_team_skill, away_team_skill)
        match_predictor.generate_prob_distribution()
        for i in range(0, int(match_predictor.draw_prob), 1):
            outcomes.append(0)
        for i in range(0, int(match_predictor.home_team_win_prob), 1):
            outcomes.append(1)
        for i in range(0, int(match_predictor.away_team_win_prob), 1):
            outcomes.append(-1)

        for i in range(0, self._n, 1):
            match_outcome = random.choice(outcomes)
            if match_outcome == 0:
                home_xp.append(1)
                away_xp.append(1)
            elif match_outcome == 1:
                home_xp.append(3)
                away_xp.append(0)
            else:
                home_xp.append(0)
                away_xp.append(3)

        return sum(home_xp) / self._n, sum(away_xp) / self._n


class SemiSeasonSimulator:
    """Simulator to simulate one half of a season where a team plays every opponent once.

    Extra Information:
    -----------------
    The idea is that this simulator runs until the transfer window, allowing the user to mutate the squad.

    Parameters:
    ----------
    league: League
        The league to draw teams for.
    league_players: pd.DataFrame
        All players in the league.
    virtual_team: str
        Name of the team managed by the virtual td.
    virtual_instruction: CoachInstruction
        The instruction for a coach from the virtual td.
    n_iter: int = 10
        The number of iterations to run in a simulation.

    Methods:
    -------
    simulate_match_calendar(team: Squad, line_up: LineUpPredictor) -> float
        Simulate the matches versus all opponents in the league.
    simulate_season()
        Simulate the full semi-season where all teams play each other once.
    """

    def __init__(
            self,
            league_teams: pd.DataFrame,
            league_players: pd.DataFrame,
            virtual_team: str,
            virtual_instruction: CoachInstruction,
            n_iter: int = 10
    ):
        """Inits SemiSeasonSimulator with a league, a virtual team and instruction, and a number of sims."""
        self._teams = league_teams.copy()
        self._players = league_players.copy()
        self._default_instruction = CoachInstruction()
        self._virtual_team = virtual_team
        self._virtual_instruction = virtual_instruction
        self._n = n_iter
        self._simulation_output = []

    def simulate_match_calendar(self, team: Squad, line_up: LineUpPredictor) -> float:
        """Simulate the matches versus all opponents in the league.

        Returns:
        -------
        Total expected points over all simulated matches.
        """
        team_xp = 0
        for opponent in self._teams['squad_name'].unique():
            if opponent != team:
                opp_team_players = self._players[self._players['team'] == opponent].copy()
                opponent_line_up = LineUpPredictor(self._default_instruction, opp_team_players)
                sim = MatchSimulator(line_up, opponent_line_up, self._n)
                home_xp, away_xp = sim.simulate_match()
                team_xp += home_xp
            else:
                continue

        return team_xp

    def simulate_season(self):
        """Simulate the full semi-season where all teams play each other once."""
        for team in self._teams['squad_name'].unique():
            print(f"starting simulation for {team}")
            team_players = self._players[self._players['team'] == team].copy()
            if team == self._virtual_team:
                team_line_up = LineUpPredictor(self._virtual_instruction, team_players)
            else:
                team_line_up = LineUpPredictor(self._default_instruction, team_players)
            team_xp = self.simulate_match_calendar(team, team_line_up)
            self._teams.loc[self._teams['squad_name'] == team, 'xPoints'] += team_xp
            print(f"{team} achieved {team_xp} points in this iteration")
            print('----------------- \n')

    @property
    def league_teams(self) -> pd.DataFrame:
        """Get the results with xPoints for all teams in the simulation."""
        self._teams.sort_values("xPoints", ascending=False, inplace=True)
        self._teams.reset_index(inplace=True, drop=True)

        return self._teams


class TransferWindowSimulator:
    """Simulate a transfer window by updating player attributes.

    Extra Information:
    -----------------
    This simulator assumes every window is 6 months after the previous, and updates contracts and ages accordingly.
    For other attributes, it uses heuristic models to generate synthetic updates.

    Parameters:
    ----------
    league_players: pd.DataFrame
        Dataframe with all players in the league and their attributes.
    my_team_only: bool = True
        If True, returns updated data only for the team managed as part of virtual td.

    Methods:
    -------
    update_players(step: float = 0.5)
        Update player attributes for the start of the transfer window with a step in years.
    """

    def __init__(self, league_players: pd.DataFrame, my_team_only: bool = True):
        """Inits TransferWindowSimulator with the league players."""
        self._league_players = league_players.copy()
        self._my_team_only = my_team_only

    def _decrease_contract_step(self, step: float = 0.5):
        """Reduce the remaining contract years with half a year."""
        self._league_players["contract_years"] -= step

    @staticmethod
    def _update_skill(row: pd.Series):
        """Update the skill level based on the achieved performance by the team."""
        skill_bonus = (row['xPoints'] / (row['n_matches'] * 3)) * (row['minutes'] / 10)
        row['skill_bonus'] = skill_bonus
        if row['skill_level'] + skill_bonus < row['potential_level']:
            row['skill_level'] += skill_bonus

        return row

    def _update_age(self, step: float = 0.5):
        """Increase the age with half a year."""
        self._league_players.loc[:, "age"] += step

    @staticmethod
    def _update_transfer_value(row: pd.Series):
        """Update the transfer value based on the newest attributes."""
        return ValuePredictor(
            row['age'],
            row['contract_years'],
            row['skill_level'],
            row['potential_level'],
            row['injury_proneness']
        ).predict_player_value()

    def update_players(self, step: float = 0.5):
        """Update player attributes for the start of the transfer window with a step in years."""
        self._decrease_contract_step(step)
        self._update_age(step)
        self._league_players = self._league_players.apply(
            lambda row: self._update_skill(row), axis=1)
        self._league_players.loc[:, 'player_value'] = self._league_players.apply(
            lambda row: self._update_transfer_value(row), axis=1)

    @property
    def updated_players(self) -> pd.DataFrame:
        """Get the updated league players table."""
        if self._my_team_only:
            return self._league_players[self._league_players['my_team']]
        else:
            return self._league_players


class DecisionSimulator:
    """Simulator to virtual td decisions to mutate the squad.

    Extra Information:
    -----------------
    Every transfer window, the squad a virtual td is managing gets mutated:
        - contracts are decreased with 6 months.
        - age is increased with 6 months.
        - players who are too old or ran out of a contract are removed from the squad.
        - academy players who are too old are removed from the squad.
        - players can sold or contracts can be extended.
        - players can be promoted to a new hierarchy role.
        - new players can be bought.

    Players can only be bought with money first generated through selling players, and players can only
    be bought for open slots.

    Parameters:
    ----------
    squad_players: pd.DataFrame
        Overview with all players in the squad.

    Methods:
    -------
    sell_players(player_list: List[str])
        Sell a set of players and add money to your available spending money.
    extend_contracts(extensions: Dict[str, int])
        Extend a predetermined number of contracts.
    promote_players(promotions: Dict[str, SquadHierarchy])
        Promote a predetermined number of contracts.
    assess_team_state()
        Check wat position slots need to be filled and print an overview to the console.
    buy_players(buy_list: List[dict])
        Buy a list of players while checking if their transfers are valid.
    """

    def __init__(self, squad_players: pd.DataFrame, team_name: str):
        """Inits DecisionSimulator with a squad of players to simulate decisions for."""
        self._players = squad_players
        self._auto_termination()
        self.money_to_spend = 0
        self._team_name = team_name

    def _auto_termination(self):
        """Automatically terminates players who don't have a contract or who passed the age threshold."""
        gross_value = self._players['player_value'].sum()
        squad_size = len(self._players)
        print(self._players[self._players['contract_years'] == 0.0])
        self._players = self._players[
            (self._players['contract_years'] > 0) &
            (self._players['age'] < 35)
            ].copy()
        print(f"{squad_size - len(self._players)} out of {squad_size} players were auto-terminated because of age or contract.")
        print(f"You lost {gross_value - self._players['player_value'].sum()} Euro because of auto-termination.")
        self._auto_terminate_academy_players()

    def _auto_terminate_academy_players(self):
        """Automatically terminates academy players who passed the age threshold."""
        gross_value = self._players['player_value'].sum()
        squad_size = len(self._players)
        self._players = self._players[
            (self._players['squad_hierarchy'].isin([
                SquadHierarchy.SUB,
                SquadHierarchy.STARTER
            ])) |
            (self._players['age'] < 21)
            ]
        print(f"{squad_size - len(self._players)} out of {squad_size} players were auto-terminated because of age.")
        print(f"You lost {gross_value - self._players['player_value'].sum()} Euro because of auto-termination.")

    def sell_players(self, player_list: List[str]):
        """Sell a set of players and add money to your available spending money."""
        to_sell = self._players[self._players['player_name'].isin(player_list)].copy()
        self._players = self._players[~self._players['player_name'].isin(player_list)]
        self.money_to_spend += to_sell['player_value'].sum()

    def extend_contracts(self, extensions: Dict[str, int]):
        """Extend a predetermined number of contracts."""
        for player in extensions.keys():
            self._players.loc[self._players['player_name'] == player, 'contract_years'] = extensions[player]

    def promote_players(self, promotions: Dict[str, SquadHierarchy]):
        """Promote a predetermined number of contracts."""
        for player in promotions.keys():
            self._players.loc[self._players['player_name'] == player, 'squad_hierarchy'] = promotions[player]

    def assess_team_state(self):
        """Check wat position slots need to be filled and print an overview to the console."""
        for position in Position:
            position_players = self._players[self._players['position'] == position].copy()
            if len(position_players) == 3:
                print(f"for the {position.name} all slots are filled")
            else:
                if SquadHierarchy.STARTER not in position_players['squad_hierarchy'].values:
                    print(f"for the {position.name} position you need a {SquadHierarchy.STARTER.name}")
                if SquadHierarchy.SUB not in position_players['squad_hierarchy'].values:
                    print(f"for the {position.name} position you need a {SquadHierarchy.SUB.name}")
                if SquadHierarchy.ACADEMY not in position_players['squad_hierarchy'].values:
                    print(f"for the {position.name} position you need a {SquadHierarchy.ACADEMY.name}")

    def _validate_transfer(self, player: Player) -> bool:
        """Check if a proposed transfer is valid."""
        return (
                (player.player_value < self.money_to_spend) &
                (self._players[
                     (self._players['position'] == player.position) &
                     (self._players['squad_hierarchy'] == player.squad_hierarchy)
                     ].empty())
        )

    def _add_player_to_squad(self, transfer: dict):
        """Add a player to the squad."""
        self._players = self._players.append({
            'player_name': transfer.get('player').player_name,
            'contract_years': transfer.get('contract'),
            'age': transfer.get('player').age,
            'position': transfer.get('player').position,
            'skill_level': transfer.get('player').skill_level,
            'potential_level': transfer.get('player').potential_level,
            'player_value': transfer.get('player').player_value,
            'squad_hierarchy': transfer.get('squad_hierarchy'),
            'injury_proneness': transfer.get('player').injury_proneness,
            'team': self._team_name,
            'n_matches': 0,
            'my_team': True,
            'minutes': 0,
            'xPoints': 0,
        }, ignore_index=True)

    def buy_players(self, buy_list: List[dict]):
        """Buy a list of players while checking if their transfers are valid.

        Parameters:
        ----------
        buy_list: List[Dict]
            The buy list should contain dicts with player attributes looking as follows:
                {
                    player: Player,
                    squad_hierarchy: SquadHierarchy,
                    contract: int (range 1-5)
                }
        """
        for transfer in buy_list:
            if self._validate_transfer(transfer.get("player")):
                print(
                    f"Transfer of {transfer.get('player').player_name} as {transfer.get('player').squad_hierarchy.name} for the {transfer.get('player').position.name}")
                print(f"is valid, progressing to spend €{transfer.get('player').player_value}")
                self.money_to_spend -= transfer.get('player').player_value
                self._add_player_to_squad(transfer)
            else:
                print("transfer is invalid, skipping to next transfer.")

    @property
    def updated_squad(self) -> pd.DataFrame:
        """Get the latest version of the squad after mutations."""
        return self._players


class LeagueSimulator:
    """Simulator to simulate being a virtual TD and managing a club for a full league iteration.

    Extra Information:
    -----------------
    One can simulate a league as long as you like, using the following flow:
        - Initialize the league;
        - Simulate first half of the season;
        - Simulate transfer window;
        - Simulate second half of the season;
        - Simulate transfer window;
        - Start new season.

    Parameters:
    ----------
    league: League
        The league to draw teams for.
    my_team: str
        Name of the team managed by the virtual td.

    Methods:
    -------
    run_season_half(virtual_instruction: CoachInstruction)
        Run one half of a season on a given instruction.
    run_transfer_window(self)
        Update the player overview by simulating a transfer window.
    """

    def __init__(self, league: League, my_team: str):
        """Inits LeagueSimulator with a league and a virtual team."""
        self.league = league
        self._league_teams = pd.DataFrame(league.league_squads)
        self.my_team = my_team
        self._league_teams.loc[:, "xPoints"] = 0.0
        self._league_players = self._set_league_players()
        self._set_my_virtual_team()

    def _set_league_players(self) -> pd.DataFrame:
        """Create a dataframe with all players in the league."""
        players = []
        for squad in self.league.league_squads:
            df_players = pd.DataFrame(squad.squad_players)
            df_players.loc[:, "team"] = squad.squad_name
            players.append(df_players)

        return pd.concat(players)

    def _set_my_virtual_team(self):
        """Set the team you are managing based on the team name."""
        self._league_teams["my_team"] = self._league_teams['squad_name'] == self.my_team
        self._league_players["my_team"] = self._league_players['team'] == self.my_team

    def run_season_half(self, virtual_instruction: CoachInstruction):
        """Run one half of a season on a given instruction."""
        self._league_players.loc[:, 'n_matches'] = 0
        sim = SemiSeasonSimulator(self._league_teams, self._league_players, self.my_team, virtual_instruction)
        sim.simulate_season()
        self._league_teams = sim.league_teams.copy()
        self._update_players_in_season_half(virtual_instruction)

    def _update_players_in_season_half(self, virtual_instruction: CoachInstruction):
        """Update players with the team attributes from the simulated season half."""
        self._league_players.loc[:, 'n_matches'] += len(self.league.league_squads) - 1
        self._league_players.loc[
            (self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.STARTER), 'minutes'
        ] = virtual_instruction.starter_match_share
        self._league_players.loc[
            (self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.SUB), 'minutes'
        ] = virtual_instruction.sub_match_share
        self._league_players.loc[
            (self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.ACADEMY), 'minutes'
        ] = virtual_instruction.academy_match_share
        self._league_players.loc[
            (~self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.STARTER), 'minutes'
        ] = CoachInstruction().starter_match_share
        self._league_players.loc[
            (~self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.SUB), 'minutes'
        ] = CoachInstruction().sub_match_share
        self._league_players.loc[
            (~self._league_players['my_team']) &
            (self._league_players['squad_hierarchy'] == SquadHierarchy.ACADEMY), 'minutes'
        ] = CoachInstruction().academy_match_share
        for row in self._league_teams.to_dict('records'):
            self._league_players.loc[self._league_players['team'] == row['squad_name'], 'xPoints'] = row['xPoints']

    def run_transfer_window(self) -> pd.DataFrame:
        """Update the player overview by simulating a transfer window."""
        TM = TransferWindowSimulator(self._league_players)
        TM.update_players(0.5)

        return TM.updated_players

    def update_end_of_transfer_window(self, df_players):
        """After simulating the transfer window, update the team with the latest squad version."""
        self._league_players = self._league_players[self._league_players['team'] != self.my_team].copy()
        self._league_players = pd.concat([
            self._league_players,
            df_players
        ])

    def start_new_season(self):
        """At start of a new season, reset the points count & minutes."""
        self._league_players.loc[:, 'xPoints'] = 0.0
        self._league_players.loc[:, 'minutes'] = 0.0
        self._league_teams.loc[:, "xPoints"] = 0.0
