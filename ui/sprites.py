import typing

import pygame


class Sprites:

    FONT: typing.Optional[pygame.Font] = None

    @staticmethod
    def initialize(font_path):
        Sprites.FONT = pygame.font.Font(font_path)
