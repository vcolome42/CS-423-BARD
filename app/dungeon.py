from random import randint, random, randrange

from core import *

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
        print("split ", depth)
        if depth == 0:
            return
        a, b = split_rect(self.bounds, self.split_dir)
        print(a.size, a.width() >= MIN_BOUNDS_SIZE and a.height() >= MIN_BOUNDS_SIZE)
        print(b.size, b.width() >= MIN_BOUNDS_SIZE and b.height() >= MIN_BOUNDS_SIZE)
        if a.width() >= MIN_BOUNDS_SIZE and a.height() >= MIN_BOUNDS_SIZE\
            and b.width() >= MIN_BOUNDS_SIZE and b.height() >= MIN_BOUNDS_SIZE:
            new_split = 1 if self.split_dir == 0 else 0
            self.children.append(BspNode(a, new_split))
            self.children.append(BspNode(b, new_split))
            for child in self.children:
                child.split(depth - 1)

def split_factor():
    return random() * (SPLIT_RANGE[1] - SPLIT_RANGE[0]) + SPLIT_RANGE[0]

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

def generate(game: Game, depth: int, size: Tuple[int, int]):
    width = size[0]
    height = size[1]

    map = [[0 for x in range(width)] for y in range(height)]
    split_dir = randint(0, 1)
    root_node = BspNode(Rect((0, 0), size), split_dir)
    root_node.split(depth)
    print_rec(root_node, 0)
    paint_node(root_node, map)
    paint_corridors(root_node, map)
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
    print("dungeon")
    print(test)

def print_rec(node: BspNode, depth:int = 0):
    print(depth, "\t" * depth, node.bounds.pos, node.bounds.size)
    for i in node.children:
        print_rec(i, depth + 1)

def paint_node(node: BspNode, map: list[list[int]]):
    if node.children:
        for child in node.children:
            paint_node(child, map)
        return
    room_width = randint(MIN_ROOM_SIZE, node.bounds.width() - MIN_PADDING * 2)
    room_height = randint(MIN_ROOM_SIZE, node.bounds.height() - MIN_PADDING * 2)
    inner = Rect(
        (node.bounds.pos[0] + MIN_PADDING, node.bounds.pos[1] + MIN_PADDING),
        (room_width, room_height),
    )
    for y in range(node.bounds.y(), node.bounds.end()[1]):
        for x in range(node.bounds.x(), node.bounds.end()[0]):
            map[y][x] = 2
    for y in range(inner.pos[1], inner.end()[1]):
        for x in range(inner.pos[0], inner.end()[0]):
            map[y][x] = 1

def paint_corridors(node: BspNode, map: list[list[int]]):
    if node.children:
        a: BspNode = node.children[0]
        b: BspNode = node.children[1]
        if a.split_dir == 0: # x split
            center_x = int(a.bounds.pos[0] + a.bounds.size[0] / 2)

            center_a_y = int(a.bounds.pos[1] + a.bounds.size[1] / 2)
            center_b_y = int(b.bounds.pos[1] + b.bounds.size[1] / 2)
            for i in range(center_a_y, center_b_y):
                print(center_x, i)
                map[i][center_x] = 1
        else:
            center_y = int(a.bounds.pos[1] + a.bounds.size[1] / 2)

            center_a_x = int(a.bounds.pos[0] + a.bounds.size[0] / 2)
            center_b_x = int(b.bounds.pos[0] + b.bounds.size[0] / 2)
            for i in range(center_a_x, center_b_x):
                print(i, center_y)
                map[center_y][i] = 1
        for child_node in node.children:
            paint_corridors(child_node, map)