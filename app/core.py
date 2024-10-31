from abc import abstractmethod
from typing import Tuple, Set
from items import *
import random


class Game:
    def __init__(self):
        self.ground: Set[Tuple[int, int]] = set()
        self.entities: list = []
        self.walls: Set[Tuple[int, int]] = set()
        self.controller_entity = None
        self.game_over = False
        self.next_level = False
        self.inventory_open = False
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
        if self.controller_entity:
            for i in self.entities:
                if isinstance(i, Stairs):
                    if i.grid_pos == self.controller_entity.grid_pos:
                        self.next_level = True

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
                    "_type": type(entity),
                    "synonyms": entity.get_synonym_list(),
                    "flags": entity.get_flags(),
                    "appearance": entity.get_appearance(self.controller_entity) if self.controller_entity else None,
                } for entity in [e for e in self.entities if e != self.controller_entity]
            ]
        }

class Entity:
    def __init__(self, grid_pos: Tuple[int, int]):
        self.grid_pos = grid_pos
        self.sprite_idx: int = 15
        self.collision: bool = False
        self.destroyed: bool = False
    def with_grid_pos(self, grid_pos: Tuple[int, int]):
        self.grid_pos = grid_pos
        return self
    def with_sprite_idx(self, sprite_idx: int):
        self.sprite_idx = sprite_idx
        return self
    def with_collision(self, collision: bool):
        self.collision = collision
        return self
    def can_interact(self):
        return False
    def interact(self, user):
        pass

    def get_synonym_list(self) -> Set[str]:
        return set()
    def get_flags(self) -> Set[str]:
        return set()
    def get_appearance(self, viewer: 'Entity') -> Set[str]:
        appearance = set()
        dist = (self.grid_pos[0] - viewer.grid_pos[0], self.grid_pos[1] - viewer.grid_pos[1])
        if dist[0] > 1:
            appearance.add("to the right")
            appearance.add("in the right")
            appearance.add("right")
        if dist[0] < -1:
            appearance.add("to the left")
            appearance.add("in the left")
            appearance.add("left")
        if dist[1] > 1:
            appearance.add("in the bottom")
            appearance.add("below")
        if dist[1] < -1:
            appearance.add("at the top")
            appearance.add("above")
        if abs(dist[0]) <= 1 and abs(dist[1]) <= 1:
            appearance.add("nearby")
        return appearance

    def destroy(self):
        self.destroyed = True

class Character(Entity):
    def __init__(self, grid_pos: tuple[int, int], game: Game, health: int, attack_damage: int):
        super().__init__(grid_pos)
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
    def __init__(self, grid_pos: Tuple[int, int]):
        super().__init__(grid_pos)
        self.opened = False
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
    def can_interact(self):
        return True
    def interact(self, user):
        self.set_opened(not self.opened)

class Stairs(Entity):
    def __init__(self, grid_pos: Tuple[int, int]):
        super().__init__(grid_pos)
        self.sprite_idx = 3
        self.collision = False

class LockedDoor(Entity):
    def __init__(self, grid_pos: Tuple[int, int]):
        super().__init__(grid_pos)
        self.opened: bool = False
        self.sprite_idx = 5
        self.collision = True
    def set_opened(self, opened: bool):
        self.opened = opened
        self.collision = not opened
        self.sprite_idx = -1 if opened else 5
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
    def can_interact(self):
        return True
    def interact(self, user):
        if isinstance(user, Player):
            if user.use_item("Key"):
                self.set_opened(True)
            else:
                print("You don't have a key")

class ItemEntity(Entity):
    def __init__(self, item: Item, grid_pos: Tuple[int, int]):
        super().__init__(grid_pos)
        self.item = item
        self.sprite_idx = item.sprite_idx
        self.collision = False
    def get_synonym_list(self) -> Set[str]:
        return super().get_synonym_list().union({
            self.item.name.lower(),
            "potion",
            "health potion"
        })

