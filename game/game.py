# Example file showing a basic pygame "game loop"
import pygame as pg

# pygame setup
pg.init()
pg.font.init()

DEFAULT_FONT = pg.font.SysFont("Arial", 24)
text_surf = DEFAULT_FONT.render("Hello world", False, (255, 255, 255))

screen = pg.display.set_mode((640, 480), pg.RESIZABLE)
clock = pg.time.Clock()
running = True


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    screen.blit(text_surf, (0, 0))

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()