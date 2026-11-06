import math
import random

import pygame
from array import array

pygame.init()

# --------------------------------------------------
# WINDOW AND DISPLAY
# --------------------------------------------------

WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gridrunner 2099: Arena Overload")
clock = pygame.time.Clock()

HUD_FONT = pygame.font.SysFont("consolas", 18, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 15)
TITLE_FONT = pygame.font.SysFont("consolas", 38, bold=True)

BLACK = (8, 10, 18)
FLOOR_COLOR = (13, 20, 32)
GRID_COLOR = (27, 44, 62)
CYAN = (0, 220, 255)
GREEN = (70, 255, 100)
RED = (255, 65, 90)
PURPLE = (175, 80, 255)
WHITE = (235, 245, 255)
GRAY = (80, 90, 110)

# --------------------------------------------------
# WORLD AND FIXED CAMERA
# --------------------------------------------------

ARENA_WIDTH = 800
ARENA_DEPTH = 600

CAMERA_X = ARENA_WIDTH / 2
CAMERA_Y = 1000
CAMERA_HEIGHT = 800
CAMERA_TARGET_Y = 280

FOCAL_LENGTH = 780
SCREEN_CENTER_X = WIDTH / 2
SCREEN_CENTER_Y = HEIGHT / 2 - 5

CAMERA_PITCH = math.atan2(
    CAMERA_HEIGHT,
    CAMERA_Y - CAMERA_TARGET_Y,
)

CAMERA_SIN = math.sin(CAMERA_PITCH)
CAMERA_COS = math.cos(CAMERA_PITCH)

NEAR_CLIP = 20

BOMB_COST = 500
BOMB_COOLDOWN_MS = 5000
SPAWN_INTERVAL_MS = 1400

WALLS = [
    pygame.Rect(160, 135, 160, 32),
    pygame.Rect(480, 135, 160, 32),
    pygame.Rect(375, 245, 50, 100),
    pygame.Rect(140, 425, 180, 32),
    pygame.Rect(480, 425, 180, 32),
]

WALL_HEIGHT = 42


def camera_depth(x, y, z=0):
    relative_y = y - CAMERA_Y
    relative_z = z - CAMERA_HEIGHT

    return (
        -relative_y * CAMERA_COS
        - relative_z * CAMERA_SIN
    )


def project_3d(x, y, z=0):
    relative_x = x - CAMERA_X
    relative_y = y - CAMERA_Y
    relative_z = z - CAMERA_HEIGHT

    depth = max(NEAR_CLIP, camera_depth(x, y, z))
    scale = FOCAL_LENGTH / depth

    camera_up = (
        -relative_y * CAMERA_SIN
        + relative_z * CAMERA_COS
    )

    sx = SCREEN_CENTER_X + relative_x * scale
    sy = SCREEN_CENTER_Y - camera_up * scale

    return round(sx), round(sy), scale


def project_point(x, y, z=0):
    sx, sy, _ = project_3d(x, y, z)
    return sx, sy


def screen_to_world(sx, sy):
    """Find where the mouse ray intersects the ground."""
    horizontal = (sx - SCREEN_CENTER_X) / FOCAL_LENGTH
    vertical = (SCREEN_CENTER_Y - sy) / FOCAL_LENGTH

    ray_y = -CAMERA_COS - vertical * CAMERA_SIN
    ray_z = -CAMERA_SIN + vertical * CAMERA_COS

    if ray_z >= -0.0001:
        return pygame.Vector2(CAMERA_X, 0)

    distance = -CAMERA_HEIGHT / ray_z

    return pygame.Vector2(
        CAMERA_X + horizontal * distance,
        CAMERA_Y + ray_y * distance,
    )


def body_rect(pos, radius):
    return pygame.Rect(
        round(pos.x - radius),
        round(pos.y - radius),
        radius * 2,
        radius * 2,
    )


def move_with_collisions(pos, velocity, radius):
    # Resolve each axis separately so entities can slide along walls.
    pos.x += velocity.x

    if any(body_rect(pos, radius).colliderect(wall) for wall in WALLS):
        pos.x -= velocity.x

    pos.y += velocity.y

    if any(body_rect(pos, radius).colliderect(wall) for wall in WALLS):
        pos.y -= velocity.y

    pos.x = max(radius, min(ARENA_WIDTH - radius, pos.x))
    pos.y = max(radius, min(ARENA_DEPTH - radius, pos.y))