class Player(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=100, attack_damage=10)
        self.max_health = 100
        self.inventory = {}
        self.sprite_idx = 8

    def add_to_inventory(self, item: Item):
        if item.name in self.inventory:
            self.inventory[item.name]['quantity'] += 1
        else:
            self.inventory[item.name] = {'item': item, 'quantity': 1}
        print(f"{item.name} added to inventory.")

    def use_item(self, item_name: str):
        if item_name in self.inventory and self.inventory[item_name]['quantity'] > 0:
            item = self.inventory[item_name]['item']
            item.use(self)
            self.inventory[item_name]['quantity'] -= 1
            if self.inventory[item_name]['quantity'] == 0:
                del self.inventory[item_name]
            return True
        else:
            print(f"No {item_name} in inventory.")
            return False

class Slime(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=20, attack_damage=5)
        self.sprite_idx = 9
        self.collision = True
    def get_synonym_list(self) -> Set[str]:
        return super().get_synonym_list().union({
            "slime",
            "enemy",
        })

class Skeleton(Character):
    def __init__(self, game: Game):
        super().__init__(game, health=30, attack_damage=7)
        self.sprite_idx = 13
        self.collision = True
    def get_synonym_list(self) -> Set[str]:
        return super().get_synonym_list().union({
            "skeleton",
            "enemy",
        })

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
    def __init__(self, target_pos: Tuple[int, int]):
        self.target_pos = target_pos
    def is_valid(self, user: Entity, game: Game) -> bool:
        game_occ = game.create_occlusion_set()
        return (self.target_pos not in game_occ)
    def act(self, user: Entity, game: Game):
        user.grid_pos = self.target_pos
class MoveAction(EntityAction):
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

class OpenInventoryAction(EntityAction):
    def act(self, user: Entity, game: Game):
        game.inventory_open = True
        print("Inventory opened.")

class CloseInventoryAction(EntityAction):
    def act(self, user: Entity, game: Game):
        game.inventory_open = False
        print("Inventory closed.")

class UseItemAction(EntityAction):
    def __init__(self, item_name: str):
        self.item_name = item_name

    def is_valid(self, user: Entity, game: Game) -> bool:
        return self.item_name in user.inventory

    def act(self, user: Entity, game: Game):
        user.use_item(self.item_name)

class PickUpAction(EntityAction):
    def are_positions_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx <= 1 and dy <= 1)
    
    def is_valid(self, user: Entity, game: Game) -> bool:
        for entity in game.entities:
            if isinstance(entity, ItemEntity):
                if self.are_positions_adjacent(user.grid_pos, entity.grid_pos):
                    return True
        return False

    def act(self, user: Entity, game: Game):
        items_to_pick = []
        for entity in game.entities:
            if isinstance(entity, ItemEntity):
                if self.are_positions_adjacent(user.grid_pos, entity.grid_pos):
                    items_to_pick.append(entity)

        if items_to_pick:
            for item_entity in items_to_pick:
                user.add_to_inventory(item_entity.item)
                game.entities.remove(item_entity)
                print(f"Picked up {item_entity.item.name}.")
        else:
            print("No items nearby to pick up.")

class InteractAction(EntityAction):
    def __init__(self, target: Entity):
        self.target = target
    def are_positions_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return dx <= 1 and dy <= 1
    def is_valid(self, user: Entity, game: Game) -> bool:
        return self.target.can_interact() and self.are_positions_adjacent(user.grid_pos, self.target.grid_pos)
    def act(self, user: Character, game: Game):
        self.target.interact(user)

class InteractEverything(EntityAction):
    def are_positions_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx <= 1 and dy <= 1)
    def is_valid(self, user: Entity, game: Game) -> bool:
        nearby = []
        for entity in game.entities:
            if self.are_positions_adjacent(user.grid_pos, entity.grid_pos):
                if entity.can_interact():
                    nearby.append(entity)
        if nearby:
            return True
        return False
    def act(self, user: Entity, game: Game):
        nearby = []
        for entity in game.entities:
            if self.are_positions_adjacent(user.grid_pos, entity.grid_pos):
                if entity.can_interact():
                    nearby.append(entity)
        if nearby:
            for entity in nearby:
                entity.interact(user)
                print(f"Interacted with {entity.get_synonym_list()}.")
        else:
            print("No nearby interactables.")
