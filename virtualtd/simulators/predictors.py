

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
            base_value: int = 1000
    ):
        """Inits ValuePredictor with an age, contract, skill level, potential and a base value."""
        self._age = player_age
        self._contract = contract_years
        self._skill = skill_level
        self._potential = potential
        self._base_value = base_value

    def _get_contract_multiplier(self) -> float:
        """Get the contract multiplier based on the assumption that a longer contract adds value."""
        self._contract = int(self._contract * 12)
        return 1 + 36 / self._contract

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

    def predict_player_value(self) -> float:
        """Predict the resulting player value."""
        value = self._get_skill_value() + self._get_potential_value()
        return value * self._get_age_multiplier() * self._get_contract_multiplier()


class DevelopmentPredictor:

    def __init__(self):
        ...


class MatchPredictor:

    def __init__(self):
        ...
