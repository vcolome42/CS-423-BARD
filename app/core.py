from typing import Tuple, Set

class Game:
    ground: Set[Tuple[int, int]]
    entities: list
    walls: Set[Tuple[int, int]]
    def __init__(self):
        self.ground = set()
        self.entities = []
        self.walls = set()

class Entity:
    grid_pos: Tuple[int, int]
    def __init__(self):
        pass
