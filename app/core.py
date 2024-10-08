from abc import abstractmethod
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
    def create_occlusion_set(self) -> Set[Tuple[int, int]]:
        occ = set()
        for wall in self.walls:
            occ.add(wall)
        for entity in self.entities:
            if entity.collision:
                occ.add(entity.grid_pos)
        return occ

class Entity:
    grid_pos: Tuple[int, int]
    sprite_idx: int
    collision: bool = False
    def __init__(self):
        pass
    def with_grid_pos(self, grid_pos: Tuple[int, int]):
        self.grid_pos = grid_pos
        return self
    def with_sprite_idx(self, sprite_idx: int):
        self.sprite_idx = sprite_idx
        return self
    def with_collision(self, collision: bool):
        self.collision = collision
        return self

class EntityAction:
    def is_valid(self, user: Entity, game: Game) -> bool:
        return True
    @abstractmethod
    def act(self, user: Entity, game: Game):
        pass
class WaitAction:
    def act(self, user: Entity, game: Game):
        pass
class TeleportAction(EntityAction):
    target_pos: Tuple[int, int]
    def __init__(self, target_pos: Tuple[int, int]):
        self.target_pos = target_pos
    def is_valid(self, user: Entity, game: Game) -> bool:
        game_occ = game.create_occlusion_set()
        return (self.target_pos not in game_occ)
    def act(self, user: Entity, game: Game):
        user.grid_pos = self.target_pos
class MoveAction(EntityAction):
    delta_pos: Tuple[int, int]
    def __init__(self, delta_pos: Tuple[int, int]):
        self.delta_pos = delta_pos
    def is_valid(self, user: Entity, game: Game) -> bool:
        target_pos = user.grid_pos[0] + self.delta_pos[0], user.grid_pos[1] + self.delta_pos[1]
        game_occ = game.create_occlusion_set()
        return (target_pos not in game_occ)
    def act(self, user: Entity, game: Game):
        target_pos = user.grid_pos[0] + self.delta_pos[0], user.grid_pos[1] + self.delta_pos[1]
        user.grid_pos = target_pos
