from typing import Tuple

import pygame as pg
import speech_recognition as speech

import sprites
import items
import core
import re

from dungeon import generate
from commands import commands
# from dotenv import dotenv_values
# SECRETS = dotenv_values(".env.secret")

LIST_MICS = False
MIC_INDEX = None
# None = default device

class SrModel:
    GOOGLE = 1  # Not suitable for punctuation and sentences.
    WHISPER_LOCAL = 2
    # WHISPER_API = 3
SR_MODEL = SrModel.WHISPER_LOCAL

# WHISPER_API_KEY = None
# if "API_KEY" in SECRETS:
#     WHISPER_API_KEY = SECRETS["API_KEY"]
#     print("Whisper API Key found:", WHISPER_API_KEY)
#     if SR_MODEL != SrModel.WHISPER_API:
#         print("[WARN] Whisper API key found but not using SrModel.WHISPER_API")

CONTROLS = True
CHEATS = True

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
connectors = ["and", "then", "after that", "next", ".", ","]


def split_command(command):
    for connector in connectors:
        command = command.replace(connector, "|")
    return command.split("|")


# https://www.geeksforgeeks.org/a-search-algorithm/
def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(pos: Tuple[int, int], game: core.Game) -> list[Tuple[int, int]]:
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        next_pos = (pos[0] + dx, pos[1] + dy)
        if next_pos in game.ground and next_pos not in game.create_occlusion_set():
            neighbors.append(next_pos)
    return neighbors


# Uses A* pathfinding algorithm
def calculate_path(
    start_pos: Tuple[int, int], end_pos: Tuple[int, int]
) -> list[Tuple[int, int]]:
    frontier = [(0, start_pos)]
    came_from = {start_pos: None}
    cost_so_far = {start_pos: 0}

    while frontier:
        frontier.sort(reverse=True)
        current = frontier.pop()[1]

        if current == end_pos:
            break

        for next_pos in get_neighbors(current, game):
            new_cost = cost_so_far[current] + 1

            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + manhattan_distance(next_pos, end_pos)
                frontier.append((priority, next_pos))
                came_from[next_pos] = current

    if end_pos not in came_from:
        return []

    path = []
    current = end_pos
    while current != start_pos:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return path


# parse and execute different commands
def parse_and_execute_command(command: str):
    command = command.lower()
    global text_surf

    # Split command into parts
    parts = split_command(command)

    print(parts)
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Split part into words
        words = part.split()
        i = 0
        while i < len(words):
            current_phrase = " ".join(words[i:])
            commandFound = False

            # Check for non coordinate commands first
            for commandKey in commands:
                if commandKey in current_phrase:
                    action = commands[commandKey]
                    if action is not None:
                        player_decide(action)
                    commandFound = True
                    # Move past the command words
                    i += len(commandKey.split())
                    break

            if commandFound:
                continue

            # If no command found, check for coordinate
            coord_pattern = re.match(r"^([a-z])[\s-]?(\d+)$", words[i])
            if coord_pattern:
                # Handle coordinate movement
                coord = coord_pattern.group(1) + coord_pattern.group(2)
                target_pos = parse_chess_notation(coord)

                if target_pos is None:
                    print("Invalid coordinate.")
                    text_surf = DEFAULT_FONT.render(
                        "Invalid coordinate.", False, (255, 0, 0), (0, 0, 0)
                    )
                    i += 1
                    continue

                # Check if position is valid
                if (
                    target_pos not in game.ground
                    or target_pos in game.create_occlusion_set()
                ):
                    print("Cannot move to that position.")
                    text_surf = DEFAULT_FONT.render(
                        "Cannot move to that position.", False, (255, 0, 0), (0, 0, 0)
                    )
                    i += 1
                    continue

                # Move to coordinate
                if game.controller_entity:
                    current_pos = game.controller_entity.grid_pos
                    path = calculate_path(current_pos, target_pos)

                    if not path:
                        print("No valid path to that position.")
                        text_surf = DEFAULT_FONT.render(
                            "No valid path to that position.",
                            False,
                            (255, 0, 0),
                            (0, 0, 0),
                        )
                        i += 1
                        continue

                    # Execute movement
                    for step in path:
                        delta_x = step[0] - current_pos[0]
                        delta_y = step[1] - current_pos[1]
                        action = core.MoveAction((delta_x, delta_y))
                        if action.is_valid(game.controller_entity, game):
                            player_decide(action)
                            pg.time.wait(600)  # 0.6 second delay
                            current_pos = step
                        else:
                            break
                i += 1
                continue

            # If neither command or coordinate found, move to next word
            i += 1

        if i == 0:
            print("Command not recognized.")
            text_surf = DEFAULT_FONT.render(
                "Command not recognized.", False, (255, 0, 0), (0, 0, 0)
            )


