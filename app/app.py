from enum import global_enum
from typing import Tuple

import pygame as pg
import speech_recognition as speech

import sprites
import items
import core
import re

from dungeon import generate
from dotenv import dotenv_values

from commands import (
    action_keywords,
    direction_keywords,
    item_keywords,
    connectors,
    number_words,
    patterns,
)

SECRETS = dotenv_values(".env.secret")

import ssl 
ssl._create_default_https_context = ssl._create_unverified_context

class SrModel:
    GOOGLE = 1
    WHISPER_LOCAL = 2
    WHISPER_API = 3
SR_MODEL = SrModel.WHISPER_LOCAL

WHISPER_API_KEY = None
if "API_KEY" in SECRETS:
    WHISPER_API_KEY = SECRETS["API_KEY"]
    print("Whisper API Key found:", WHISPER_API_KEY)
    if SR_MODEL != SrModel.WHISPER_API:
        print("[WARN] Whisper API key found but not using SrModel.WHISPER_API")

CONTROLS = True
CHEATS = True

# Print microphones as list
# for i, microphone_name in enumerate(speech.Microphone.list_microphone_names()):
#     print(i, microphone_name)

game = core.Game()
generate(game, 4, (32, 32))

# pygame setup
pg.init()
pg.font.init()

DEFAULT_FONT = pg.font.SysFont("Arial", 12)
text_surf = DEFAULT_FONT.render("", False, (255, 255, 255), (0, 0, 0))

INFO_FONT = pg.font.Font("m3x6.ttf", 16)

SCREEN_SIZE = (240, 144)
RENDER_SCALE = 2

screen = pg.display.set_mode(
    (SCREEN_SIZE[0] * RENDER_SCALE, SCREEN_SIZE[1] * RENDER_SCALE), pg.RESIZABLE
)
clock = pg.time.Clock()

tiles = sprites.Spritesheet("tiles.png", (4, 4))
game_screen = pg.surface.Surface(SCREEN_SIZE)

def word_to_num(word: str) -> int:
    word = word.lower()
    return number_words.get(word, None)

def parse_and_execute_command(command: str):
    global text_surf
    actions = parse_command_sequence(command)
    if not actions:
        print("Command not recognized.")
        text_surf = DEFAULT_FONT.render("Command not recognized.", False, (255, 0, 0), (0, 0, 0))
        return

    for action in actions:
        try:
            action_type = action[0]
            if action_type == "move":
                _, dx, dy, steps = action
                move_action = core.MoveAction((dx, dy), steps)
                player_decide(move_action)
            elif action_type == "move_until_obstacle":
                _, dx, dy = action
                move_until_obstacle_action = core.MoveUntilObstacleAction((dx, dy))
                player_decide(move_until_obstacle_action)
            elif action_type == "attack":
                player_decide_nodelay(core.AttackAction())
            elif action_type == "pickup":
                player_decide_nodelay(core.PickUpAction())
            elif action_type == "use":
                _, item_name = action
                player_decide_nodelay(core.UseItemAction(item_name))
            elif action_type == "interact":
                player_decide_nodelay(core.InteractEverything())
            elif action_type == "open_inventory":
                player_decide_nodelay(core.OpenInventoryAction())
            elif action_type == "close_inventory":
                player_decide_nodelay(core.CloseInventoryAction())
            else:
                print(f"Unhandled action type: {action_type}")
        except Exception as e:
            print(e)

# parse and execute different commands
def parse_command_sequence(command: str):
    # Split the command
    command_parts = re.split(r'\b(?:' + '|'.join(connectors) + r')\b', command)
    actions = []
    for part in command_parts:
        part = part.strip()
        if part:
            action = parse_single_command(part)
            if action:
                actions.append(action)
    return actions

def parse_single_command(command: str):
    command = command.lower()
    if command in direction_keywords:
        dx, dy = direction_keywords[command]
        return ("move", dx, dy, 1)
    for action_type, pattern in patterns.items():
        match = re.match(pattern, command)
        if match:
            if action_type == "move":
                direction = match.group("direction")
                steps = match.group("steps")
                if direction in direction_keywords:
                    dx, dy = direction_keywords[direction]
                    if steps:
                        if steps in ["until", "till", "to"]:
                            return ("move_until_obstacle", dx, dy)
                        steps = word_to_num(steps) if steps.isalpha() else int(steps)
                    else:
                        steps = 1
                    return ("move", dx, dy, steps)
            elif action_type == "attack":
                return ("attack",)
            elif action_type == "pickup":
                return ("pickup",)
            elif action_type == "use":
                item = match.group("item")
                if item in item_keywords:
                    return ("use", item_keywords[item])
            elif action_type == "interact":
                return ("interact",)
            elif action_type == "open":
                return ("open_inventory",)
            elif action_type == "close":
                return ("close_inventory",)
    return None
