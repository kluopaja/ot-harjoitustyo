
## Installation

The following commands should be run at the project root.

1. Set up Poetry environment:
```poetry install```

2. Initialize the database:
```poetry run invoke init-database```

3. Start game:
```poetry run invoke start```

## Running tests
Tests can be run with:
```poetry run invoke test```

Coverage report can be genreated with:
```poetry run invoke coverage-report```

Pylint can be run with;
```poetry run invoke lint```

## Usage

Navigation in the menu is done with arrow keys, esc and enter.


### Add user menu
New users can be added in the `Add user` menu by typing the player
name to the `Name` field and selecting`Create user`.


### New game menu
The game can be configured by navigating to a menu item and selecting
the values with left and right keys.

The players should have different names to make the game results
more interpretable.

The number of supported players depends on the number of player keymaps defined
and on the map support. Currently these support 4 players.

### Game

The timer to end the game hasn't been implemented yet so the players
have to press `Esc` to finish the game.

The player's score is shown in the top left corner of the game view.

Keys for player 1:

```
accelerate: w
turn up: a
turn down: d
shoot: q

```
Keys for player 2:

```
accelerate: up
turn up: left
turn down: right
shoot: right shift

```
Keys for player 3:

```
accelerate: t
turn up: f
turn down: h
shoot: r

```
Keys for player 4:

```
accelerate: i
turn up: j
turn down: l
shoot: u
```

They keymaps can be configured by modifying the `assets/keys.json` file.
Please note that in single player mode the keymappings for player 1 will
be used.


The game can be further configured by modifying the following files:

```assets/plane.json```

```assets/bullet.json```

```assets/gun.json```


### Results
The results view will be shown automatically after the game has finished.


### Levels
The levels are defined in ```assets/levels/```. Currently the only way
to edit the levels or to create new levels is to manually edit the level files.


### Tips for flying

Wings don't work well if the plane doesn't move fast enough.

Turning the plane too fast results in losing the velocity and not getting much
lift. In other words:

The angle of attack (angle between the wing and relative air movement) determines
(alongside with the velocity) the amount of lift and drag.

From 0 the lift increases rapidly to its maximum at 20 degrees. After this, the
lift immediately decreases to about 60 % of its maximum and starts to increase again.

The drag increases monotonously from 0 to 90 degrees.
