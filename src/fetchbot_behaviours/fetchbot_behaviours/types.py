from dataclasses import dataclass

@dataclass
class NavGoal:
    pos_x: float
    pos_y: float
    rot_z: float