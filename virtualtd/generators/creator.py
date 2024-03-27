import random
from typing import List
from typing import Tuple

import randomname
import names

from virtualtd.generators.model import League
from virtualtd.generators.model import Squad
from virtualtd.generators.model import Player
from virtualtd.generators.model import Position
from virtualtd.generators.model import SquadHierarchy
from virtualtd.generators.constraints import AgeConstraint
from virtualtd.generators.constraints import ContractConstraint
from virtualtd.generators.constraints import SkillConstraint
from virtualtd.generators.constraints import PotentialConstraint
from virtualtd.simulators.predictors import ValuePredictor


class LeagueGenerator:
    """Generator class for creating a league with virtual teams and players.

    Extra Information:
    -----------------
    The league generator creates a league of teams and players that can be used for simulation.

    Parameters:
    ----------
    league_strength: float = 50.0
        Average skill level of teams in the league on a range of 0-100.
    competitiveness_sd: float = 10.0
        Determines the distribution of skill level across the league. The lower this number is, the higher the
        competitiveness given the skill level of teams is closer. The user is advised to only chose values where
        league_strength - 2 * competitiveness_sd > 0 and league_strength + 2 * competitiveness_sd < 100, as otherwise
        many teams will gravitate towards the min or max strength values.
    n_teams: int = 18
        Number of teams in the league. This can be any positive number > 2, but the user is advised to work with a
        range of 12-24 teams for representative simulations.

    Methods:
    -------
    get_league_name() -> str
        Get a randomly generated league name.
    get_skill() -> float
        Get a randomly generated skill level using the provided league level benchmarks.
    create_league() -> League
        Create a synthetic league using the provided settings.
    """
    def __init__(self, league_strength: float = 50.0, competitiveness_sd: float = 10.0, n_teams: int = 18):
        """Inits LeagueGenerator with a league strength, competitiveness level and number of teams."""
        self._league_strength = league_strength
        self._competitiveness = competitiveness_sd
        self._n_teams = n_teams
        self._player_names = []
        self._team_names = []

    @staticmethod
    def get_league_name() -> str:
        """Get a randomly generated league name."""
        return f"{randomname.generate(('adj/weather', 'adj/size', 'adj/sound'), 'v/sports')} League"

    def get_skill(self) -> float:
        """Get a randomly generated skill level using the provided league level benchmarks.

        Extra Information:
        -----------------
        Generates the skill level from a normal distribution with mean league_strength and SD competitiveness.
        Note that the range is fixed (0-100), and numbers generated outside of this range are dropped and regenerated.
        """
        value = random.normalvariate(self._league_strength, self._competitiveness)
        while value < 0 or value > 100:
            value = random.normalvariate(self._league_strength, self._competitiveness)

        return value

    def _set_teams(self) -> List[Squad]:
        """Create a collection of teams using the provided league settings."""
        created_teams = []
        for i in range(0, self._n_teams, 1):
            squad = TeamGenerator(
                self.get_skill(),
                self._competitiveness,
                self._team_names,
                self._player_names,
            ).create_team()
            created_teams.append(squad)
            self._team_names.append(squad.squad_name)
            self._player_names.extend([plr.player_name for plr in squad.squad_players])

        return created_teams

    def create_league(self) -> League:
        """Create a synthetic league using the provided settings."""
        return League(
            league_name=self.get_league_name(),
            league_squads=self._set_teams()
        )

    def save_league_state(self):
        ...


