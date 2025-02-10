import pygame
import const

import poker.hands as hands
import poker.scraping as scraping

import ui.scenes as scenes
import ui.utils as utils
import ui.elements as elements
import ui.sprites as sprites

if __name__ == "__main__":
    pygame.init()
    screen = utils.make_fancy_scaled_display(
        const.GAME_DIMS,
        scale_factor=1.,
        outer_fill_color=(0, 0, 0),
        extra_flags=pygame.RESIZABLE
    )
    pygame.display.set_caption(const.NAME_OF_GAME)

    sprites.Sprites.initialize(utils.res_path("assets/fonts/m6x11.ttf"))
    all_hands = scraping.scrape_directory(const.HERO_ID, const.LOG_DOWNLOADER_ID, const.LOG_DIR)

    grid_res = (500, 500)
    grid = elements.CardGrid([20, screen.get_height() / 2 - grid_res[1] / 2, grid_res[0], grid_res[1]], all_hands)
    # for cc in poker.cardutils.all_card_codes():
    #     print(f"{cc}:\t{grid.get_rect_for(cc)}")

    clock = pygame.time.Clock()
    dt = 0

    scene_manager = scenes.SceneManager(scenes.Scene())

    running = True
    while running and not scene_manager.should_quit:
        const.KEYS_PRESSED_THIS_FRAME.clear()
        const.KEYS_RELEASED_THIS_FRAME.clear()
        const.MOUSE_PRESSED_AT_THIS_FRAME.clear()
        const.MOUSE_RELEASED_AT_THIS_FRAME.clear()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                const.KEYS_PRESSED_THIS_FRAME.add(e.key)
                const.KEYS_HELD_THIS_FRAME.add(e.key)
            elif e.type == pygame.KEYUP:
                const.KEYS_RELEASED_THIS_FRAME.add(e.key)
                if e.key in const.KEYS_HELD_THIS_FRAME:
                    const.KEYS_HELD_THIS_FRAME.remove(e.key)
            elif e.type == pygame.MOUSEMOTION:
                const.MOUSE_XY = e.pos
            elif e.type == pygame.MOUSEBUTTONDOWN:
                const.MOUSE_PRESSED_AT_THIS_FRAME[e.button] = e.pos
                const.MOUSE_BUTTONS_HELD_THIS_FRAME.add(e.button)
            elif e.type == pygame.MOUSEBUTTONUP:
                const.MOUSE_RELEASED_AT_THIS_FRAME[e.button] = e.pos
                if e.button in const.MOUSE_BUTTONS_HELD_THIS_FRAME:
                    const.MOUSE_BUTTONS_HELD_THIS_FRAME.remove(e.button)
            elif e.type == pygame.WINDOWLEAVE:
                const.MOUSE_XY = None

        scene_manager.update(dt)
        scene_manager.render(screen)

        grid.render(screen)

        pygame.display.flip()

        dt = clock.tick(60)