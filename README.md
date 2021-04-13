Repository for the University of Helsinki couse *Ohjelmistotekniikka*.

# Unnamed Plane Game

A 2D shoot 'em up flying game inspired by Sopwith.

## Documentation
* [Requirements specification](https://github.com/kluopaja/ot-harjoitustyo/blob/master/doc/requirements_specificiation.md)


## Installation

1. Set up Poetry environment:
```poetry install```

2. Start game:
```poetry run invoke start```

## Running tests
Tests can be run with:
```poetry run invoke test```

Coverage report can be genreated with:
```poetry run invoke coverage-report```

## Usage

Navigation in the menu is done with arrow keys, esc and enter.

Currently the game only supports 1 and 2 player modes. The player's score is
shown in the top left corner of the game view.

Keys for player 1:

```
shoot: left shift
accelerate: w
turn down: d
turn up: a

```
Keys for player 2:

```
shoot: space
accelerate: up
turn down: right
turn up: left


It is not yet possible to configure the keys.
Please note that in single player mode the keymappings for player 1 will
be used.


### Tips for flying

Wings don't work well if the plane doesn't move fast enough.

Turning the plane too fast results in losing the velocity and not getting much
lift. In other words:

The angle of attack (angle between the wing and relative air movement) determines
(alongside with the velocity) the amount of lift and drag.

From 0 the lift increases rapidly to its maximum at 20 degrees. After this, the
lift immediately decreases to about 60 % of its maximum and starts to increase again.

The drag increases monotonously from 0 to 90 degrees.
