import math
import random
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
    def __init__(self, bounds: Rect, split_dir: int, parent):
        self.bounds = bounds
        self.children = []
        self.split_dir = split_dir
        self.parent = parent
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
            self.children.append(BspNode(a, new_split, self))
            self.children.append(BspNode(b, new_split, self))
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
        while True:
            npc_pos = (randint(inner.pos[0], inner.end()[0] - 1), randint(inner.pos[1], inner.end()[1] - 1))
            if valid_position(npc_pos[0], npc_pos[1], map, game):
                npc = npc_class(npc_pos)
                game.entities.append(npc)
                break
    
    # Generate random potions
    num_potions = randint(0, 1)
    for _ in range(num_potions):
        while True:
            potion_pos = (randint(inner.pos[0], inner.end()[0] - 1), randint(inner.pos[1], inner.end()[1] - 1))
            if valid_position(potion_pos[0], potion_pos[1], map, game):
                potion_entity = ItemEntity(HealingPotion(), potion_pos)
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

def place_npcs(node: BspNode, game: Game, rooms: list[BspNode]):
    if node.children:
        for child in node.children:
            place_npcs(child, game, rooms)
        return
    rooms.append(node)

NEIGHBOR_INDICES = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
]
def neighbor_idx_dist(a: int, b: int):
    if b > a:
        return min(b - a, 7 - (b - a - 1))
    else:
        return min(a - b, 7 - (a - b - 1))
def add_doors(game: Game, map: list[list[int]]):
    map_y = len(map)
    map_x = len(map[0])
    door_map = [[None for x in range(map_x)] for y in range(map_y)]
    door_list = []
    # Cannot handle bounds cases, [1, row/col)
    for y in range(1, len(map) - 2):
        row = map[y]
        for x in range(1, len(row) - 2):
            origin_pos = (x, y)
            tile = map[y][x]
            if tile == 1:
                voids = [] # Don't know what else to call a subsequence sequence of empty spaces.
                void = []
                for nb_idx in range(len(NEIGHBOR_INDICES)):
                    offset = NEIGHBOR_INDICES[nb_idx]
                    nb_pos = (x + offset[0], y + offset[1])
                    grid_tile = map[nb_pos[1]][nb_pos[0]]
                    # grid_valid = valid_position(nb_pos[0], nb_pos[1], map, game)
                    if len(void) == 0: # case 1, void is empty
                        if grid_tile == 1:
                            void.append(nb_idx)
                    else: # case 2, void has other tiles
                        if grid_tile == 1:
                            void.append(nb_idx)
                        else: # case 2b: make a new void if it's solid
                            voids.append(void)
                            void = []
                if void:
                    voids.append(void)
                    void = []

                if len(voids) >= 2: # connect start and end if they can connect
                    first_void = voids[0]
                    last_void = voids[len(voids) - 1]
                    start_fv = first_void[0]
                    end_lv = last_void[len(last_void) - 1]
                    if neighbor_idx_dist(start_fv, end_lv) <= 1:
                        voids = [last_void + first_void]
                if len(voids) == 2:
                    a = voids[0]
                    b = voids[1]
                    if len(a) <= 3 and len(b) <= 3:
                        if (len(a) >= 2 and len(b) == 1) or (len(a) == 1 and len(b) >= 2):
                            if a == 1: # neither can just be a corner
                                if a[0] in (0, 2, 4, 6):
                                    continue
                            elif b == 1:
                                if b[0] in (0, 2, 4, 6):
                                    continue
                            # print(origin_pos, voids)
                            new_door = core.Door(origin_pos)
                            door_map[y][x] = new_door
                            door_list.append(new_door)
    # choose one from any adjacent doors
    for y in range(1, map_x - 2):
        for x in range(1, map_y - 2):
            # if (x, y) in checked:
            #     continue
            if door_map[y][x] is not None:
                adj_doors = [door_map[y][x]]

                frontier = []
                checked = []
                for nb_offset in NEIGHBOR_INDICES:
                    nb_pos = (x + nb_offset[0], y + nb_offset[1])
                    frontier.append(nb_pos)
                while len(frontier) >= 1:
                    f_pos = frontier.pop()
                    f_door = door_map[f_pos[1]][f_pos[0]]
                    if f_door is not None:
                        adj_doors.append(f_door)
                        for nb_offset in NEIGHBOR_INDICES:
                            nb_pos = (f_pos[0] + nb_offset[0], f_pos[1] + nb_offset[1])
                            if nb_pos not in checked:
                                frontier.append(nb_pos)
                    checked.append(f_pos)

                final_door = random.choice(adj_doors)
                for i in door_list.copy():
                    if i in adj_doors and i != final_door:
                        door_list.remove(i)
    for y in range(1, map_x - 2):
        for x in range(1, map_y - 2):
            door_check = door_map[y][x]
            if door_check is not None and door_check in door_list:
                game.entities.append(door_map[y][x])


