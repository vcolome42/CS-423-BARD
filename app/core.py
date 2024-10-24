from abc import abstractmethod
from typing import Tuple, Set
from items import *
import random


class Game:
    ground: Set[Tuple[int, int]]
    entities: list
    controller_entity = None
    walls: Set[Tuple[int, int]]
    def __init__(self):
        self.ground = set()
        self.entities = []
        self.walls = set()
        self.game_over = False
    def step(self):
        self.entities = [entity for entity in self.entities if not entity.destroyed]
        for entity in self.entities:
            if entity != self.controller_entity and isinstance(entity, Character):
                distance_x = abs(entity.grid_pos[0] - self.controller_entity.grid_pos[0])
                distance_y = abs(entity.grid_pos[1] - self.controller_entity.grid_pos[1])
                if distance_x <= 1 and distance_y <= 1:
                    if random.random() > 0.5:  # 50% chance entity attacks
                        entity.attack(self.controller_entity)
                        print(f"{entity} attacked {self.controller_entity}")




    def create_occlusion_set(self) -> Set[Tuple[int, int]]:
        occ = set()
        for wall in self.walls:
            occ.add(wall)
        for entity in self.entities:
            if entity.collision:
                occ.add(entity.grid_pos)
        return occ
    def create_description(self):
        return {
            "entities": [
                {
                    "synonyms": entity.get_synonym_list(),
                    "flags": entity.get_flags(),
                } for entity in self.entities
            ]
        }

class Entity:
    grid_pos: Tuple[int, int]
    sprite_idx: int
    collision: bool = False
    destroyed: bool = False
    def with_grid_pos(self, grid_pos: Tuple[int, int]):
        self.grid_pos = grid_pos
        return self
    def with_sprite_idx(self, sprite_idx: int):
        self.sprite_idx = sprite_idx
        return self
    def with_collision(self, collision: bool):
        self.collision = collision
        return self
    def get_synonym_list(self) -> Set[str]:
        return set()
    def get_flags(self) -> Set[str]:
        return set()

    def destroy(self):
        self.destroyed = True

class Character(Entity):
    def __init__(self, game: Game, health: int, attack_damage: int):
        super().__init__()
        self.game = game
        self.health = health
        self.attack_damage = attack_damage

    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.destroy()

    def attack(self, target: 'Character'):
        if isinstance(target, Character):
            target.take_damage(self.attack_damage)
            print(f"{self} attacked {target}")

    def destroy(self):
        self.destroyed = True
        if self == self.game.controller_entity:
            print("game over")
            self.game.game_over = True


class Door(Entity):
    opened: bool = False
    def __init__(self):
        self.sprite_idx = 2
        self.collision = True
    def set_opened(self, opened: bool):
        self.opened = opened
        self.collision = not opened
        self.sprite_idx = 6 if opened else 2
    def get_synonym_list(self) -> Set[str]:
        return super().get_synonym_list().union({
            "door",
            "gate",
            "entrance",
            "exit",
        })
    def get_flags(self) -> Set[str]:
        return super().get_flags().union({
            "opened" if self.opened else "closed"
        })

class ItemEntity(Entity):
    item: Item
    def get_synonym_list(self) -> Set[str]:
        return super().get_synonym_list().union({
            "item",
        })

class Player(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=100, attack_damage=10)
        self.sprite_idx = 8

class Slime(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=20, attack_damage=5)
        self.sprite_idx = 9
        self.collision = True

class Skeleton(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=30, attack_damage=7)
        self.sprite_idx = 13
        self.collision = True

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

# Moves character up,down,right,right until a obstacle
class MoveUntilObstacleAction(EntityAction):
    def __init__(self, direction: Tuple[int, int]):
        self.direction = direction

    def act(self, user: Entity, game: Game):
        while True:
            target_pos = (user.grid_pos[0] + self.direction[0], user.grid_pos[1] + self.direction[1])
            if target_pos in game.create_occlusion_set():
                break
            user.grid_pos = target_pos

class AttackAction(EntityAction):
    def act(self, user: Character, game: Game):
        # find nearby enemies
        for entity in game.entities:
            if isinstance(entity, Character) and entity != user:
                if abs(user.grid_pos[0] - entity.grid_pos[0]) <= 1 and abs(user.grid_pos[1] - entity.grid_pos[1]) <= 1:
                    user.attack(entity)
                    print(f"{user} attacked {entity}")
                    break
