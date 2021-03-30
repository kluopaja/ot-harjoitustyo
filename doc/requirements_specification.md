# Requirements

## Purpose of the software

The software will be a 2D shoot 'em up flying game loosely similar to
[Sopwith](https://en.wikipedia.org/wiki/Sopwith_(video_game)). The players' goal
is to fly a plane while trying to shoot other players' planes and avoiding to
get shot by others.

## Users

The software will support at least 2 simultaneous players. In the beginning the
game will not have any AI and thus single-player mode will not be very useful.

## Basic functionality

### Main menu

* The players can start the game
* The players can select a map
* The players can select the number of players
* The players can select their usernames
* The players can view the list of the most successful players
* The players can quit the game

### Game

* Each player has their own plane that they pilot
* The players can shoot bullets
* Each of planes will be drawn on a separate subwindow tracking the plane
* The players can see their current score
* The players can pause the game
* Hitting a bullet or ground will damage the plane
* Enough damage will destroy the plane causing the player to lose points
* The destroyed planes will spawn again after a while

### After game

* The players can see their final scores
* Game statistics will be saved to a database

## Further development ideas

### Main menu

* Configuration of the planes

### Game
* Powerups
* Birds which will cause damage if hit by the plane
* Repairing the plane at a base