def player_decide(action: core.EntityAction):
    global text_surf
    player = game.controller_entity
    if action.is_valid(player, game):
        action.act(player, game)
        game.step()
    else:
        if isinstance(action, core.PickUpAction):
            text_surf = DEFAULT_FONT.render(
                "No items nearby to pick up.", False, (255, 0, 0), (0, 0, 0)
            )
        elif isinstance(action, core.InteractEverything):
            text_surf = DEFAULT_FONT.render(
                "No interactables.", False, (255, 0, 0), (0, 0, 0)
            )
        else:
            text_surf = DEFAULT_FONT.render(
                "Action is not valid.", False, (255, 0, 0), (0, 0, 0)
            )


def grid_to_draw(gridpos: Tuple[int, int]) -> Tuple[int, int]:
    return (gridpos[0] * 16, gridpos[1] * 16)


def view_grid_to_draw(
    gridpos: Tuple[int, int], view_pos: Tuple[int, int]
) -> Tuple[int, int]:
    x = (gridpos[0] - view_pos[0]) * 16
    y = (gridpos[1] - view_pos[1]) * 16
    x += SCREEN_SIZE[0] / 2
    y += SCREEN_SIZE[1] / 2
    return (x, y)


# Constants
COORDINATE_COLOR = (180, 180, 180)  # Light gray
COORDINATE_OPACITY = 160  # Slightly transparent
COORDINATE_OFFSET = 2  # Pixels from the edge of tiles


