from dataclasses import dataclass
from dataclasses import field


@dataclass
class CoachInstruction:
    """Configuration class with a coach instruction to configure a season or match simulation.

    Parameters:
    ----------
    starter_match_share: int = field(default=70)
        Relative share of matches where the best player in a position is selected.
    sub_match_share: int = field(default=20)
        Relative share of matches where the sub player in a position is selected.
    academy_match_share: int = field(default=10)
        Relative share of matches where the academy player in a position is selected.
    """
    starter_match_share: int = field(default=70)
    sub_match_share: int = field(default=20)
    academy_match_share: int = field(default=10)
