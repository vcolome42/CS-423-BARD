from typing import Tuple

class Game:
    ground_map: dict[Tuple[int, int], bool]
    def __init__(self):
        self.ground_map = {}
        self.entities = []

class Entity:
    grid_pos: Tuple[int, int]
    def __init__(self):
        pass
