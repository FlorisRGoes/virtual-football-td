import random
from typing import Tuple


class AgeConstraint:
    """Constraint class for the generation of random player ages.

    Extra Information:
    -----------------
    If the player profile contains a starter of substitute player, randomly generates an age from a normal
    distribution with mean 25±3.5 years. All ages should be between 18 and 25 years.

    If the player profile contains an academy player, randomly generates an age from a normal
    distribution with mean 18.5±1 years. All ages should be between 17 and 21 years.

    Parameters:
    ----------
    min_age: int = 18
        Minimum age of the population.
    max_age: int = 35
        Minimum age of the population.
    max_acd_age: int = 21
        Maximum age of the academy players.

    Methods:
    -------
    get_regular_age(mu: float = 25.0, sigma: float = 3.5) -> float
        Randomly generates the age of a regular (non-academy).
    get_academy_age(mu: float = 18.5, sigma: float = 1.0) -> float
        Randomly generates the age of an academy player.
    """

    def __init__(self, min_age: int = 18, max_age: int = 35, max_acd_age: int = 21):
        """Inits AgeConstraint with a minimum age, a maximum age and a maximum academy age."""
        self._min_age = min_age
        self._max_age = max_age
        self._max_acd_age = max_acd_age

    def get_regular_age(self, mu: float = 25.0, sigma: float = 3.5) -> float:
        """Randomly generates the age of a regular (non-academy)."""
        age = random.normalvariate(mu, sigma)
        while age < self._min_age or age > self._max_age:
            age = random.normalvariate(mu, sigma)

        return age

    def get_academy_age(self, mu: float = 18.5, sigma: float = 1.0) -> float:
        """Randomly generates the age of an academy player."""
        age = random.normalvariate(mu, sigma)
        while age < self._min_age or age > self._max_acd_age:
            age = random.normalvariate(mu, sigma)

        return age


class ContractConstraint:
    """Constraint class for the generation of random player contracts.

    Extra Information:
    -----------------
    As a simulation always starts in the summer break, we assume all player start on contract for the full season.
    Player contracts are constraint to a maximum of 5 years, and academy players are constraint to a maximum of
    3 years.

    Parameters:
    ----------
    min_length: int = 1
        Minimal contract length in years.
    max_length: int = 5
        Maximal contract length in years.
    max_acd_length: int = 3
        Maximal contract length for academy players.

    Methods:
    -------
    get_regular_contract(mu: float = 25.0, sigma: float = 3.5) -> float
        Randomly generates a contract for a regular (non-academy) player.
    get_academy_contract(mu: float = 18.5, sigma: float = 1.0) -> float
        Randomly generates a contract for an academy player.
    """

    def __init__(self, min_length: int = 1, max_length: int = 5, max_acd_length: int = 3):
        """Inits ContractConstraint with a minimum length, a maximum length and a maximum academy length."""
        self._min_length = min_length
        self._max_length = max_length
        self._max_acd_length = max_acd_length

    def get_regular_contract(self) -> int:
        """Randomly generates a contract for a regular (non-academy) player."""
        return random.randint(self._min_length, self._max_length)

    def get_academy_contract(self) -> int:
        """Randomly generates a contract for an academy player."""
        return random.randint(self._min_length, self._max_length)


class SkillConstraint:
    """Constraint class for the generation of skill levels.

    Extra Information
    ----------------
    This class works on the assumption that the skill level of any academy player can never exceed the skill level
    of any substitute, as the level of any substitute can never exceed the level of any starter.

    Parameters:
    ----------
    team_strength: float
        Mean skill level of the starting 11.
    strength_sd: float
        Deviation of the skill level across the team.

    Methods:
    -------
    get_starter_skill(self) -> float
        Get the skill level for a player with a starter profile.
    get_sub_skill(self) -> float
        Get the skill level for a player with a sub profile.
    get_academy_skill(self) -> float
        Get the skill level for a player with an academy profile.
    """

    def __init__(self, team_strength: float, strength_sd: float):
        """Inits SkillConstraint with a team strength level and a SD."""
        self._team_strength = team_strength
        self._strength_sd = strength_sd

    def _get_valid_range(self, range_k: float, shift: float = 0.0) -> Tuple[float, float]:
        """Check if a generated value is within a valid range."""
        mu = self._team_strength - shift
        if mu - range_k > 0.0:
            lower = mu - range_k
        else:
            lower = 0
        if mu + range_k < 100.0:
            upper = self._team_strength + range_k
        else:
            upper = 100

        return lower, upper

    def get_starter_skill(self) -> float:
        """Get the skill level for a player with a starter profile.

        Extra Information:
        -----------------
        Any starter gets a randomly generated skill level in range team_strength - 0.5SD : team_strength + 0.5SD.
        """
        range_k = 0.5 * self._strength_sd
        lower, upper = self._get_valid_range(range_k)

        return random.uniform(lower, upper)

    def get_sub_skill(self) -> float:
        """Get the skill level for a player with a sub profile.

        Extra Information:
        -----------------
        Any sub gets a randomly generated skill level in range
        (team_strength - SD) - 0.5SD : (team_strength - SD) + 0.5SD.
        """
        range_k = 0.5 * self._strength_sd
        shift = self._strength_sd
        lower, upper = self._get_valid_range(range_k, shift)

        return random.uniform(lower, upper)

    def get_academy_skill(self) -> float:
        """Get the skill level for a player with an academy profile.

        Extra Information:
        -----------------
        Any academy player gets a randomly generated skill level in range
        (team_strength - SD) - 0.5SD : (team_strength - SD) + 0.5SD.
        """
        range_k = 0.5 * self._strength_sd
        shift = 1.5 * self._strength_sd
        lower, upper = self._get_valid_range(range_k, shift)

        return random.uniform(lower, upper)


class PotentialConstraint:
    """Constraint class for the generation of potential values.

    Extra Information:
    -----------------
    Player potential is assumed to be limited by age, young players have unlimited potential, players in their prime
    (24-28) are expected to only moderately increase there skill levels, and players over 28 are expected not to
    further improve their skill levels.

    Parameters:
    ----------
    age: float
        Age (years) of the player, has to be in range 18-35.
    skill_level: float
        Player skill level.
    strength_sd: float
        Deviation of the skill level across the team.

    Methods:
    -------
    get_potential(self) -> float
        Get a randomly generated potential value based on a player's age and current skill level.
    """

    def __init__(self, age: float, skill_level: float, strength_sd: float):
        """Inits PotentialConstraint with an age, skill level and skill SD."""
        self._age = age
        self._skill_level = skill_level
        self._strength_sd = strength_sd

    def _get_young_player_potential(self) -> float:
        """Get the potential of players below 28."""
        lower = self._skill_level
        upper = 100

        return random.uniform(lower, upper)

    def _get_prime_player_potential(self) -> float:
        """Get the potential for players between 24-28."""
        lower = self._skill_level
        upper = self._skill_level + self._strength_sd

        return random.uniform(lower, upper)

    def _get_old_player_potential(self) -> float:
        """Get the potential for players over 28."""
        return self._skill_level

    def get_potential(self) -> float:
        """Get a randomly generated potential value based on a player's age and current skill level."""
        if self._age <= 24:
            return self._get_young_player_potential()
        elif 24 < self._age < 28:
            return self._get_prime_player_potential()
        else:
            return self._get_old_player_potential()