# decide_voice_debounce = False

def player_decide(action: core.EntityAction):
    global text_surf
    player = game.controller_entity
    if action.is_valid(player, game):
        player.action_queue.append(action)
        # action.act(player, game)
        # game.step()
    else:
        if isinstance(action, core.PickUpAction):
            text_surf = DEFAULT_FONT.render("No items nearby to pick up.", False, (255, 0, 0), (0, 0, 0))
        elif isinstance(action, core.InteractEverything):
            text_surf = DEFAULT_FONT.render("No interactables.", False, (255, 0, 0), (0, 0, 0))
        else:
            text_surf = DEFAULT_FONT.render("Action is not valid.", False, (255, 0, 0), (0, 0, 0))

def player_decide_nodelay(action: core.EntityAction):
    global text_surf
    player = game.controller_entity
    if action.is_valid(player, game):
        action.act(player, game)
        game.step()
    else:
        if isinstance(action, core.PickUpAction):
            text_surf = DEFAULT_FONT.render("No items nearby to pick up.", False, (255, 0, 0), (0, 0, 0))
        elif isinstance(action, core.InteractEverything):
            text_surf = DEFAULT_FONT.render("No interactables.", False, (255, 0, 0), (0, 0, 0))
        else:
            text_surf = DEFAULT_FONT.render("Action is not valid.", False, (255, 0, 0), (0, 0, 0))

def grid_to_draw(gridpos: Tuple[int, int]) -> Tuple[int, int]:
    return (gridpos[0] * 16, gridpos[1] * 16)
def view_grid_to_draw(gridpos: Tuple[int, int], view_pos: Tuple[int, int]) -> Tuple[int, int]:
    x = (gridpos[0] - view_pos[0]) * 16
    y = (gridpos[1] - view_pos[1]) * 16
    x += SCREEN_SIZE[0] / 2
    y += SCREEN_SIZE[1] / 2
    return (x, y)

DAMAGE_ANIM_DURATION = 600.0 # milliseconds

def render_game(game: core.Game):
    local_pos = (0, 0)
    if game.controller_entity:
        local_pos = game.controller_entity.grid_pos
    for ground_gridpos in game.ground:
        game_screen.blit(tiles.get_sprite(1), view_grid_to_draw(ground_gridpos, local_pos))
    for wall_gridpos in game.walls:
        game_screen.blit(tiles.get_sprite(0), view_grid_to_draw(wall_gridpos, local_pos))
    for entity in game.entities:
        if not entity.destroyed:  # Check if the entity is not destroyed
            if entity.sprite_idx != -1:
                sprite = tiles.get_sprite(entity.sprite_idx)
                # sprite_mask = tiles.get_mask(entity.sprite_idx)

                entity_blit = pg.Surface(sprite.size, pg.SRCALPHA).convert_alpha()
                entity_blit.blit(sprite)

                if isinstance(entity, core.Character):
                    if entity.damaged_hint_check:
                        entity.damaged_hint_check = False
                        entity.damaged_hint_frame = elapsed
                        entity.damaged_hint = True
                    if entity.damaged_hint:
                        first_damaged = entity.damaged_hint_frame
                        elapsed_damaged = elapsed - first_damaged
                        alpha_mult = max(DAMAGE_ANIM_DURATION - float(elapsed_damaged), 0.0) / DAMAGE_ANIM_DURATION
                        alpha_col = int(alpha_mult * 255.0)

                        # TODO: use mask to render damage highlight.
                        highlight_surface = pg.Surface(sprite.get_size(), pg.SRCALPHA).convert_alpha()
                        highlight_surface.fill((255, 0, 0, alpha_col), special_flags=pg.BLEND_RGBA_ADD)
                        entity_blit.blit(highlight_surface, (0, 0))

                        if alpha_col <= 0:
                            entity.damaged_hint = False
                            entity.damaged_hint_frame = -1

                game_screen.blit(
                    entity_blit, view_grid_to_draw(entity.grid_pos, local_pos)
                )
                if game.controller_entity:
                    distance_x = abs(entity.grid_pos[0] - game.controller_entity.grid_pos[0])
                    distance_y = abs(entity.grid_pos[1] - game.controller_entity.grid_pos[1])
                    if distance_x <= 1 and distance_y <= 1:
                        label = entity.get_label()
                        if label != None:
                            label_text = INFO_FONT.render(label, False, (255, 255, 255)).convert_alpha()
                            label_text_rect = label_text.get_rect(center=view_grid_to_draw(entity.grid_pos, local_pos))
                            game_screen.blit(
                                label_text,
                                label_text_rect
                            )