# --------------------------------------------------
# ENTITIES
# --------------------------------------------------

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = pygame.Vector2(400, 525)
        self.radius = 15
        self.speed = 250
        self.health = 100
        self.max_health = 100
        self.last_damage_time = -500

    def update(self, keys, dt):
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN])
            - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )

        if direction.length_squared():
            direction = direction.normalize()

        move_with_collisions(
            self.pos,
            direction * self.speed * dt,
            self.radius,
        )

    def draw(self, surface):
        ground_x, ground_y, scale = project_3d(
            self.pos.x, self.pos.y
        )

        sx, sy, _ = project_3d(
            self.pos.x, self.pos.y, self.radius
        )

        radius = max(4, round(self.radius * scale))

        pygame.draw.ellipse(
            surface,
            (4, 9, 12),
            (
                ground_x - radius,
                ground_y - radius // 2,
                radius * 2,
                max(3, radius),
            ),
        )

        pygame.draw.circle(surface, GREEN, (sx, sy), radius)
        pygame.draw.circle(surface, WHITE, (sx, sy), radius, 2)

        target = screen_to_world(*pygame.mouse.get_pos())
        aim = target - self.pos

        if aim.length_squared():
            tip = self.pos + aim.normalize() * 29
            tip_screen = project_point(tip.x, tip.y, self.radius)

            pygame.draw.line(
                surface,
                WHITE,
                (sx, sy),
                tip_screen,
                3,
            )


class Enemy:
    def __init__(self):
        edge = random.choice(("top", "bottom", "left", "right"))

        if edge == "top":
            self.pos = pygame.Vector2(
                random.randint(25, ARENA_WIDTH - 25), 20
            )
        elif edge == "bottom":
            self.pos = pygame.Vector2(
                random.randint(25, ARENA_WIDTH - 25),
                ARENA_DEPTH - 20,
            )
        elif edge == "left":
            self.pos = pygame.Vector2(
                20, random.randint(25, ARENA_DEPTH - 25)
            )
        else:
            self.pos = pygame.Vector2(
                ARENA_WIDTH - 20,
                random.randint(25, ARENA_DEPTH - 25),
            )

        self.radius = 13
        self.speed = random.uniform(65, 105)

    def update(self, player_pos, dt):
        direction = player_pos - self.pos

        if direction.length_squared():
            move_with_collisions(
                self.pos,
                direction.normalize() * self.speed * dt,
                self.radius,
            )

    def draw(self, surface):
        gx, gy, scale = project_3d(self.pos.x, self.pos.y)
        sx, sy, _ = project_3d(
            self.pos.x, self.pos.y, self.radius
        )

        radius = max(4, round(self.radius * scale))

        pygame.draw.ellipse(
            surface,
            (8, 8, 12),
            (
                gx - radius,
                gy - radius // 2,
                radius * 2,
                max(3, radius),
            ),
        )

        pygame.draw.circle(surface, RED, (sx, sy), radius)
        pygame.draw.circle(
            surface, (255, 160, 170), (sx, sy), radius, 1
        )


class Bullet:
    def __init__(self, start, target):
        self.pos = pygame.Vector2(start)
        self.previous_pos = pygame.Vector2(start)
        self.radius = 4

        direction = target - self.pos

        if not direction.length_squared():
            direction = pygame.Vector2(0, -1)

        self.velocity = direction.normalize() * 700

    def update(self, dt):
        self.previous_pos.update(self.pos.x, self.pos.y)
        self.pos += self.velocity * dt

    def outside_arena(self):
        return not (
            0 <= self.pos.x <= ARENA_WIDTH
            and 0 <= self.pos.y <= ARENA_DEPTH
        )

    def draw(self, surface):
        start = project_point(
            self.previous_pos.x, self.previous_pos.y, 14
        )
        end = project_point(self.pos.x, self.pos.y, 14)

        pygame.draw.line(surface, CYAN, start, end, 3)
        pygame.draw.circle(surface, WHITE, end, 2)


