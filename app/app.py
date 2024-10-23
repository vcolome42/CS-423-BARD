from enum import global_enum
from typing import Tuple

import pygame as pg
import speech_recognition as speech
import sprites
import core
import re

from dungeon import generate
from commands import commands

game = core.Game()
generate(game, 4, (32, 32))
player = (
    core.Entity()
    .with_grid_pos((5, 5))
    .with_sprite_idx(8)
)
# debug_room_size = 9
# debug_room_center = 4
# for j in range(0, debug_room_size):
#     for i in range(0, debug_room_size):
#         game.ground.add((i, j))
# for j in range(0, debug_room_size):
#     for i in range(0, debug_room_size):
#         delta = (abs(i - debug_room_center), abs(j - debug_room_center))
#         manhat_dist = delta[0] if delta[0] >= delta[1] else delta[1]
#         if manhat_dist >= 4:
#             game.walls.add((i, j))
# player = (
#     core.Entity()
#     .with_grid_pos((debug_room_center, debug_room_center))
#     .with_sprite_idx(8)
# )
game.entities.append(player)
game.controller_entity = player

# door = core.Door().with_grid_pos((debug_room_center + 1, debug_room_center))
# game.entities.append(door)

# pygame setup
pg.init()
pg.font.init()

DEFAULT_FONT = pg.font.SysFont("Arial", 24)
text_surf = DEFAULT_FONT.render("", False, (255, 255, 255))

SCREEN_SIZE = (240, 144)
RENDER_SCALE = 2

screen = pg.display.set_mode(
    (SCREEN_SIZE[0] * RENDER_SCALE, SCREEN_SIZE[1] * RENDER_SCALE), pg.RESIZABLE
)
clock = pg.time.Clock()

tiles = sprites.Spritesheet("tiles.png", (4, 4))
game_screen = pg.surface.Surface(SCREEN_SIZE)

# Manual ask_voice system.
# def ask_voice(recognizer: speech.Recognizer):
#     out = None
#     with speech.Microphone() as source:
#         try:
#             recognizer.adjust_for_ambient_noise(source, duration=0.3)
#             print("Rec start.")
#             audio_text = recognizer.listen(source, timeout=3.0, phrase_time_limit=5.0)
#             print("Rec end.")
#             out = recognizer.recognize_google(audio_text).lower()
#             print("Text: " + out)
#         except Exception as e:
#             print("Sorry, I did not get that:", e)
#     return out
# def print_voice():
#     global text_surf
#     data = ask_voice(recognizer)
#     text = f"Voice: {data}" if data else "Voice: No words recognized"
#     text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))

# Word to int (three -> 3)
def word_to_num(word: str) -> int:
    word_to_number = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }
    return word_to_number.get(word.lower(), None)

# parse and execute different commands
def parse_and_execute_command(command: str):
    global text_surf
    move_pattern = re.match(
        r".*(left|right|up|down) (\d+|one|two|three|four|five|six|seven|eight|nine|ten)",
        command,
    )
    commandFound = False
    if move_pattern:
        direction = move_pattern.group(1)
        x = move_pattern.group(2)
        if x.isdigit():
            x = int(x)
        else:
            x = word_to_num(x)
        if x is not None:
            if direction == "left":
                action = core.MoveAction((-x, 0))
            elif direction == "right":
                action = core.MoveAction((x, 0))
            elif direction == "up":
                action = core.MoveAction((0, -x))
            elif direction == "down":
                action = core.MoveAction((0, x))
            player_decide(action)
            commandFound = True
        else:
            print("Invalid number.")
            text_surf = DEFAULT_FONT.render("Invalid number.", False, (255, 0, 0))
    else:
        for commandKeys in commands:
            if commandKeys in command:
                player_decide(commands[commandKeys])
                commandFound = True

    if not commandFound:
        print("Command not recognized.")
        text_surf = DEFAULT_FONT.render("Command not recognized.", False, (255, 0, 0))

