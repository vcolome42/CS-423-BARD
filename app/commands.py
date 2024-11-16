action_keywords = {
    "move": "move",
    "go": "move",
    "walk": "move",
    "step": "move",
    "run": "move",
    "attack": "attack",
    "strike": "attack",
    "hit": "attack",
    "fight": "attack",
    "defeat": "attack",
    "pick up": "pickup",
    "take": "pickup",
    "grab": "pickup",
    "collect": "pickup",
    "use": "use",
    "drink": "use",
    "eat": "use",
    "open": "interact",
    "interact": "interact",
    "close": "close",
}

direction_keywords = {
    "left": (-1, 0),
    "right": (1, 0),
    "up": (0, -1),
    "down": (0, 1),
    "to the left": (-1, 0),
    "to the right": (1, 0),
    "to the top": (0, -1),
    "to the bottom": (0, 1),
    "west": (-1, 0),
    "east": (1, 0),
    "north": (0, -1),
    "south": (0, 1),
    # "forward": (0, -1),  # these are relative/subjective to player
    # "backward": (0, 1),
}

item_keywords = {
    "potion": "Health Potion",
    "health potion": "Health Potion",
}

connectors = ["and", "then", "after that", "next", ".", ","]

number_words = {
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

patterns = {
    "move": r"(move|go|walk|run|step)\s+(?P<direction>\w+)(\s+(?P<steps>\d+|\w+))?",
    "move_until_obstacle": r"(move|go|walk|run|step)\s+(?P<direction>\w+)\s+(until|till|to)\s+(?P<condition>\w+)",
    "attack": r"(attack|strike|hit|fight)",
    "pickup": r"(pick up|take|grab|collect)",
    "use": r"(use|drink|eat)\s+(?P<item>[\w\s]+)",
    "interact": r"(open|interact)",
    "close": r"(close|hide)\s+inventory",
    "open": r"(open|show)\s+inventory",
}