class Shockwave:
    def __init__(self, center):
        self.center = pygame.Vector2(center)
        self.radius = 8
        self.max_radius = 1050
        self.speed = 1100

    @property
    def active(self):
        return self.radius < self.max_radius

    def update(self, dt):
        self.radius += self.speed * dt

    def draw(self, surface):
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade = max(0, 1 - self.radius / self.max_radius)
        alpha = int(240 * fade)

        for width, opacity in (
            (18, alpha // 6),
            (10, alpha // 3),
            (4, alpha),
        ):
            previous = None

            for angle in range(0, 361, 3):
                radians = math.radians(angle)

                x = self.center.x + math.cos(radians) * self.radius
                y = self.center.y + math.sin(radians) * self.radius

                if camera_depth(x, y, 3) <= NEAR_CLIP:
                    previous = None
                    continue

                point = project_point(x, y, 3)

                if previous is not None:
                    pygame.draw.line(
                        glow,
                        (*PURPLE, opacity),
                        previous,
                        point,
                        width,
                    )

                previous = point

        surface.blit(glow, (0, 0))


# --------------------------------------------------
# ARENA RENDERING
# --------------------------------------------------

def draw_floor(surface):
    corners = [
        project_point(0, 0),
        project_point(ARENA_WIDTH, 0),
        project_point(ARENA_WIDTH, ARENA_DEPTH),
        project_point(0, ARENA_DEPTH),
    ]

    pygame.draw.polygon(surface, FLOOR_COLOR, corners)

    for x in range(0, ARENA_WIDTH + 1, 40):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            project_point(x, 0),
            project_point(x, ARENA_DEPTH),
        )

    for y in range(0, ARENA_DEPTH + 1, 40):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            project_point(0, y),
            project_point(ARENA_WIDTH, y),
        )

    pygame.draw.polygon(surface, CYAN, corners, 2)


def draw_wall(surface, wall):
    ground = [
        project_point(wall.left, wall.top),
        project_point(wall.right, wall.top),
        project_point(wall.right, wall.bottom),
        project_point(wall.left, wall.bottom),
    ]

    top = [
        project_point(wall.left, wall.top, WALL_HEIGHT),
        project_point(wall.right, wall.top, WALL_HEIGHT),
        project_point(wall.right, wall.bottom, WALL_HEIGHT),
        project_point(wall.left, wall.bottom, WALL_HEIGHT),
    ]

    # Draw the side facing the camera's horizontal position.
    if CAMERA_X < wall.left:
        side = [ground[0], ground[3], top[3], top[0]]
        pygame.draw.polygon(surface, (18, 45, 70), side)
        pygame.draw.polygon(surface, (0, 120, 160), side, 1)

    elif CAMERA_X > wall.right:
        side = [ground[1], ground[2], top[2], top[1]]
        pygame.draw.polygon(surface, (18, 45, 70), side)
        pygame.draw.polygon(surface, (0, 120, 160), side, 1)

    front = [ground[3], ground[2], top[2], top[3]]

    pygame.draw.polygon(surface, (20, 55, 85), front)
    pygame.draw.polygon(surface, (0, 150, 190), front, 1)

    pygame.draw.polygon(surface, (35, 80, 115), top)
    pygame.draw.polygon(surface, CYAN, top, 2)


def draw_scene(surface, player, enemies, bullets, blasts, game_over):
    draw_floor(surface)

    # Simple back-to-front ordering for the raised walls and entities.
    drawables = []

    for wall in WALLS:
        depth = camera_depth(wall.centerx, wall.bottom)
        drawables.append((depth, "wall", wall))

    entities = enemies + bullets

    if not game_over:
        entities.append(player)

    for entity in entities:
        depth = camera_depth(entity.pos.x, entity.pos.y)
        drawables.append((depth, "entity", entity))

    drawables.sort(key=lambda item: item[0], reverse=True)

    for _, kind, item in drawables:
        if kind == "wall":
            draw_wall(surface, item)
        else:
            item.draw(surface)

    for blast in blasts:
        blast.draw(surface)


