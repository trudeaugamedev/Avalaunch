from .constants import VEC, FONT, TEXT_COLOR
from .sprite import Layers, VisibleSprite
from .scene import Scene

from pygame.locals import *
from typing import Callable
import pygame

class Button(VisibleSprite):
    mouse_over = None
    mouse_down_in = None
    mouse_up_in = None

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int], text: str, command: Callable, centered: bool = False, style: bool = True, font_size: int = 36, font_color: tuple[int, int, int] = TEXT_COLOR) -> None:
        super().__init__(scene, Layers.GUI)
        self.size = VEC(size)
        self.pos = VEC(pos)
        if centered:
            self.pos = self.pos - self.size // 2
        self.rect = pygame.Rect(self.pos, self.size)
        self.text = text
        self.text_surf = FONT[font_size].render(self.text, False, font_color)
        self.text_size = VEC(self.text_surf.get_size())
        self.style = style
        self.command = command

    def update(self) -> None:
        m_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(m_pos):
            self.mouse_over = self
            if MOUSEBUTTONDOWN in self.manager.events:
                self.mouse_down_in = self
                self.mouse_up_in = None
            elif MOUSEBUTTONUP in self.manager.events:
                self.mouse_up_in = self
        elif self.mouse_over is self:
            self.mouse_over = None
            self.mouse_down_in = None

        if self.mouse_down_in is self.mouse_up_in is self:
            self.mouse_down_in = self.mouse_up_in = None
            self.command()

    def draw(self) -> None:
        if self.style:
            (surf := pygame.Surface(self.size, SRCALPHA)).fill((255, 255, 255, 80))
            self.manager.screen.blit(surf, self.pos)
            pygame.draw.rect(self.manager.screen, (0, 0, 0), (*self.pos, *self.size), 3)
        self.manager.screen.blit(self.text_surf, self.pos + self.size // 2 - (self.text_size.x // 2, self.text_size.y // 2 * 1.1))