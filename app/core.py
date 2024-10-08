from typing import Tuple, Set

class Game:
    ground: Set[Tuple[int, int]]
    entities: list
    controller_entity = None
    walls: Set[Tuple[int, int]]
    def __init__(self):
        self.ground = set()
        self.entities = []
        self.walls = set()

class Entity:
    grid_pos: Tuple[int, int]
    sprite_idx: int
    def __init__(self):
        pass
    def with_grid_pos(self, grid_pos: Tuple[int, int]):
        self.grid_pos = grid_pos
        return self
    def with_sprite_idx(self, sprite_idx: int):
        self.sprite_idx = sprite_idx
        return self
