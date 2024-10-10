from random import randint, random

from core import *

MIN_SIZE = 4
SPLIT_RANGE = (0.3, 0.7)
MAX_SIZE_ROOMS = False

def generate(game: Game, depth: int, size: Tuple[int, int]):
    width = size[0]
    height = size[1]

    map = [[0 for x in range(width)] for y in range(height)]
    split_dir = randint(0, 1)
    root_node = BspNode(Rect((0, 0), size), split_dir)
    root_node.split(depth)
    print_rec(root_node)
    

def print_rec(node):
    print(node.bounds.size)
    for i in node.children:
        print_rec(i)

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
        self.split_dir = 0
    def split(self, depth: int):
        if depth == 0:
            return
        a, b = split_rect(self.bounds, self.split_dir)
        if a.width() > MIN_SIZE and a.height() > MIN_SIZE\
            and b.width() > MIN_SIZE and b.height() > MIN_SIZE:
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
            (container.pos[0], container.y() + a.width()),
            (container.width(), container.height() - a.height()),
        )
        return a, b