def draw_hud(surface, player, score, enemies, last_bomb, now):
    pygame.draw.rect(surface, (12, 17, 28), (0, 0, WIDTH, 105))

    score_text = HUD_FONT.render(
        f"CORE SCORE: {score:06d}", True, CYAN
    )
    surface.blit(score_text, (20, 15))

    pygame.draw.rect(surface, GRAY, (20, 45, 180, 14))

    health_width = round(
        180 * player.health / player.max_health
    )

    health_color = GREEN if player.health > 35 else RED

    pygame.draw.rect(
        surface,
        health_color,
        (20, 45, health_width, 14),
    )
    pygame.draw.rect(surface, WHITE, (20, 45, 180, 14), 1)

    remaining = max(
        0, BOMB_COOLDOWN_MS - (now - last_bomb)
    )

    if remaining > 0:
        status = f"BOMB CHARGING: {remaining / 1000:.1f}s"
        color = RED
    elif score < BOMB_COST:
        status = f"BOMB: {score}/{BOMB_COST} POINTS"
        color = GRAY
    else:
        status = "BOMB ONLINE: PRESS SPACE"
        color = PURPLE

    surface.blit(
        HUD_FONT.render(status, True, color),
        (20, 73),
    )

    threat_text = HUD_FONT.render(
        f"THREATS: {len(enemies):02d}", True, RED
    )
    surface.blit(
        threat_text,
        (WIDTH - threat_text.get_width() - 20, 15),
    )

    view_text = SMALL_FONT.render(
        "FIXED ANGLED ARENA CAMERA", True, GRAY
    )
    surface.blit(
        view_text,
        (WIDTH - view_text.get_width() - 20, 45),
    )

    controls = SMALL_FONT.render(
        "WASD / ARROWS: MOVE   |   CLICK: SHOOT   |   "
        "SPACE: BOMB   |   ESC: EXIT",
        True,
        WHITE,
    )

    surface.blit(
        controls,
        (
            WIDTH // 2 - controls.get_width() // 2,
            HEIGHT - 30,
        ),
    )
# --------------------------------------------------
# PROCEDURAL SOUND EFFECTS
# --------------------------------------------------

class SoundEffects:
    def __init__(self):
        self.sounds = {}

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512,
                )

            self.sample_rate, sample_format, self.channels = (
                pygame.mixer.get_init()
            )

            # The generator below produces signed 16-bit samples.
            if sample_format != -16:
                return

            pygame.mixer.set_num_channels(24)
            pygame.mixer.set_reserved(1)

            self.bomb_channel = pygame.mixer.Channel(0)

            self.sounds["shoot"] = self.make_sound(
                duration=0.09,
                start_frequency=1000,
                end_frequency=260,
                noise_amount=0.08,
                volume=0.20,
            )

            self.sounds["kill"] = self.make_sound(
                duration=0.20,
                start_frequency=240,
                end_frequency=55,
                noise_amount=0.65,
                volume=0.32,
            )

            self.sounds["damage"] = self.make_sound(
                duration=0.22,
                start_frequency=160,
                end_frequency=65,
                noise_amount=0.25,
                volume=0.28,
            )

            self.sounds["bomb"] = self.make_sound(
                duration=1.0,
                start_frequency=110,
                end_frequency=25,
                noise_amount=0.55,
                volume=0.48,
            )

        except pygame.error:
            # Keep the game playable without an audio device.
            self.sounds.clear()

    def make_sound(
        self,
        duration,
        start_frequency,
        end_frequency,
        noise_amount,
        volume,
    ):
        samples = array("h")
        sample_count = int(self.sample_rate * duration)
        phase = 0.0

        # Separate RNG: sound generation won't change enemy randomness.
        rng = random.Random(81)

        for index in range(sample_count):
            progress = index / max(1, sample_count - 1)

            frequency = (
                start_frequency
                + (end_frequency - start_frequency) * progress
            )

            phase += math.tau * frequency / self.sample_rate

            tone = math.sin(phase)
            noise = rng.uniform(-1, 1)

            attack = min(1.0, index / (self.sample_rate * 0.004))
            envelope = attack * (1.0 - progress) ** 2

            value = (
                tone * (1.0 - noise_amount)
                + noise * noise_amount
            )

            sample = int(
                max(-1.0, min(1.0, value * envelope * volume))
                * 32767
            )

            for _ in range(self.channels):
                samples.append(sample)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        sound = self.sounds.get(name)

        if sound is None:
            return

        if name == "bomb":
            self.bomb_channel.play(sound)
        else:
            sound.play()


