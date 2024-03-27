from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import List


class SquadHierarchy(Enum):
    """Enum representation of the hierarchical roles in a squad.

    Extra Information:
    -----------------
    For the purpose of the VirtualTD simulator, we assume for every position (see `Position`), every hierarchical role
    is represented once.
    """
    STARTER = 1
    SUB = 2
    ACADEMY = 3


class Position(Enum):
    """Enum representation of positions.

    Extra Information:
    -----------------
    For the purpose of the VirtualTD simulator, we disregard playing style or individual player characteristics like
    right/left footedness etc. We assume every squad plays 4-3-3 and always has the 11 positions below on the field.
    """
    GOALKEEPER = 1
    LEFT_BACK = 2
    LEFT_CENTRE_BACK = 3
    RIGHT_CENTRE_BACK = 4
    RIGHT_BACK = 5
    LEFT_MID = 6
    CENTRE_MID = 7
    RIGHT_MID = 8
    LEFT_WING = 9
    STRIKER = 10
    RIGHT_WING = 11


@dataclass
class Player:
    """Data model for Players.

    Parameters:
    -----------
    player_name: str
        Name of the player, generated randomly.
    contract_years: float
        No. of contract years left, can never be >5.0.
    age: float
        Age (years) of the player, has to be in range 18-35.
    position: Position
        Position of the player.
    skill_level: float
        Skill level of the player, has to be in range 0-100.
    potential_level: float
        Potential level of the player, has to be in range 0-100.
    player_value: float
        Financial value (€) of the player based on a simplified model.
    squad_hierarchy: SquadHierarchy
        Hierarchical role in the squad.
    injury_proneness: float
        Probability (0-1) that a player is injured and not available for a match.
    """
    player_name: str
    contract_years: float
    age: float
    position: Position
    skill_level: float
    potential_level: float
    player_value: float
    squad_hierarchy: SquadHierarchy
    injury_proneness: float


@dataclass
class Squad:
    """Data model for squads.

    Parameters:
    -----------
    squad_name: str
        Name of the squad, generated randomly.
    squad_players: List[Player]
        List of players in the squad.
    squad_value_sum: float = field(init=False)
        Total financial value (€) of players in the squad.
    squad_value_avg: float = field(init=False)
        Average financial value (€) of players in the squad.
    squad_avg_age: float = field(init=False)
        Average age (years) of players in the squad.
    squad_avg_contract: float = field(init=False)
        Average contract years left for players in the squad.
    """
    squad_name: str
    squad_players: List[Player]
    squad_value_sum: float = field(init=False)
    squad_value_avg: float = field(init=False)
    squad_avg_age: float = field(init=False)
    squad_avg_contract: float = field(init=False)

    def __post_init__(self):
        self.squad_value_sum = self._get_squad_value_sum()
        self.squad_value_avg = self._get_squad_value_avg()
        self.squad_avg_age = self._get_squad_avg_age()
        self.squad_avg_contract = self._get_squad_avg_contract()

    def _get_squad_value_sum(self) -> float:
        """Get the total squad value (€)."""
        return sum([plr.player_value for plr in self.squad_players])

    def _get_squad_value_avg(self) -> float:
        """Get the total squad value (€)."""
        return self._get_squad_value_sum() / len(self.squad_players)

    def _get_squad_avg_age(self) -> float:
        """Get the average age per player."""
        return sum([plr.age for plr in self.squad_players]) / len(self.squad_players)

    def _get_squad_avg_contract(self) -> float:
        """Get the average contract duration left per player."""
        return sum([plr.contract_years for plr in self.squad_players]) / len(self.squad_players)


@dataclass
class League:
    """Data model for Leagues.

    Parameters:
    -----------
    league_name: str
        Name of the league, generated randomly.
    league_squads: List[squad]
        List of squads in the league.
    """
    league_name: str
    league_squads: List[Squad]