def print_rec(node: BspNode, depth:int = 0):
    # print(depth, "\t" * depth, node.bounds.pos, node.bounds.size)
    for i in node.children:
        print_rec(i, depth + 1)

# Picks a room that the player can access and is not locked.
def pick_key_room(player_room: BspNode, end_room: BspNode):
    p_next = player_room.parent
    p_pred = player_room
    e_next = end_room.parent
    e_pred = end_room
    while p_next != e_next and (p_next is not None and e_next is not None):
        p_pred = p_next
        e_pred = e_next

        p_next = p_next.parent
        e_next = e_next.parent
    top_valid = p_pred
    valid_rooms = []
    _pick_key_room_rec(top_valid, valid_rooms)
    return random.choice(valid_rooms)

def _pick_key_room_rec(node: BspNode, room_list: list[BspNode]):
    if node.children:
        for child in node.children:
            _pick_key_room_rec(child, room_list)
        return
    room_list.append(node)


def generate(game: Game, depth: int, size: Tuple[int, int]):
    game.entities = []
    game.walls = set()
    game.ground = set()

    width = size[0]
    height = size[1]
    map = [[0 for x in range(width)] for y in range(height)]
    split_dir = randint(0, 1)
    root_node = BspNode(Rect((0, 0), size), split_dir, None)
    root_node.split(depth)
    # print_rec(root_node, 0)
    paint_node(root_node, map, game)
    paint_corridors(root_node, map)
    add_doors(game, map)
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
    rooms = []
    place_npcs(root_node, game, rooms)
    start: BspNode = random.choice(rooms)
    rooms.remove(start)
    player_pos_list = []
    for x in range(start.bounds.pos[0], start.bounds.end()[0]):
        for y in range(start.bounds.pos[1], start.bounds.end()[1]):
            if valid_position(x, y, map, game):
                player_pos_list.append((x, y))
    player = game.controller_entity
    player_pos = random.choice(player_pos_list)
    if player is not None:
        player.grid_pos = player_pos
    else:
        player = (
            core.Player(player_pos)
        )
    game.entities.append(player)
    game.controller_entity = player
    # print("dungeon")
    end: BspNode = random.choice(rooms)
    end_pos_list = []
    for x in range(end.bounds.pos[0], end.bounds.end()[0]):
        for y in range(end.bounds.pos[1], end.bounds.end()[1]):
            if valid_position(x, y, map, game):
                end_pos_list.append((x, y))
    stairs_pos = random.choice(end_pos_list)
    stairs = Stairs(stairs_pos)
    game.entities.append(stairs)
    door = None
    door_dist = 0
    for i in game.entities:
        if isinstance(i, Door):
            i_dist = math.sqrt((stairs_pos[0] - i.grid_pos[0]) ** 2 + (stairs_pos[1] - i.grid_pos[1]) ** 2)
            if door is None:
                door = i
                door_dist = i_dist
            else:
                if i_dist < door_dist:
                    door = i
                    door_dist = i_dist
    door.destroy()
    locked_door = LockedDoor(door.grid_pos)
    game.entities.append(locked_door)

    key_room = pick_key_room(start, end)
    key_pos_list = []
    for x in range(key_room.bounds.pos[0], key_room.bounds.end()[0]):
        for y in range(key_room.bounds.pos[1], key_room.bounds.end()[1]):
            if valid_position(x, y, map, game):
                key_pos_list.append((x, y))
    key_entity = ItemEntity(KeyItem(), random.choice(key_pos_list))
    game.entities.append(key_entity)