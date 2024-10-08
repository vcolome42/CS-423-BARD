import pygame
from typing_extensions import Tuple

class Spritesheet:
    sheet: pygame.Surface
    size: Tuple[int, int]
    sprites: dict[int, pygame.Surface]
    def __init__(self, filepath: str, size: Tuple[int, int]):
        self.sheet = pygame.image.load(filepath).convert()
        self.size = size
        self.sprites = {}
        self.load_sprites()
    def load_sprites(self):
        idx = 0
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                rect = pygame.Rect(x * 16, y * 16, 16, 16)
                image = pygame.Surface(rect.size).convert()
                image.blit(self.sheet, (0, 0), rect)
                self.sprites[idx] = image
                idx += 1
    def get_sprite(self, idx: int) -> pygame.Surface:
        return self.sprites[idx]