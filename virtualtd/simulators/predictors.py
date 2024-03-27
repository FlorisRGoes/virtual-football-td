import random
from typing import List

import pandas as pd

from virtualtd.simulators.model import CoachInstruction
from virtualtd.generators.model import Position
from virtualtd.generators.model import SquadHierarchy


class ValuePredictor:
    """Predictor class for modelling player values based on age, skill, contract years, and potential.

    Extra Information:
    -----------------
    The predictor works based on a couple of assumptions:
        - players > 27 will decrease in value;
        - longer contracts mean higher values;
        - potential skill only holds 50% of the value of real skill, given the uncertainty.

    Parameters:
    ----------
    player_age: float
        Age of the player in years
    contract_years: float
        Years remaining on a players contract.
    skill_level: float
        Skill level of a player in range (0-100).
    potential: float
        Potential level of a player in range (0-100).
    base_value: int = 1000
        Base value for all predictions to start at.

    Methods:
    -------
    get_league_name() -> str
        Get a randomly generated league name.
    get_skill() -> float
        Get a randomly generated skill level using the provided league level benchmarks.
    create_league() -> League
        Create a synthetic league using the provided settings.
    """

    def __init__(
            self,
            player_age: float,
            contract_years: float,
            skill_level: float,
            potential: float,
            injury: float,
            base_value: int = 1000
    ):
        """Inits ValuePredictor with an age, contract, skill level, potential and a base value."""
        self._age = player_age
        self._contract = contract_years
        self._skill = skill_level
        self._potential = potential
        self._injury = injury
        self._base_value = base_value

    def _get_contract_multiplier(self) -> float:
        """Get the contract multiplier based on the assumption that a longer contract adds value."""
        self._contract = int(self._contract * 12)
        if self._contract > 0:
            return 1 + 36 / self._contract
        else:
            return 0.0

    def _get_age_multiplier(self) -> float:
        """Get the age multiplier based on the assumption that the prima age is 27."""
        return 27 / self._age

    def _get_skill_value(self) -> float:
        """Get the value based on current skill."""
        return self._skill ** 2 * self._base_value

    def _get_potential_value(self):
        """Get the value based on estimated potential."""
        val = self._potential ** 2 * self._base_value
        return 0.5 * (val - self._get_skill_value())

    def _get_injury_multiplier(self):
        """Get the injury proneness multiplier."""
        return 1 - self._injury

    def predict_player_value(self) -> float:
        """Predict the resulting player value."""
        value = self._get_skill_value() + self._get_potential_value()
        return value * self._get_age_multiplier() * self._get_contract_multiplier() * self._get_injury_multiplier()


class LineUpPredictor:
    """Predictor class to get the line-up for a team.

    Extra Information:
    -----------------
    Takes the coach instruction coming from the virtual TD as input and generates a line-up of eleven players based
    on the probability that the starter, sub or academy player will play.

    Parameters:
    ----------
    config: CoachInstruction
        Instruction for the coach with parameters that influence the option distribution.
    df_squad_players: pd.DataFrame
        All players in a squad that can be in the line-up.

    Methods:
    -------
    get_set_line_up() -> pd.DataFrame
        Get the line-up for a team based on the option distribution.
    """
    def __init__(self, config: CoachInstruction, df_squad_players: pd.DataFrame):
        """Inits LineUpPredictor with a coach instruction and squad to get the line-up from."""
        self._params = config
        self._squad_players = df_squad_players.copy()
        self._option_distribution = self._generate_option_distribution()

    def _generate_option_distribution(self) -> List[SquadHierarchy]:
        """Generate a distribution with 100 choices based on the provided coach instruction."""
        option_distribution = []
        for i in range(0, self._params.starter_match_share, 1):
            option_distribution.append(SquadHierarchy.STARTER)
        for i in range(0, self._params.sub_match_share, 1):
            option_distribution.append(SquadHierarchy.SUB)
        for i in range(0, self._params.academy_match_share, 1):
            option_distribution.append(SquadHierarchy.ACADEMY)

        return option_distribution

    def _set_line_up_player(self, position: Position):
        """Draw a player from the squad for a given position based on the hierarchy option distribution."""
        hierarchy = random.choice(self._option_distribution)
        self._squad_players.loc[
            (self._squad_players['position'] == position) &
            (self._squad_players['squad_hierarchy'] == hierarchy), 'line_up_player'
        ] = True

    def get_set_line_up(self) -> pd.DataFrame:
        """Get the line-up for a team based on the option distribution."""
        self._squad_players.loc[:, 'line_up_player'] = False
        for position in Position:
            self._set_line_up_player(position)

        return self._squad_players[self._squad_players['line_up_player']]


class MatchPredictor:
    """Predictor class for predicting the probabilities of a match result in terms on win, draw, loose.

    Extra Information:
    -----------------
    When the skill level of both teams is equal, both teams have 1 in 3 win probability, and there is a 1 in 3 draw
    probability. The distribution of probabilities chances once the skill differential between both teams chances:
        - The draw probability is changed based on the skill differential between both teams:
            draw (%) = abs(skill_a/100 - skill_b/100) * _draw_prob
        - The win probability of both teams is generated from the remaining 100 - draw point
            if draw (%) = 30, the combined win probability of either team A or B winning is 70%.
        - The win probability is distributed over both teams based on the skill differential.
            if a team of skill 70 plays a team of skill 60, the team of skill 70 is 50 + (70-60) % likely to win.
        - The win probability is then distributed based on the generated ratios (in this case 60-40).

    Parameters:
    ----------
    skill_team_a: float
        Skill level of team A in range (0-100).
    skill_team_b: float
        Skill level of team B in range (0-100).

    Methods:
    -------
    generate_prob_distribution()
        Predict the probability of every result class.

    Example:
    -------
    If for example team A with skill 80 plays team B with skill 40:
        - The draw probability is abs(80/100 - 40/100) * (100/3) = 13.33%
        - The combined win probability over both teams equals 100 - 13.3 or 86.66%
        - Team A has 50 + (80-40) = 90% chance of winning over team B (which has a 10% chance).
        - The resulting win probability of Team A equals 90% of 86.66% or 78%, and that of Team B 8.66.

    """

    def __init__(self, skill_team_a: float, skill_team_b: float):
        """Inits MatchPredictor with the skill level of both competing line-ups."""
        self._skill_a = skill_team_a
        self._skill_b = skill_team_b
        self._win_prob_a = 100 / 3
        self._draw_prob = 100 / 3
        self._win_prob_b = 100 / 3

    def _set_draw_probability(self):
        """Set the draw probability."""
        draw = abs(self._skill_a / 100 - self._skill_b / 100)
        self._draw_prob *= draw

    def _set_win_probability(self):
        """Set the win probabilities for both teams."""
        combined_win_prob = 100 - self._draw_prob
        team_a_win_share = 50 + (self._skill_a - self._skill_b)
        team_b_win_share = 50 + (self._skill_b - self._skill_a)

        self._win_prob_a = team_a_win_share / 100 * combined_win_prob
        self._win_prob_b = team_b_win_share / 100 * combined_win_prob

    @property
    def home_team_win_prob(self) -> float:
        """Probability that the home team wins the match."""
        return self._win_prob_a

    @property
    def away_team_win_prob(self) -> float:
        """Probability that the away team wins the match."""
        return self._win_prob_b

    @property
    def draw_prob(self) -> float:
        """Probability that match returns in a draw."""
        return self._draw_prob

    def generate_prob_distribution(self):
        """Predict the probability of every result class."""
        self._set_draw_probability()
        self._set_win_probability()