class TeamGenerator:
    """Generator class for creating a league with virtual teams and players.

    Parameters:
    ----------
    team_strength: float
        Mean skill level of the starting 11.
    strength_sd: float
        Deviation of the skill level across the team.
    occupied_team_names: List[str]
        List of team names already taken to prevent duplicate team names in a single competition.
    occupied_player_names: List[str]
        List of player names already taken to prevent duplicate player names in a single dataset.

    Methods:
    -------
    get_team_name() -> str
        Get a randomly generated team name.
    create_team(self) -> Squad
        Create a synthetic team using the provided settings.
    """
    def __init__(
            self,
            team_strength: float,
            strength_sd: float,
            occupied_team_names: List[str],
            occupied_player_names: List[str]
    ):
        self._team_names = occupied_team_names
        self._player_names = occupied_player_names
        self._team_strength = team_strength
        self._strength_sd = strength_sd

    def get_team_name(self) -> str:
        """Get a randomly generated team name."""
        adjectives = ("adj/speed", "adj/sound", "adj/shape", "adj/size", "adj/appearance", "adj/character")
        verbs = ("v/sports", "v/movement", "v/fire")
        nouns = ("n/cats", "n/birds", "n/dogs", "n/sports", "n/apex_predators", "n/fish")

        team_name = f"{randomname.generate(adjectives, verbs, nouns)} FC"
        while team_name in self._team_names:
            team_name = f"{randomname.generate(adjectives, verbs, nouns)} FC"

        return team_name

    @staticmethod
    def _get_squad_composition() -> List[Tuple[Position, SquadHierarchy]]:
        """Get the composition of the squad to know what players to generate."""
        return [
            (Position.GOALKEEPER, SquadHierarchy.STARTER),
            (Position.GOALKEEPER, SquadHierarchy.SUB),
            (Position.GOALKEEPER, SquadHierarchy.ACADEMY),
            (Position.LEFT_BACK, SquadHierarchy.STARTER),
            (Position.LEFT_BACK, SquadHierarchy.SUB),
            (Position.LEFT_BACK, SquadHierarchy.ACADEMY),
            (Position.RIGHT_BACK, SquadHierarchy.STARTER),
            (Position.RIGHT_BACK, SquadHierarchy.SUB),
            (Position.RIGHT_BACK, SquadHierarchy.ACADEMY),
            (Position.LEFT_CENTRE_BACK, SquadHierarchy.STARTER),
            (Position.LEFT_CENTRE_BACK, SquadHierarchy.SUB),
            (Position.LEFT_CENTRE_BACK, SquadHierarchy.ACADEMY),
            (Position.RIGHT_CENTRE_BACK, SquadHierarchy.STARTER),
            (Position.RIGHT_CENTRE_BACK, SquadHierarchy.SUB),
            (Position.RIGHT_CENTRE_BACK, SquadHierarchy.ACADEMY),
            (Position.LEFT_MID, SquadHierarchy.STARTER),
            (Position.LEFT_MID, SquadHierarchy.SUB),
            (Position.LEFT_MID, SquadHierarchy.ACADEMY),
            (Position.RIGHT_MID, SquadHierarchy.STARTER),
            (Position.RIGHT_MID, SquadHierarchy.SUB),
            (Position.RIGHT_MID, SquadHierarchy.ACADEMY),
            (Position.CENTRE_MID, SquadHierarchy.STARTER),
            (Position.CENTRE_MID, SquadHierarchy.SUB),
            (Position.CENTRE_MID, SquadHierarchy.ACADEMY),
            (Position.RIGHT_WING, SquadHierarchy.STARTER),
            (Position.RIGHT_WING, SquadHierarchy.SUB),
            (Position.RIGHT_WING, SquadHierarchy.ACADEMY),
            (Position.LEFT_WING, SquadHierarchy.STARTER),
            (Position.LEFT_WING, SquadHierarchy.SUB),
            (Position.LEFT_WING, SquadHierarchy.ACADEMY),
            (Position.STRIKER, SquadHierarchy.STARTER),
            (Position.STRIKER, SquadHierarchy.SUB),
            (Position.STRIKER, SquadHierarchy.ACADEMY),
        ]

    def _set_players(self) -> List[Player]:
        """Create a collection of players using the provided team settings."""
        squad_composition = self._get_squad_composition()
        created_players = []
        for profile in squad_composition:
            player = PlayerGenerator(
                profile,
                self._player_names,
                self._team_strength,
                self._strength_sd
            ).create_player()
            created_players.append(player)
            self._player_names.append(player.player_name)
        return created_players

    def create_team(self) -> Squad:
        """Create a synthetic team using the provided settings."""
        return Squad(
            squad_name=self.get_team_name(),
            squad_players=self._set_players()
        )


class PlayerGenerator:
    """Generator class for creating a league with virtual teams and players.

    Parameters:
    ----------
    profile: Tuple[Position, SquadHierarchy]
        Specification of the type of player to create.
    occupied_names: List[str]
        List of player names already taken to prevent duplicate player names in a single competition.
    team_strength: float
        Mean skill level of the starting 11.
    strength_sd: float
        Deviation of the skill level across the team.

    Methods:
    -------
    get_player_name(gender: str = 'male') -> str
        Get a randomly generated player name.
    create_player(self) -> Player
        Create a synthetic player using the provided settings.
    """
    def __init__(
            self,
            profile: Tuple[Position, SquadHierarchy],
            occupied_names: List[str],
            team_strength: float,
            strength_sd: float
    ):
        """Inits PlayerGenerator with a player profile, a list of taken names, the average team strength and SD."""
        self._profile = profile
        self._player_names = occupied_names
        self._team_strength = team_strength
        self._strength_sd = strength_sd

    def get_player_name(self, gender: str = 'male') -> str:
        """Get a randomly generated player name."""
        player_name = names.get_full_name(gender=gender)
        while player_name in self._player_names:
            player_name = names.get_full_name(gender=gender)

        return player_name

    def _set_contract_years(self) -> int:
        """Set the number of contract years for a player."""
        if self._profile[1] in [SquadHierarchy.STARTER, SquadHierarchy.SUB]:
            return ContractConstraint().get_regular_contract()
        else:
            return ContractConstraint().get_academy_contract()

    def _set_age(self) -> float:
        """Randomly generates the age of a player based on the provided squad hierarchy."""
        if self._profile[1] in [SquadHierarchy.STARTER, SquadHierarchy.SUB]:
            return AgeConstraint().get_regular_age()
        else:
            return AgeConstraint().get_academy_age()

    def _set_skill_level(self) -> float:
        """Randomly assign a skill level to a player based on its profile and team specifics."""
        if self._profile[1] == SquadHierarchy.STARTER:
            return SkillConstraint(self._team_strength, self._strength_sd).get_starter_skill()
        elif self._profile[1] == SquadHierarchy.SUB:
            return SkillConstraint(self._team_strength, self._strength_sd).get_sub_skill()
        else:
            return SkillConstraint(self._team_strength, self._strength_sd).get_academy_skill()

    def _set_potential_level(self, age: float, skill_level: float) -> float:
        """Set the potential level for a player."""
        return PotentialConstraint(age, skill_level, self._strength_sd).get_potential()

    @staticmethod
    def _set_player_value(contract_years: float, age: float, skill: float, potential: float, injury: float) -> float:
        """Set the player estimated transfer value."""
        return ValuePredictor(age, contract_years, skill, potential, injury).predict_player_value()

    @staticmethod
    def _get_injury_proneness() -> float:
        """Randomly generate a player's proneness to injury."""
        risk = random.normalvariate(0.05, 0.02)
        if risk < 0:
            risk = 0.01

        return risk

    def create_player(self) -> Player:
        """Create a synthetic player using the provided settings."""
        contract_years = self._set_contract_years()
        age = self._set_age()
        skill_level = self._set_skill_level()
        potential_level = self._set_potential_level(age, skill_level)
        injury = self._get_injury_proneness()

        return Player(
            player_name=self.get_player_name(),
            contract_years=contract_years,
            age=age,
            position=self._profile[0],
            skill_level=skill_level,
            potential_level=potential_level,
            player_value=self._set_player_value(contract_years, age, skill_level, potential_level, injury),
            squad_hierarchy=self._profile[1],
            injury_proneness=injury
        )


