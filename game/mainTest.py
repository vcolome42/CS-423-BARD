from gameState import GameState
from player import Player
from room import Room

# GameState, Player, and Room
game_state = GameState()
player = Player(name="Hero", health=100, attack=10, defense=5)
room = Room()

# add the player and room to the game state
game_state.add_player(player)
game_state.add_room(room)

# add a trap to the room
trap = "Spiked Pit"
room.add_trap(trap)

# trigger trap
player.trigger_trap(room, trap)

# check playe health
print(f"{player.name}'s health: {player.health}")
