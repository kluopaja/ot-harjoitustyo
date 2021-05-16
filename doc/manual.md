
## Installation

The following commands should be run at the project root.

1. Set up Poetry environment:
```poetry install```

2. Initialize the database:
```poetry run invoke init-database```

3. Start game:
```poetry run invoke start```

If the game window is too big or the game runs too slowly,
see Configuration section on how to adjust the game window resolution.

## Running tests
Tests can be run with:
```poetry run invoke test```

Coverage report can be genreated with:
```poetry run invoke coverage-report```

Pylint can be run with;
```poetry run invoke lint```

## Usage

Navigation in the menu is done with arrow keys, esc and enter (by default,
can be configured).


### Add user menu
New users can be added in the `Add user` menu by typing the player
name to the `Name` field and selecting`Create user`. If no users have
been added to the database, the game can still be played with the "default user".
This user will not be saved to the database and will disappear when a
first user is saved to the database.


### New game menu
The game can be configured by navigating to a menu item and selecting
the values with left and right keys.

The players should have different names to make the game results
more interpretable.

The number of supported players depends on the number of player keymaps defined
and on the map support. Currently these support maximum of 4 players.

### Game

By default each game lasts 120 seconds or until the player pressed `Esc` key.

The game can be paused by pressing `p`.

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

They keymaps can be configured by modifying the configuration files. (See Configuration section)
Please note that in single player mode the keymappings for player 1 will
be used.


### Results
The results view will be shown automatically after the game has finished.


### Levels
The levels are defined by default in ```assets/levels/```. Currently the only way
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


## Configuration

The game reads the configs from a file `assets/config.json`. By default the game also uses
configuration files `assets/background.json`, `assets/bullet.json`, `assets/gun.json`,
`assets/keys.json`, `assets/plane.json` and level configs located at `assets/levels`.
These other configuration files are not fixed but can be set at the
configuration files that uses them (for example, `assets/plane.json` has the property
`gun_config_path`).

The paths inside configuration files are always relative paths to directory containing
the configuration file.

The parameters have some limitations. For example, `health` property in a plane configuration
file has to be a positive integer. These limitations are defined using JSON Schema and
can be viewed in `assets/schemas`. In addition, the value of the parameters in key configuration file (default
`assets/keys.json`) should be valid pygame key descriptions (see here https://www.pygame.org/docs/ref/key.html).

The game window resolution can be adjusted by changing `window_width` and `window_height` in
`assets/config.json`.