def render_chess_coordinates(surface: pg.Surface, view_pos: Tuple[int, int]):
    # visible range based on screen size
    visible_width = SCREEN_SIZE[0] // 16
    visible_height = SCREEN_SIZE[1] // 16

    start_x = max(0, view_pos[0] - visible_width // 2)
    start_y = max(0, view_pos[1] - visible_height // 2)

    coord_surface = pg.Surface(surface.get_size(), pg.SRCALPHA)
    # non-walkable positions
    occlusion_set = game.create_occlusion_set()

    # Render coordinates for each tile
    for y in range(visible_height):
        for x in range(visible_width):
            grid_x = start_x + x
            grid_y = start_y + y
            current_pos = (grid_x, grid_y)

            # Skip if tile is:
            # - not in ground set
            # - in occlusion set
            # - player's current position
            if (
                current_pos not in game.ground
                or current_pos in occlusion_set
                or current_pos == view_pos
            ):
                continue

            # chess notation
            coord_text = f"{chr(ord('a') + grid_x)}{grid_y + 1}"
            text = INFO_FONT.render(coord_text, False, COORDINATE_COLOR)
            text.set_alpha(COORDINATE_OPACITY)

            # Get tile position
            pos = view_grid_to_draw(current_pos, view_pos)

            # Position text at bottom right tile
            text_rect = text.get_rect()
            text_pos = (
                pos[0] + 16 - text_rect.width - COORDINATE_OFFSET,
                pos[1] + 16 - text_rect.height - COORDINATE_OFFSET,
            )

            coord_surface.blit(text, text_pos)
    surface.blit(coord_surface, (0, 0))


# grid to chess notation
def get_chess_notation(pos: Tuple[int, int]) -> str:
    col = chr(ord("a") + pos[0])
    row = pos[1] + 1  # Chess notation starts at 1
    return f"{col}{row}"


def parse_chess_notation(notation: str) -> Tuple[int, int] | None:
    if len(notation) < 2:
        return None

    col = notation[0].lower()
    if not col.isalpha() or not notation[1:].isdigit():
        return None

    x = ord(col) - ord("a")
    y = int(notation[1:]) - 1  # Convert to 0-based index

    return (x, y)


DAMAGE_ANIM_DURATION = 600.0  # milliseconds


# render_suggestions = list[tuple[str, str]]
def render_game(game: core.Game):
    # global render_suggestions
    render_suggestions = []
    local_pos = (0, 0)
    if game.controller_entity:
        local_pos = game.controller_entity.grid_pos
    for ground_gridpos in game.ground:
        game_screen.blit(
            tiles.get_sprite(1), view_grid_to_draw(ground_gridpos, local_pos)
        )
    for wall_gridpos in game.walls:
        game_screen.blit(
            tiles.get_sprite(0), view_grid_to_draw(wall_gridpos, local_pos)
        )
    for entity in game.entities:
        if not entity.destroyed:  # Check if the entity is not destroyed
            if entity.sprite_idx != -1:
                sprite = tiles.get_sprite(entity.sprite_idx)
                # sprite_mask = tiles.get_mask(entity.sprite_idx)

                entity_blit = pg.Surface(sprite.get_size(), pg.SRCALPHA).convert_alpha()
                entity_blit.blit(sprite, (0, 0))

                if isinstance(entity, core.Character):
                    if entity.damaged_hint_check:
                        entity.damaged_hint_check = False
                        entity.damaged_hint_frame = elapsed
                        entity.damaged_hint = True
                    if entity.damaged_hint:
                        first_damaged = entity.damaged_hint_frame
                        elapsed_damaged = elapsed - first_damaged
                        alpha_mult = (
                            max(DAMAGE_ANIM_DURATION - float(elapsed_damaged), 0.0)
                            / DAMAGE_ANIM_DURATION
                        )
                        alpha_col = int(alpha_mult * 255.0)

                        # TODO: use mask to render damage highlight.
                        highlight_surface = pg.Surface(
                            sprite.get_size(), pg.SRCALPHA
                        ).convert_alpha()
                        highlight_surface.fill(
                            (255, 0, 0, alpha_col), special_flags=pg.BLEND_RGBA_ADD
                        )
                        entity_blit.blit(highlight_surface, (0, 0))

                        if alpha_col <= 0:
                            entity.damaged_hint = False
                            entity.damaged_hint_frame = -1

                game_screen.blit(
                    entity_blit, view_grid_to_draw(entity.grid_pos, local_pos)
                )
                if game.controller_entity:
                    distance_x = abs(
                        entity.grid_pos[0] - game.controller_entity.grid_pos[0]
                    )
                    distance_y = abs(
                        entity.grid_pos[1] - game.controller_entity.grid_pos[1]
                    )
                    if distance_x <= 1 and distance_y <= 1:
                        label = entity.get_label()
                        if label is not None:
                            label_text = INFO_FONT.render(
                                label, False, (255, 255, 255)
                            ).convert_alpha()
                            label_text_rect = label_text.get_rect(
                                center=view_grid_to_draw(entity.grid_pos, local_pos)
                            )
                            game_screen.blit(label_text, label_text_rect)
                        suggestions = entity.get_suggestions()
                        if suggestions is not None:
                            for suggestion in suggestions:
                                render_suggestions.append((label, suggestion))
    suggest_txt_list = ""
    for suggestion in render_suggestions:
        entity_label = suggestion[0]
        suggestion = suggestion[1]
        suggest_txt = suggestion
        if entity_label is not None:
            suggest_txt += f" ({entity_label})"
        suggest_txt_list += suggest_txt + "\n"
    if suggest_txt_list:
        suggest_txt_list_disp = INFO_FONT.render(
            suggest_txt_list, False, (255, 255, 255)
        ).convert_alpha()
        rect = suggest_txt_list_disp.get_rect(
            bottomright=(SCREEN_SIZE[0], SCREEN_SIZE[1])
        )
        game_screen.blit(suggest_txt_list_disp, rect)

    if game.controller_entity:
        render_chess_coordinates(game_screen, game.controller_entity.grid_pos)


def render_health_bar(
    surface, current_health, max_health, position=(85, 10), size=(70, 10)
):
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
        item_sprite_idx = item_info["item"].sprite_idx
        item_sprite = tiles.get_sprite(item_sprite_idx)

        item_sprite_large = pg.transform.scale(item_sprite, (30, 30))
        inventory_surface.blit(item_sprite_large, (x_offset, y_offset))

        # draw quantity
        quantity_text = (pg.font.SysFont("Arial", 10)).render(
            f"x{item_info['quantity']}", True, (0, 0, 0)
        )
        # bottom right corner of the item sprite
        quantity_rect = quantity_text.get_rect(
            bottomright=(x_offset + 32, y_offset + 32)
        )
        inventory_surface.blit(quantity_text, quantity_rect)

        # next item
        x_offset += item_spacing
        if x_offset + item_spacing > inventory_surface.get_width():
            x_offset = 10
            y_offset += item_spacing

    surface.blit(inventory_surface, (20, 20))


def render_text(text, fg_color=(255, 255, 255), bg_color=(0, 0, 0)):
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
        # elif SR_MODEL == SrModel.WHISPER_API:
            # out = recognizer.recognize_whisper_api(data, api_key=WHISPER_API_KEY)
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
    print("Heard a phrase, listening. ", data)
    vc_command = recognize_data(recognizer, data)
    text = f"Voice: {vc_command}" if vc_command else "Voice: No words recognized."
    text_surf = DEFAULT_FONT.render(text, False, (255, 255, 255), (0, 0, 0))
    if vc_command:
        parse_and_execute_command(vc_command)
    else:
        print("Command not recognized.")
        text_surf = DEFAULT_FONT.render(
            "Command not recognized.", False, (255, 0, 0), (0, 0, 0)
        )

# Print microphones as list
if LIST_MICS:
    for i, microphone_name in enumerate(speech.Microphone.list_microphone_names()):
        print(i, microphone_name)

microphones = dict(enumerate(speech.Microphone.list_microphone_names()))
print(f"Using default microphone {microphones[0]}. \nIf this is incorrect, please assign a microphone using LIST_MICS = TRUE and set MIC_INDEX to the microphone.")

RECOGNIZER = speech.Recognizer()
RECOGNIZER.dynamic_energy_threshold = False
MIC = speech.Microphone(device_index=MIC_INDEX)

with MIC as source:
    hint = "Calibrating mic for noise. Please remain quiet."
    print(hint)
    splash_text(hint)
    RECOGNIZER.adjust_for_ambient_noise(source, 5.0)
    print("energy_threshold set to: ", RECOGNIZER.energy_threshold)

stop_listener = RECOGNIZER.listen_in_background(MIC, on_listener_heard, 8.0)


def move_until_obstacle_step(action: core.MoveUntilObstacleAction, player):
    target_pos = (
        player.grid_pos[0] + action.direction[0],
        player.grid_pos[1] + action.direction[1],
    )
    if target_pos not in game.create_occlusion_set():
        player.grid_pos = target_pos
        game.step()
    else:
        action.is_moving = False  # Stop movement


def move_player_step(action: core.MoveAction, player):
    target_pos = (
        player.grid_pos[0] + action.delta_pos[0],
        player.grid_pos[1] + action.delta_pos[1],
    )

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
                    player_decide(core.MoveAction((0, 1)))
                if event.key == pg.K_UP:
                    player_decide(core.MoveAction((0, -1)))
                if event.key == pg.K_LEFT:
                    player_decide(core.MoveAction((-1, 0)))
                if event.key == pg.K_RIGHT:
                    player_decide(core.MoveAction((1, 0)))
                if event.key == pg.K_i:
                    if game.inventory_open:
                        player_decide(core.CloseInventoryAction())
                    else:
                        player_decide(core.OpenInventoryAction())
                if event.key == pg.K_e:
                    player_decide(core.InteractEverything())
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
            text_rect = game_over_text.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2)
            )
            screen.blit(game_over_text, text_rect)
            pg.display.flip()
            continue

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