# decide_voice_debounce = False

def player_decide(action: core.EntityAction):
    player = game.controller_entity
    if action.is_valid(player, game):
        action.act(player, game)

def grid_to_draw(gridpos: Tuple[int, int]) -> Tuple[int, int]:
    return (gridpos[0] * 16, gridpos[1] * 16)
def view_grid_to_draw(gridpos: Tuple[int, int], view_pos: Tuple[int, int]) -> Tuple[int, int]:
    x = (gridpos[0] - view_pos[0]) * 16
    y = (gridpos[1] - view_pos[1]) * 16
    x += SCREEN_SIZE[0] / 2
    y += SCREEN_SIZE[1] / 2
    return (x, y)

def render_game(game: core.Game):
    local_pos = (0, 0)
    if game.controller_entity:
        local_pos = game.controller_entity.grid_pos
    for ground_gridpos in game.ground:
        game_screen.blit(tiles.get_sprite(1), view_grid_to_draw(ground_gridpos, local_pos))
    for wall_gridpos in game.walls:
        game_screen.blit(tiles.get_sprite(0), view_grid_to_draw(wall_gridpos, local_pos))
    for entity in game.entities:
        game_screen.blit(
            tiles.get_sprite(entity.sprite_idx), view_grid_to_draw(entity.grid_pos, local_pos)
        )

# def decide_voice():
#     global text_surf
#     data = ask_voice(recognizer)
#     text = f"Voice: { "\"{}\"".format(data) if data is not None else "None"}"
#     text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))
#     if data:
#         parse_and_execute_command(data)
#     else:
#         print("Command not recognized.")
#         text_surf = DEFAULT_FONT.render("Command not recognized.", False, (255, 0, 0))

def recognize_data(recognizer: speech.Recognizer, data: speech.AudioData) -> None | str:
    out = None
    try:
        out = recognizer.recognize_google(data)
        print(out)
        # out = recognizer.recognize_sphinx(data)
    except Exception as e:
        print("Listener error:", e)
    return out

def on_listener_heard(recognizer: speech.Recognizer, data: speech.AudioData):
    global text_surf
    print("heard something")
    vc_command = recognize_data(recognizer, data)
    text = f"Voice: {vc_command}" if vc_command else "Voice: No words recognized."
    text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))
    if vc_command:
        parse_and_execute_command(vc_command)
    else:
        print("Command not recognized.")
        text_surf = DEFAULT_FONT.render("Command not recognized.", False, (255, 0, 0))

RECOGNIZER = speech.Recognizer()
RECOGNIZER.dynamic_energy_threshold = False
MIC = speech.Microphone()
with MIC as source:
    print("Adjusting mic noise threshold.")
    RECOGNIZER.adjust_for_ambient_noise(source, 1.0)

stop_listener = RECOGNIZER.listen_in_background(MIC, on_listener_heard)

def main_loop():
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    player_decide(core.MoveAction((0, 1)))
                if event.key == pg.K_UP:
                    player_decide(core.MoveAction((0, -1)))
                if event.key == pg.K_LEFT:
                    player_decide(core.MoveAction((-1, 0)))
                if event.key == pg.K_RIGHT:
                    player_decide(core.MoveAction((1, 0)))

                # if event.key == pg.K_SPACE:
                #     text = "LISTENING: "
                #     text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255))
                #     decide_voice_debounce = True

        # Render steps
        game_screen.fill("black")
        render_game(game)

        screen.fill("black")
        screen.blit(pg.transform.scale(game_screen, screen.get_rect().size), (0, 0))
        screen.blit(text_surf, (0, 0))

        # flip buffer to display
        pg.display.flip()

        # if decide_voice_debounce:
        #     decide_voice()
        #     decide_voice_debounce = False

        clock.tick(60)
try:
    main_loop()
except Exception as e:
    print(f"Game crashed: {e}")
pg.quit()
stop_listener(False)
