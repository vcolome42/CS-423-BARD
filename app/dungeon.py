from random import randint, choice
from core import *
import random as randomFix
import core
from items import HealingPotion

MIN_BOUNDS_SIZE = 6
SPLIT_RANGE = (0.4, 0.6)
MAX_SIZE_ROOMS = False

MIN_PADDING = 1
MIN_ROOM_SIZE = 4

class Rect:
    pos: Tuple[int, int]
    size: Tuple[int, int]
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
    def x(self):
        return self.pos[0]
    def y(self):
        return self.pos[1]
    def width(self):
        return self.size[0]
    def height(self):
        return self.size[1]
    def end(self):
        return (self.pos[0] + self.size[0], self.pos[1] + self.size[1])

class BspNode:
    def __init__(self, bounds: Rect, split_dir: int):
        self.bounds = bounds
        self.children = []
        self.split_dir = split_dir
    def split(self, depth: int):
        # print("split ", depth)
        if depth == 0:
            return
        a, b = split_rect(self.bounds, self.split_dir)
        # print(a.size, a.width() >= MIN_BOUNDS_SIZE and a.height() >= MIN_BOUNDS_SIZE)
        # print(b.size, b.width() >= MIN_BOUNDS_SIZE and b.height() >= MIN_BOUNDS_SIZE)
        if a.width() >= MIN_BOUNDS_SIZE and a.height() >= MIN_BOUNDS_SIZE\
            and b.width() >= MIN_BOUNDS_SIZE and b.height() >= MIN_BOUNDS_SIZE:
            new_split = 1 if self.split_dir == 0 else 0
            self.children.append(BspNode(a, new_split))
            self.children.append(BspNode(b, new_split))
            for child in self.children:
                child.split(depth - 1)

def split_factor():
    return randomFix.random() * (SPLIT_RANGE[1] - SPLIT_RANGE[0]) + SPLIT_RANGE[0]

def split_rect(container: Rect, split_dir: int) -> Tuple[Rect, Rect]:
    start = container.pos
    end = container.end()
    f = split_factor()
    if split_dir == 0:
        split_x = randint(start[0], end[0])
        a = Rect(
            container.pos,
            (int(container.width() * f), container.height()),
        )
        b = Rect(
            (container.pos[0] + a.width(), container.y()),
            (container.width() - a.width(), container.height()),
        )
        return a, b
    else:
        split_y = randint(start[1], end[1])
        a = Rect(
            container.pos,
            (container.width(), int(container.height() * f)),
        )
        b = Rect(
            (container.pos[0], container.y() + a.height()),
            (container.width(), container.height() - a.height()),
        )
        return a, b

def valid_position(x, y, map, game):
    if map[y][x] != 1:
        return False
    for entity in game.entities:
        if entity.grid_pos == (x, y):
            return False
    return True

def paint_node(node: BspNode, map: list[list[int]], game: Game):
    if node.children:
        for child in node.children:
            paint_node(child, map, game)
        return
    
    room_width = randint(MIN_ROOM_SIZE, node.bounds.width() - MIN_PADDING * 2)
    room_height = randint(MIN_ROOM_SIZE, node.bounds.height() - MIN_PADDING * 2)
    margin_width = node.bounds.width() - room_width
    margin_height = node.bounds.height() - room_height
    margin_left = int(margin_width / 2)
    margin_top = int(margin_height / 2)
    inner = Rect(
        (node.bounds.pos[0] + margin_left, node.bounds.pos[1] + margin_top),
        (room_width, room_height),
    )

    for y in range(node.bounds.y(), node.bounds.end()[1]):
        for x in range(node.bounds.x(), node.bounds.end()[0]):
            map[y][x] = 2

    for y in range(inner.pos[1], inner.end()[1]):
        for x in range(inner.pos[0], inner.end()[0]):
            map[y][x] = 1

    # Generate 0-2 NPCs randomly
    num_npcs = randint(0, 2)
    npc_classes = [Slime, Skeleton]
    for _ in range(num_npcs):
        npc_class = choice(npc_classes)
        npc = npc_class(game)
        while True:
            npc_pos = (randint(inner.pos[0], inner.end()[0] - 1), randint(inner.pos[1], inner.end()[1] - 1))
            if valid_position(npc_pos[0], npc_pos[1], map, game):
                npc.with_grid_pos(npc_pos)
                game.entities.append(npc)
                break
    
    # Generate random potions
    num_potions = randint(0, 1)
    for _ in range(num_potions):
        potion_entity = ItemEntity(HealingPotion())
        while True:
            potion_pos = (randint(inner.pos[0], inner.end()[0] - 1), randint(inner.pos[1], inner.end()[1] - 1))
            if valid_position(potion_pos[0], potion_pos[1], map, game):
                potion_entity.with_grid_pos(potion_pos)
                game.entities.append(potion_entity)
                break

def paint_corridors(node: BspNode, map: list[list[int]]):
    if node.children:
        a: BspNode = node.children[0]
        b: BspNode = node.children[1]
        if a.split_dir == 0:  # x split
            center_x = int(a.bounds.pos[0] + a.bounds.size[0] / 2)
            center_a_y = int(a.bounds.pos[1] + a.bounds.size[1] / 2)
            center_b_y = int(b.bounds.pos[1] + b.bounds.size[1] / 2)
            for i in range(center_a_y, center_b_y):
                # print(center_x, i)
                map[i][center_x] = 1
        else:
            center_y = int(a.bounds.pos[1] + a.bounds.size[1] / 2)
            center_a_x = int(a.bounds.pos[0] + a.bounds.size[0] / 2)
            center_b_x = int(b.bounds.pos[0] + b.bounds.size[0] / 2)
            for i in range(center_a_x, center_b_x):
                # print(i, center_y)
                map[center_y][i] = 1
        for child_node in node.children:
            paint_corridors(child_node, map)

def place_npcs(node: BspNode, game: Game):
    if node.children:
        for child in node.children:
            place_npcs(child, game)
        return


def add_doors(game: Game, map: list[list[int]], num_doors: int):
    door_count = 0
    while door_count < num_doors:
        x, y = randint(0, len(map[0]) - 1), randint(0, len(map) - 1)
        if valid_position(x, y, map, game):
            door = core.Door().with_grid_pos((x, y))
            game.entities.append(door)
            door_count += 1

def print_rec(node: BspNode, depth:int = 0):
    # print(depth, "\t" * depth, node.bounds.pos, node.bounds.size)
    for i in node.children:
        print_rec(i, depth + 1)

def generate(game: Game, depth: int, size: Tuple[int, int]):
    width = size[0]
    height = size[1]
    map = [[0 for x in range(width)] for y in range(height)]
    split_dir = randint(0, 1)
    root_node = BspNode(Rect((0, 0), size), split_dir)
    root_node.split(depth)
    # print_rec(root_node, 0)
    paint_node(root_node, map, game)
    paint_corridors(root_node, map)
    add_doors(game, map, randint(1, 3))
    test = ""
    for y in range(height):
        line = ""
        for x in range(width):
            if map[y][x] == 1:
                game.ground.add((x, y))
                line += "."
            elif map[y][x] == 2:
                game.walls.add((x, y))
                line += "#"
            else:
                line += " "
        test += line + "\n"
    player = (
        core.Player(game)
        .with_grid_pos((5, 5))
        .with_sprite_idx(8)
    )
    game.entities.append(player)
    game.controller_entity = player
    # print("dungeon")