def render_health_bar(surface, current_health, max_health, position=(85, 10), size=(70, 10)):
    health_ratio = current_health / max_health
    health_bar_width = int(size[0] * health_ratio)

    bar_color = (0, 255, 0)  # gree color for health
    back_color = (100, 100, 100)  # grey background

    # background bar
    back_rect = pg.Rect(position, size)
    pg.draw.rect(surface, back_color, back_rect)

    # health bar
    health_rect = pg.Rect(position, (health_bar_width, size[1]))
    pg.draw.rect(surface, bar_color, health_rect)

    pg.draw.rect(surface, (255, 255, 255), back_rect, 1)  # White border

def render_inventory(surface, player):
    inventory_surface = pg.Surface((200, 100))
    inventory_surface.fill((50, 50, 50))
    inventory_rect = inventory_surface.get_rect()
    
    # border around inventory
    pg.draw.rect(inventory_surface, (255, 255, 255), inventory_rect, 2)

    # Render inventory items
    x_offset = 10
    y_offset = 10
    item_spacing = 40  # space between items

    for item_name, item_info in player.inventory.items():
        item_sprite_idx = item_info['item'].sprite_idx
        item_sprite = tiles.get_sprite(item_sprite_idx)

        # scale up the item 
        item_sprite_large = pg.transform.scale(item_sprite, (30, 30))
        inventory_surface.blit(item_sprite_large, (x_offset, y_offset))

        # draw quantity
        quantity_text = (pg.font.SysFont("Arial", 10)).render(f"x{item_info['quantity']}", True, (0, 0, 0))
        # bottom right corner of the item sprite
        quantity_rect = quantity_text.get_rect(bottomright=(x_offset + 32, y_offset + 32))
        inventory_surface.blit(quantity_text, quantity_rect)

        # next item
        x_offset += item_spacing
        if x_offset + item_spacing > inventory_surface.get_width():
            x_offset = 10
            y_offset += item_spacing

    surface.blit(inventory_surface, (20, 20)) 

def render_text(text, fg_color = (255, 255, 255), bg_color = (0, 0, 0)):
    text_surf = DEFAULT_FONT.render(text, False, fg_color, bg_color)
    return text_surf

# Used for displaying info outside of main game loop
def splash_text(text):
    screen.fill("black")
    screen.blit(render_text(text), (0, 0))
    pg.display.flip()

def recognize_data(recognizer: speech.Recognizer, data: speech.AudioData) -> None | str:
    out = None
    try:
        if SR_MODEL == SrModel.GOOGLE:
            out = recognizer.recognize_google(data)
        elif SR_MODEL == SrModel.WHISPER_API:
            out = recognizer.recognize_whisper_api(data, api_key = WHISPER_API_KEY)
        elif SR_MODEL == SrModel.WHISPER_LOCAL:
            out = recognizer.recognize_whisper(data, model="base.en")
        else:
            raise Exception("SR_MODEL not set to a supported model.")
        print("recognized:", out)
    except Exception as e:
        print("Listener error:", e)
    return out

def on_listener_heard(recognizer: speech.Recognizer, data: speech.AudioData):
    global text_surf
    print("heard audio: ", data)
    vc_command = recognize_data(recognizer, data)
    text = f"Voice: {vc_command}" if vc_command else "Voice: No words recognized."
    text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255), (0, 0, 0))
    if vc_command:
        parse_and_execute_command(vc_command)
    else:
        print("Command not recognized.")
        text_surf = DEFAULT_FONT.render("Command not recognized.", False, (255, 0, 0), (0, 0, 0))

RECOGNIZER = speech.Recognizer()
RECOGNIZER.dynamic_energy_threshold = False
MIC = speech.Microphone()
with MIC as source:
    hint = "Calibrating mic for noise. Please remain quiet."
    print(hint)
    splash_text(hint)
    RECOGNIZER.adjust_for_ambient_noise(source, duration=5.0)
    print("energy_threshold set to: ", RECOGNIZER.energy_threshold)

