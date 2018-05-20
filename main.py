import os, sys, pygame, os, random
from pygame.locals import *
from pygame import constants
from pgu import gui

from constants import *
from base import Scene, Rural, Suburb, GameObject

class TestScene(Scene):
    title = "Having a House"
    prompt = "How would you like to care for your home?"

    def render(self, screen):
        super().render(screen)
        house_img = pygame.image.load(os.path.join(BASE_PATH, 'data', 'rural_base_blue.png'))
        house_img = pygame.transform.scale(house_img, (200, 250))
        screen.blit(house_img, [400,300])
        for image, coords, scale in self.gameobject.visualizations:
            image = pygame.image.load(os.path.join(BASE_PATH, 'data', image))
            image = pygame.transform.scale(image, scale)
            screen.blit(image, coords)


class TitleScene(Scene):
    def __init__(self, gameobject):
        self.font_l = pygame.font.SysFont(None, 42)
        self.font_m = pygame.font.SysFont(None, 26)
        self.font_s = pygame.font.SysFont(None, 24)
        self.title = self.font_l.render(TITLE, True, WHITE)
        self.author = self.font_m.render('By IPs', True, WHITE)
        self.instructions = [
            self.font_s.render("> Press 'Space Bar' for Start Game", True, WHITE),
            self.font_s.render("> Press 'Escape' to Exit", True, WHITE),
            # self.font_s.render("> Press 'O' to Load Game ", True, WHITE),
            # self.font_s.render("> Press 'I' for instructions", True, WHITE)
        ]
        super().__init__(gameobject)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                terminate()
            if e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(StartScene(self.gameobject))

    def render(self, screen):
        screen.fill(BLACK)
        image = pygame.image.load(os.path.join(BASE_PATH, 'data', 'background_image.png'))
        image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(image, [0,0])
        screen.blit(self.title, (20, 25))
        screen.blit(self.author, (20, 70))
        accumulated_height = 120
        for instruction in self.instructions:
            screen.blit(instruction, (25, accumulated_height))
            accumulated_height += 35


class StartScene(Scene):
    title = ''
    prompt = 'Choose your home type'
    background = 'background_image.png'

    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.instructions = [
            self.font_s.render("> A. 2BD/2BA in Suburbia", True, WHITE),
            self.font_s.render("> B. 2BD/2BA Rural Property", True, WHITE)
        ]

    def update(self):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        if self.background:
            image = pygame.image.load(os.path.join(BASE_PATH, 'data', self.background))
            image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(image, [0, 0])
        title = self.font_l.render(self.title, True, WHITE)
        screen.blit(title, XY_TITLE)
        prompt = self.font_m.render(self.prompt, True, WHITE)
        screen.blit(prompt, XY_PROMPT)

        instruction_height = 100
        for instruction in self.instructions:
            screen.blit(instruction, (45, instruction_height))
            instruction_height += 25

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_a:
                self.gameobject.house = Suburb()
                self.manager.go_to(TestScene(self.gameobject))
            if e.type == KEYDOWN and e.key == K_b:
                self.gameobject.house = Rural()
                self.manager.go_to(TestScene(self.gameobject))


class SceneManager:
    def __init__(self):
        self.scene = None
        gameobject = GameObject()
        self.go_to(TitleScene(gameobject))

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self


def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption(TITLE)
    timer = pygame.time.Clock()
    running = True
    manager = SceneManager()

    while running:
        timer.tick(FPS)
        if pygame.event.get(QUIT):
            running = False
            return

        screen = pygame.display.get_surface()
        manager.scene.handle_events(pygame.event.get())
        manager.scene.update()
        manager.scene.render(screen)
        pygame.display.flip()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__': main()
