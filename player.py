from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_a, K_d, K_w, KEYUP, K_SPACE
import pygame

from utils import intvec, snap, clamp, clamp_max
from constants import VEC, WIDTH, HEIGHT, GRAVITY
from sprite import VisibleSprite, Layers
from snowball import Snowball
from ground import Ground

class Camera:
    def __init__(self, master: Player):
        self.master = master
        self.manager = self.master.manager
        self.float_offset = self.master.pos - (WIDTH // 2, HEIGHT // 2 + 100) + self.master.size / 2
        self.offset = intvec(self.float_offset)

    def update(self):
        tick_offset = self.master.pos - self.offset - (WIDTH // 2, HEIGHT // 2 + 100) + self.master.size / 2
        self.float_offset += tick_offset * 5 * self.manager.dt
        self.offset = intvec(self.float_offset)

class Player(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(30, 60)
        self.pos = VEC(0, 0)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.speed = 150
        self.rect = pygame.Rect(self.pos, self.size)
        self.on_ground = False

        self.throwing = False
        self.sb_vel = 0

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
        self.MAX_SPEED = 200
        self.JUMP_SPEED = -400
        self.THROW_SPEED = 800
        self.SB_OFFSET = self.size // 2 - (0, 10)

        self.camera = Camera(self)

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if keys[K_a]: # Acceleration
            self.acc.x -= self.CONST_ACC
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
        if keys[K_d]:
            self.acc.x += self.CONST_ACC
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC

        if keys[K_w] and self.on_ground:
            self.vel.y = self.JUMP_SPEED

        if keys[K_SPACE]:
            m_pos = VEC(pygame.mouse.get_pos())
            self.throwing = True
            # Use camera offset to convert screen-space pos to in-world pos
            try:
                self.sb_vel = -((m_pos - self.SB_OFFSET + self.camera.offset) - self.pos).normalize() * self.THROW_SPEED
            except ValueError:
                self.sb_vel = VEC() # 0 vector
        if KEYUP in self.manager.events:
            if self.manager.events[KEYUP].key == K_SPACE:
                self.throwing = False
                Snowball(self.scene, self.sb_vel)

        self.vel += self.acc * self.manager.dt
        # _ to catch the successful clamp return value
        # Baiscally if it clamped to the left it would be -1, right would be 1, if it didn't clamp (value is in range), it's 0
        self.vel.x, _ = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        self.rect.topleft = self.pos

        self.on_ground = False
        for ground in Ground.instances:
            if not self.rect.colliderect(ground.rect): continue
            if self.rect.bottom < ground.rect.top + 2:
                self.pos.y = ground.rect.top - self.size.y
                self.vel.y = 0
            else:
                self.pos.y -= 200 * self.manager.dt
                self.vel.y = 0
            self.on_ground = True

        self.camera.update()

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*(self.pos - self.camera.offset), *self.size))
        if not self.throwing: return
        factor = 0.015 # Basically how accurate we want the calculation to be, the distance factor between two points
        pos = self.pos + self.SB_OFFSET
        vel = self.sb_vel.copy()
        for i in range(40): # Number of points on the parabola that will be calculated
            vel.y += GRAVITY * factor
            pos += vel * factor
            if i % 4: continue # For every 4 calculated points, we draw 1 point
            pygame.draw.circle(self.manager.screen, (0, 0, 0), pos - self.camera.offset, 5)