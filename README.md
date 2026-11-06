# Gridrunner 2099

A small arena shooter built with Python and Pygame, featuring a fixed, tilted camera, tank-style characters, and a shockwave bomb.

## How the project started

I started by making a simple 3D-style shooter. The first version was mostly about getting the basics working: moving around the arena, aiming with the mouse, shooting enemies, and checking collisions. The characters were simple shapes, and the arena used perspective projection to give it depth.

While taking a break from working on it, I thought about the old Tank Hero game. That became the inspiration for the next version. Instead of keeping the player as a basic circle, I redesigned it as a small tank with tracks, a body, and a barrel that turns toward the mouse.

That change gave the project a clearer direction. I started treating it more like a tank arena game, with solid obstacles, clearer enemy silhouettes, and effects that fit the combat rather than adding glow to everything.

## How it developed

The project grew through a few stages:

1. Basic movement, mouse aiming, shooting, and enemy spawning.
2. A fixed, angled camera and raised walls to give the arena a 3D-style appearance.
3. A score-based bomb that clears enemies and creates an expanding shockwave.
4. Generated sound effects and particle bursts.
5. Tank-inspired character designs, a cleaner interface, and more restrained colours.
6. Enemy navigation around obstacles, pause controls, and volume settings.

The main shift was moving from adding features to making those features feel consistent with each other.

## Features

- Fixed, tilted overhead camera.
- Tank-style player with a mouse-directed barrel.
- Angular enemy drones with a different silhouette.
- Raised walls that block movement and bullets.
- Grid-based enemy navigation around obstacles.
- Shooting, health, scoring, and restart controls.
- Shockwave bomb with a score cost and cooldown.
- Procedurally generated sounds.
- Muzzle flashes, impact sparks, debris, and bomb effects.
- Start screen, pause menu, volume controls, and mute.

## Built with

- Python
- Pygame
- Python standard-library modules for maths, navigation, and audio sample generation.

No external images, models, or sound files are required.

## Running the game

Install Pygame:

    python -m pip install --upgrade pygame

Run the script:

    python main.py

## Controls

| Input | Action |
| Enter | Start the game |
| WASD / arrow keys | Move |
| Mouse | Aim |
| Left-click | Shoot |
| Space | Use the bomb |
| P / Esc | Pause or resume |
| − / + | Adjust volume |
| M | Mute |
| R / Enter | Restart after game over |
| Q | Quit |

## Scoring and bombs

Each enemy destroyed by a bullet earns 100 points.

The bomb costs 500 points and has a five-second cooldown. It clears all active enemies immediately and displays an expanding purple shockwave. Enemies destroyed by the bomb do not award additional points.

The displayed score is a spendable balance, so using a bomb reduces it.

## What I worked on

This project brought together several parts of game development:

- Projecting world coordinates onto a fixed camera view.
- Converting mouse positions into aiming directions on the arena floor.
- Handling movement and bullet collisions.
- Routing enemies around walls.
- Generating short sound effects from audio samples.
- Using particles and brief visual feedback without overwhelming the screen.
- Keeping timers consistent when the game is paused.
- Giving the game a more deliberate visual identity.

## Current limitations

This is a 3D-style game, not a full 3D engine. The world is drawn using Pygame shapes and custom perspective projection.

Objects use back-to-front drawing order, so some overlap artifacts are still possible. Enemy navigation is grid-based, and scores are not saved between sessions.

## Next steps

- Add different enemy behaviours.
- Improve depth handling and visual overlap.
- Refine the arena layout.
- Add high-score saving.
- Continue tuning movement, shooting, and difficulty.

## Inspiration
Tank Hero inspired the tank-style character direction during development. This project uses its own code-drawn shapes and generated sounds rather than assets from that game.
