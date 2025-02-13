import typing

import pygame


class Sprites:

    FONT_TINY: typing.Optional[pygame.Font] = None
    FONT_SMALL: typing.Optional[pygame.Font] = None
    FONT: typing.Optional[pygame.Font] = None

    @staticmethod
    def initialize(font_path):
        Sprites.FONT_TINY = pygame.font.Font(font_path, size=9)
        Sprites.FONT_SMALL = pygame.font.Font(font_path, size=16)
        Sprites.FONT = pygame.font.Font(font_path)
