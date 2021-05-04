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

### Menu

- [x] The players can start the game
- [x] The players can select a map
- [x] The players can select the number of players
- [x] The players can select their usernames
- [x] The players will be stored into a database
- [ ] The players can view the list of the most successful players
- [x] The players can quit the game

### Game

- [x] Each player has their own plane that they pilot
- [x] The players can shoot bullets
- [x] Each of planes will be drawn on a separate subwindow tracking the plane
- [x] The players can see their current score
- [x] The players can pause the game
- [x] Hitting a bullet or ground will damage the plane
- [x] Enough damage will destroy the plane causing the player to lose points **Tehty**
- [x] The destroyed planes will spawn again after a while

### After game

- [x] The players can see their final scores
- [ ] Game statistics will be saved to a database

## Further development ideas

### Menu

- [ ] Configuration of the planes

### Game
- [ ] Powerups
- [ ] Birds which will cause damage if hit by the plane
- [ ] Repairing the plane at a base
