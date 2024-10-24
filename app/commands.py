from core import MoveAction, WaitAction, TeleportAction, MoveUntilObstacleAction, AttackAction, PickUpAction, OpenInventoryAction, CloseInventoryAction, UseItemAction

# keyword commands in different file to add an extensive list
commands = {
    # Move left
    "move left": MoveAction((-1, 0)),
    "go left": MoveAction((-1, 0)),
    "step left": MoveAction((-1, 0)),
    "walk left": MoveAction((-1, 0)),
    "turn left": MoveAction((-1, 0)),

    # Move right
    "move right": MoveAction((1, 0)),
    "go right": MoveAction((1, 0)),
    "step right": MoveAction((1, 0)),
    "walk right": MoveAction((1, 0)),
    "turn right": MoveAction((1, 0)),

    # Move up
    "move up": MoveAction((0, -1)),
    "go up": MoveAction((0, -1)),
    "step up": MoveAction((0, -1)),
    "walk up": MoveAction((0, -1)),
    "climb up": MoveAction((0, -1)),

    # Move down
    "move down": MoveAction((0, 1)),
    "go down": MoveAction((0, 1)),
    "step down": MoveAction((0, 1)),
    "walk down": MoveAction((0, 1)),

    # Open chest
    "open chest": None,
    "unlock chest": None,
    "open the chest": None,
    "unlock the chest": None,
    "open treasure": None,
    "open the treasure": None,
    "unlock treasure": None,  
    "unlock the treasure": None,

    # Attack
    "attack": AttackAction(),
    "strike": AttackAction(),
    "hit": AttackAction(),
    "fight": AttackAction(),
    "punch": AttackAction(),
    "stab": AttackAction(),

    # Move left all the way
    "move left all the way": MoveUntilObstacleAction((-1, 0)),
    "go left all the way": MoveUntilObstacleAction((-1, 0)),
    "step left all the way": MoveUntilObstacleAction((-1, 0)),
    "walk left all the way": MoveUntilObstacleAction((-1, 0)),
    "head left all the way": MoveUntilObstacleAction((-1, 0)),

    # Move right all the way
    "move right all the way": MoveUntilObstacleAction((1, 0)),
    "go right all the way": MoveUntilObstacleAction((1, 0)),
    "step right all the way": MoveUntilObstacleAction((1, 0)),
    "walk right all the way": MoveUntilObstacleAction((1, 0)),
    "head right all the way": MoveUntilObstacleAction((1, 0)),

    # Move up all the way
    "move up all the way": MoveUntilObstacleAction((0, -1)),
    "go up all the way": MoveUntilObstacleAction((0, -1)),
    "step up all the way": MoveUntilObstacleAction((0, -1)),
    "walk up all the way": MoveUntilObstacleAction((0, -1)),
    "head up all the way": MoveUntilObstacleAction((0, -1)),
    "climb up all the way": MoveUntilObstacleAction((0, -1)),

    # Move down all the way
    "move down all the way": MoveUntilObstacleAction((0, 1)),
    "go down all the way": MoveUntilObstacleAction((0, 1)),
    "step down all the way": MoveUntilObstacleAction((0, 1)),
    "walk down all the way": MoveUntilObstacleAction((0, 1)),
    "head down all the way": MoveUntilObstacleAction((0, 1)),

    # Picking up items
    "pick up": PickUpAction(),
    "take": PickUpAction(),
    "grab": PickUpAction(),
    "collect": PickUpAction(),

    # Open inventory
    "open inventory": OpenInventoryAction(),
    "show inventory": OpenInventoryAction(),
    "inventory": OpenInventoryAction(),

    # Close inventory
    "close inventory": CloseInventoryAction(),
    "hide inventory": CloseInventoryAction(),

    # Use health potion
    "use potion": UseItemAction("Health Potion"),
    "use health potion": UseItemAction("Health Potion"),
    "drink health potion": UseItemAction("Health Potion"),
    "eat health potion": UseItemAction("Health Potion"),
}

