import pygame
from typing_extensions import Tuple

class Spritesheet:
    def __init__(self, filepath: str, size: Tuple[int, int]):
        self.sheet: pygame.Surface = pygame.image.load(filepath).convert_alpha()
        self.size: Tuple[int, int] = size
        self.sprites: dict[int, pygame.Surface] = {}
        self.load_sprites()
    def load_sprites(self):
        idx = 0
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                rect = pygame.Rect(x * 16, y * 16, 16, 16)
                image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
                image.blit(self.sheet, (0, 0), rect)
                self.sprites[idx] = image
                idx += 1
    def get_sprite(self, idx: int) -> pygame.Surface:
        return self.sprites[idx]
