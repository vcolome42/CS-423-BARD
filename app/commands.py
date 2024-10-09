from core import MoveAction, WaitAction, TeleportAction, MoveUntilObstacleAction

# keyword commands in different file to add an extensive list
commands = {
    "move left": MoveAction((-1, 0)),
    "move right": MoveAction((1, 0)),
    "move up": MoveAction((0, -1)),
    "move down": MoveAction((0, 1)),
    "open chest": None,  # replace none with open chest function
    "attack": None,  # replace with attack function
    "move left all the way": MoveUntilObstacleAction((-1, 0)),
    "move right all the way": MoveUntilObstacleAction((1, 0)),
    "move up all the way": MoveUntilObstacleAction((0, -1)),
    "move down all the way": MoveUntilObstacleAction((0, 1)),
}
