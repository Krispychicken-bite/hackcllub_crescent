# Gridrunner 2099: Arena Overload

A neon arcade survival shooter built with Python and Pygame. Fight enemies from a fixed, tilted overhead camera, earn points, and unleash a screen-clearing shockwave bomb.

## Features

- Fixed elevated camera with perspective projection.
- Neon arena grid and raised 3D-style walls.
- Keyboard movement and mouse-directed shooting.
- Enemy spawning and simple chase behaviour.
- Health bar, score display, and bomb cooldown indicator.
- Shockwave bomb that instantly clears active enemies.
- Procedurally generated sound effects: no external audio files required.
- Particle bursts for shooting, enemy destruction, wall impacts, damage, and bombs.
- Restart after game over.

The sound and particle features require the sound-and-particle additions to be included in `main.py`.

## Requirements

- Python 3
- Pygame
- A graphical desktop environment
- Speakers or headphones for optional audio

## Installation

Open a terminal in the project directory and install Pygame:

```bash
python -m pip install pygame
```

Run the game:

```bash
python main.py
```

If your system uses `python3` instead of `python`, use that command for both steps.

## Project Structure

```text
project/
├── main.py       # Game code, rendering, sound generation, and effects
└── README.md     # Project documentation
```

No external images, models, or audio assets are required by the current implementation.

## Controls

| Input | Action |
| --- | --- |
| W / Up arrow | Move toward the far end of the arena |
| S / Down arrow | Move toward the near end of the arena |
| A / Left arrow | Move left |
| D / Right arrow | Move right |
| Left mouse click | Fire toward the cursor's position on the arena floor |
| Space | Activate the shockwave bomb when available |
| R | Restart after game over |
| Esc | Exit |

Shooting is click-to-fire rather than automatic while holding the mouse button.

## Gameplay

### Score

Each enemy destroyed by a bullet awards **100 points**. Your displayed score is a spendable balance: activating a bomb subtracts points from it.

### Shockwave Bomb

- Costs **500 points** per activation.
- Requires a **5-second cooldown** between activations.
- Immediately removes all currently active enemies.
- Creates an expanding purple ring and, with effects installed, particle bursts and a deep blast sound.
- Does not award points for enemies cleared by the bomb.

The expanding ring is visual: enemies are cleared immediately rather than when the ring reaches them. The first bomb has no initial cooldown, but you still need enough points to use it.

### Health

The player starts with **100 health**. Enemy contact deals **10 damage**, with a **500 ms interval** between damage applications. At zero health, the game ends. Press **R** to reset the run, including the score and bomb cooldown.

### Walls and Enemies

Walls block player movement, enemy movement, and bullets. Enemies spawn approximately every **1.4 seconds**, move toward the player, and slide along walls where possible.

## Sound and Particle Effects

Sounds are generated in memory when the game starts. There are no audio files to download or manage.

| Event | Sound | Particles |
| --- | --- | --- |
| Shooting | Descending laser pulse | Cyan muzzle sparks |
| Enemy destruction | Short explosion | Red burst |
| Wall impact | None | Cyan sparks |
| Player damage | Electronic hit | Green burst |
| Bomb activation | Low descending blast | Purple burst and enemy bursts |

The audio system is designed to let the game continue if audio initialization fails. Start with a low speaker volume when testing.

## Customization

Edit the constants near the top of `main.py` to adjust gameplay:

```python
BOMB_COST = 500
BOMB_COOLDOWN_MS = 5000
SPAWN_INTERVAL_MS = 1400
WALL_HEIGHT = 42
```

Camera settings control the fixed arena view:

```python
CAMERA_X = ARENA_WIDTH / 2
CAMERA_Y = 1000
CAMERA_HEIGHT = 800
CAMERA_TARGET_Y = 280
FOCAL_LENGTH = 780
```

The camera pitch is calculated automatically from its position and target. You can also edit `WALLS` to change the arena layout, and the entity classes to adjust movement speed or health.

## Implementation Notes and Limitations

- Uses custom perspective projection and Pygame drawing, not a full 3D engine.
- Characters are rendered as sphere-style shapes, not animated 3D models.
- Walls and entities use simple back-to-front drawing order; complex overlap can produce visual artifacts.
- Particles are drawn as an overlay and are not hidden by walls.
- Enemies use direct chasing and collision sliding, not navigation or pathfinding, so they can get stuck behind obstacles.
- The window size is fixed in the current implementation.
- Scores and settings are not saved between sessions.

## Possible Future Improvements

- having the project encapsulated as a program using electron flask
- Progressive enemy waves and additional enemy types.
- Enemy pathfinding around walls.
- High-score saving and a pause menu.
- Weapon upgrades, pickups, and automatic fire.
- Sound volume controls and a mute option.
- Improved depth handling for effects and objects.