stop_listener = RECOGNIZER.listen_in_background(MIC, on_listener_heard, 8.0)

def move_until_obstacle_step(action: core.MoveUntilObstacleAction, player):
    target_pos = (player.grid_pos[0] + action.direction[0], player.grid_pos[1] + action.direction[1])
    if target_pos not in game.create_occlusion_set():
        player.grid_pos = target_pos
        game.step()
    else:
        action.is_moving = False  # Stop movement

def move_player_step(action: core.MoveAction, player):
    target_pos = (player.grid_pos[0] + action.delta_pos[0], player.grid_pos[1] + action.delta_pos[1])

    # Check if target position valid
    if target_pos in game.create_occlusion_set():
        print(f"Invalid move: {target_pos} is outside the map or blocked.")
        action.steps_remaining = 0  # Stop the movement
        return

    # Move the player
    player.grid_pos = target_pos
    if action.steps_remaining is not None:
        action.steps_remaining -= 1  # Decrement remaining steps
    game.step()

def process_player_action(action, player):
    current_time = pg.time.get_ticks()  # Get the current time in milliseconds

    if isinstance(action, core.MoveAction):
        if current_time - player.last_move_time >= 400:  # Delay in milliseconds
            if action.steps_remaining is None or action.steps_remaining <= 0:
                print("No remaining steps or invalid action.")
                return
            move_player_step(action, player)
            player.last_move_time = current_time
    elif isinstance(action, core.MoveUntilObstacleAction):
        if current_time - player.last_move_time >= 400:  # Delay in milliseconds
            move_until_obstacle_step(action, player)
            player.last_move_time = current_time
    else:
        action.act(player, game)
        game.step()

elapsed = 0
delta = 0

def main_loop():
    global elapsed
    global delta
    running = True
    while running:
        delta = clock.tick(60)
        elapsed += delta

        player: core.Player | None = None
        if game.controller_entity:
            player = game.controller_entity

        if game.next_level:
            game.next_level = False
            generate(game, 4, (32, 32))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYUP and CONTROLS:
                if event.key == pg.K_DOWN:
                    player_decide_nodelay(core.MoveAction((0, 1)))
                if event.key == pg.K_UP:
                    player_decide_nodelay(core.MoveAction((0, -1)))
                if event.key == pg.K_LEFT:
                    player_decide_nodelay(core.MoveAction((-1, 0)))
                if event.key == pg.K_RIGHT:
                    player_decide_nodelay(core.MoveAction((1, 0)))
                if event.key == pg.K_i:
                    if game.inventory_open:
                        player_decide_nodelay(core.CloseInventoryAction())
                    else:
                        player_decide_nodelay(core.OpenInventoryAction())
                if event.key == pg.K_e:
                    player_decide_nodelay(core.InteractEverything())
                if CHEATS:
                    if event.key == pg.K_0:
                        if player:
                            player.add_to_inventory(items.KeyItem())
                    if event.key == pg.K_1:
                        print(game.create_description())
        
        if game.game_over:
            # display  over screen
            screen.fill("black")
            game_over_text = DEFAULT_FONT.render("Game Over", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(game_over_text, text_rect)
            pg.display.flip()
            continue
            
        player = game.controller_entity
        if player and player.action_queue:
            current_action = player.action_queue[0]
            process_player_action(current_action, player)
            if isinstance(current_action, core.MoveAction):
                if current_action.steps_remaining <= 0:
                    player.action_queue.pop(0)
            elif isinstance(current_action, core.MoveUntilObstacleAction):
                if not current_action.is_moving:
                    player.action_queue.pop(0)
            else:
                player.action_queue.pop(0)
                game.step()

        # Render steps
        game_screen.fill("black")
        render_game(game)
        if player:
            render_health_bar(game_screen, player.health, 100)
            if game.inventory_open:
                render_inventory(game_screen, player)

        screen.fill("black")
        screen.blit(pg.transform.scale(game_screen, screen.get_rect().size), (0, 0))
        screen.blit(text_surf, (0, 0))

        # flip buffer to display
        pg.display.flip()

import traceback
try:
    main_loop()
except Exception as e:
    print(f"Game crashed: {e}")
    traceback.print_exc()
pg.quit()
stop_listener(False)