# --------------------------------------------------
# WORLD-SPACE PARTICLES
# --------------------------------------------------

class Particle:
    def __init__(self, position, color, power=1.0):
        self.pos = pygame.Vector2(position)
        self.z = random.uniform(8, 20)

        angle = random.uniform(0, math.tau)
        speed = random.uniform(45, 180) * power

        self.velocity = pygame.Vector2(
            math.cos(angle),
            math.sin(angle),
        ) * speed

        self.vertical_speed = random.uniform(70, 220) * power
        self.life = random.uniform(0.3, 0.75)
        self.max_life = self.life
        self.size = random.uniform(3, 7)
        self.color = color

    def update(self, dt):
        self.life -= dt
        self.pos += self.velocity * dt
        self.velocity *= math.exp(-2.5 * dt)

        self.vertical_speed -= 550 * dt
        self.z += self.vertical_speed * dt

        if self.z < 0:
            self.z = 0
            self.vertical_speed = abs(self.vertical_speed) * 0.3

    def draw(self, surface):
        if camera_depth(self.pos.x, self.pos.y, self.z) <= NEAR_CLIP:
            return

        sx, sy, scale = project_3d(
            self.pos.x,
            self.pos.y,
            self.z,
        )

        fade = max(0.0, self.life / self.max_life)
        radius = max(1, round(self.size * scale * fade))

        pygame.draw.circle(
            surface,
            (*self.color, int(220 * fade)),
            (sx, sy),
            radius + 2,
        )

        pygame.draw.circle(
            surface,
            (255, 245, 230, int(255 * fade)),
            (sx, sy),
            max(1, radius // 2),
        )


def emit_particles(particles, position, color, count, power=1.0):
    for _ in range(count):
        particles.append(Particle(position, color, power))

    # Limit the particle count during busy fights.
    if len(particles) > 1000:
        del particles[:len(particles) - 1000]


def draw_particles(surface, particles, layer):
    layer.fill((0, 0, 0, 0))

    for particle in particles:
        particle.draw(layer)

    surface.blit(layer, (0, 0))

# --------------------------------------------------
# GAME LOOP
# --------------------------------------------------

def main():
    player = Player()

    enemies = []
    bullets = []
    blasts = []
    particles = []
    sounds = SoundEffects()

    particle_layer = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA,
    )
    score = 0
    last_bomb = -BOMB_COOLDOWN_MS
    last_spawn = pygame.time.get_ticks()

    game_over = False
    running = True

    while running:
        dt = min(clock.tick(60) / 1000.0, 0.04)
        now = pygame.time.get_ticks()
        bomb_triggered = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE and not game_over:
                    cooldown_ready = (
                        now - last_bomb >= BOMB_COOLDOWN_MS
                    )

                    if score >= BOMB_COST and cooldown_ready:
                        score -= BOMB_COST
                        last_bomb = now

                        sounds.play("bomb")

                        emit_particles(
                            particles,
                            player.pos,
                            PURPLE,
                            count=120,
                            power=1.8,
                        )

                        # Give every destroyed enemy its own burst.
                        for enemy in enemies:
                            emit_particles(
                                particles,
                                enemy.pos,
                                RED,
                                count=16,
                                power=1.1,
                            )

                        enemies.clear()
                        blasts.append(Shockwave(player.pos))
                        bomb_triggered = True

                elif event.key == pygame.K_r and game_over:
                    player.reset()
                    enemies.clear()
                    bullets.clear()
                    blasts.clear()
                    particles.clear()
                    score = 0
                    last_bomb = -BOMB_COOLDOWN_MS
                    last_spawn = now
                    game_over = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over:
                    target = screen_to_world(*event.pos)
                    bullets.append(Bullet(player.pos, target))

                    sounds.play("shoot")

                    aim = target - player.pos

                    if aim.length_squared():
                        muzzle = player.pos + aim.normalize() * 25
                    else:
                        muzzle = pygame.Vector2(player.pos)

                    emit_particles(
                        particles,
                        muzzle,
                        CYAN,
                        count=5,
                        power=0.35,
                    )
        if not running:
            break

        if not game_over:
            if bomb_triggered:
                # Prevent a new enemy appearing in the bomb frame.
                last_spawn = now

            elif now - last_spawn >= SPAWN_INTERVAL_MS:
                enemies.append(Enemy())
                last_spawn = now

            player.update(pygame.key.get_pressed(), dt)

            for enemy in enemies:
                enemy.update(player.pos, dt)

            for bullet in bullets[:]:
                bullet.update(dt)

                start = (
                    round(bullet.previous_pos.x),
                    round(bullet.previous_pos.y),
                )
                end = (
                    round(bullet.pos.x),
                    round(bullet.pos.y),
                )

                # Find the first wall or enemy along the bullet path.
                nearest_distance = float("inf")
                hit_wall = False
                hit_enemy = None

                for wall in WALLS:
                    expanded = wall.inflate(
                        bullet.radius * 2,
                        bullet.radius * 2,
                    )
                    intersection = expanded.clipline(start, end)

                    if intersection:
                        distance = (
                            pygame.Vector2(intersection[0])
                            - bullet.previous_pos
                        ).length_squared()

                        if distance < nearest_distance:
                            nearest_distance = distance
                            hit_wall = True
                            hit_enemy = None

                for enemy in enemies:
                    expanded = body_rect(
                        enemy.pos,
                        enemy.radius + bullet.radius,
                    )
                    intersection = expanded.clipline(start, end)

                    if intersection:
                        distance = (
                            pygame.Vector2(intersection[0])
                            - bullet.previous_pos
                        ).length_squared()

                        if distance < nearest_distance:
                            nearest_distance = distance
                            hit_wall = False
                            hit_enemy = enemy

                if hit_enemy is not None:
                    sounds.play("kill")

                    emit_particles(
                        particles,
                        hit_enemy.pos,
                        RED,
                        count=26,
                        power=1.0,
                    )

                    enemies.remove(hit_enemy)
                    bullets.remove(bullet)
                    score += 100

                elif hit_wall:
                    # Recover the approximate first contact point.
                    travel = bullet.pos - bullet.previous_pos

                    if travel.length_squared():
                        impact = (
                            bullet.previous_pos
                            + travel.normalize()
                            * math.sqrt(nearest_distance)
                        )
                    else:
                        impact = pygame.Vector2(bullet.pos)

                    emit_particles(
                        particles,
                        impact,
                        CYAN,
                        count=9,
                        power=0.55,
                    )

                    bullets.remove(bullet)

                elif bullet.outside_arena():
                    bullets.remove(bullet)

            touching_enemy = any(
                player.pos.distance_squared_to(enemy.pos)
                <= (player.radius + enemy.radius) ** 2
                for enemy in enemies
            )

            if (
                touching_enemy
                and now - player.last_damage_time >= 500
            ):
                player.health = max(0, player.health - 10)
                player.last_damage_time = now
                sounds.play("damage")

                emit_particles(
                    particles,
                    player.pos,
                    GREEN,
                    count=18,
                    power=0.8,
                )
                if player.health == 0:
                    game_over = True

        for blast in blasts:
            blast.update(dt)

        blasts[:] = [blast for blast in blasts if blast.active]
        for particle in particles:
            particle.update(dt)

        particles[:] = [
            particle for particle in particles
            if particle.life > 0
        ]
        screen.fill(BLACK)

        draw_scene(
            screen,
            player,
            enemies,
            bullets,
            blasts,
            game_over,
        )
        draw_particles(screen, 
                       particles, 
                       particle_layer)
        draw_hud(
            screen,
            player,
            score,
            enemies,
            last_bomb,
            now,
        )

        if game_over:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((5, 8, 15, 220))
            screen.blit(overlay, (0, 0))

            title = TITLE_FONT.render(
                "CORE SYSTEM FAILED", True, RED
            )
            restart = HUD_FONT.render(
                "PRESS R TO RESTART", True, WHITE
            )
            final_score = HUD_FONT.render(
                f"FINAL BALANCE: {score}", True, CYAN
            )

            for text, offset in (
                (title, -65),
                (final_score, 0),
                (restart, 45),
            ):
                screen.blit(
                    text,
                    (
                        WIDTH // 2 - text.get_width() // 2,
                        HEIGHT // 2 + offset,
                    ),
                )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()