class TransferMarktGenerator:
    """Generator class for creating a transfer mark with random players that can be bought.

    Parameters:
    ----------
    occupied_names: List[str]
        List of player names already taken to prevent duplicate player names in a single competition.

    Methods:
    -------
    generate_transfermarkt(self, n_players: int = 10000) -> List[Player].
        Generate a transfermarkt of n players.
    """
    def __init__(self, occupied_names: List[str]):
        """Inits TransferMarktGenerator with a list of occupied names."""
        self._player_names = occupied_names

    @staticmethod
    def _get_player_position() -> Position:
        """Randomly generate a position"""
        choices = [position for position in Position]
        return random.choice(choices)

    @staticmethod
    def _get_player_hierarchy():
        """Randomly generate a hierarchy"""
        choices = [role for role in SquadHierarchy]
        return random.choice(choices)

    def get_player_name(self, gender: str = 'male') -> str:
        """Get a randomly generated player name."""
        player_name = names.get_full_name(gender=gender)
        while player_name in self._player_names:
            player_name = names.get_full_name(gender=gender)

        return player_name

    @staticmethod
    def _set_contract_years(hierarchy: SquadHierarchy) -> int:
        """Set the number of contract years for a player."""
        if hierarchy in [SquadHierarchy.STARTER, SquadHierarchy.SUB]:
            return ContractConstraint().get_regular_contract()
        else:
            return ContractConstraint().get_academy_contract()

    @staticmethod
    def _set_age(hierarchy: SquadHierarchy) -> float:
        """Randomly generates the age of a player based on the provided squad hierarchy."""
        if hierarchy in [SquadHierarchy.STARTER, SquadHierarchy.SUB]:
            return AgeConstraint().get_regular_age()
        else:
            return AgeConstraint().get_academy_age()

    @staticmethod
    def _set_skill_level() -> float:
        """Randomly assign a skill level to a player based on its profile and team specifics."""
        return SkillConstraint(50, 25).get_academy_skill()

    @staticmethod
    def _set_potential_level(age: float, skill_level: float) -> float:
        """Set the potential level for a player."""
        return PotentialConstraint(age, skill_level, 25).get_potential()

    @staticmethod
    def _set_player_value(contract_years: float, age: float, skill: float, potential: float, injury: float) -> float:
        """Set the player estimated transfer value."""
        return ValuePredictor(age, contract_years, skill, potential, injury).predict_player_value()

    @staticmethod
    def _get_injury_proneness() -> float:
        """Randomly generate a player's proneness to injury."""
        risk = random.normalvariate(0.05, 0.02)
        if risk < 0:
            risk = 0.01

        return risk

    def _create_player(self):
        """Create a random player for the transfermarkt."""
        position = self._get_player_position()
        role = self._get_player_hierarchy()
        contract_years = self._set_contract_years(role)
        age = self._set_age(role)
        skill_level = self._set_skill_level()
        potential_level = self._set_potential_level(age, skill_level)
        injury = self._get_injury_proneness()

        return Player(
            player_name=self.get_player_name(),
            contract_years=contract_years,
            age=age,
            position=position,
            skill_level=skill_level,
            potential_level=potential_level,
            player_value=self._set_player_value(contract_years, age, skill_level, potential_level, injury),
            squad_hierarchy=role,
            injury_proneness=injury
        )

    def generate_transfermarkt(self, n_players: int = 10000) -> List[Player]:
        """Generate a transfermarkt of n players."""
        return [self._create_player() for _ in range(n_players)]
