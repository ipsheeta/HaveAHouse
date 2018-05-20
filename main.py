import os, sys, pygame, os, random
from pygame.locals import *
from pygame import constants
from pgu import gui

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DISPLAY = (SCREEN_WIDTH, SCREEN_HEIGHT)
FLAGS = 0
DEPTH = 0
FPS = 0
TITLE = 'Have A House'

XY_TITLE = (20, 25)
XY_PROMPT = (20, 70)
X_CHOICES = 25
Y_CHOICES = 120
INC_CHOICES = 35

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BASE_PATH = os.getcwd()


def save_file(content, filepath=None):
    if filepath is None:
        filepath = os.path.join(BASE_PATH, '.savefiles', 'autosave')
        chapterKey, page_index = content[0], content[1]
        to_file = "{} {}".format(chapterKey, page_index)
        with open(filepath, 'w') as f:
            f.write(to_file)


def load_file(filepath=None):
    if filepath is None:
        filepath = os.path.join(BASE_PATH, '.savefiles', 'autosave')
    with open(filepath, 'r') as f:
        content = ''
        for line in f.lines:
            content += line
        content = content.split(" ")
        chapterKey, page_index = content[0], content[1]
    return str(chapterKey), int(page_index)


def load_image(filename, color_key=None):
    filepath = os.path.join(BASE_PATH, "data", filename)
    if color_key is None:
        img = pygame.image.load(filepath).convert()
        img.set_colorkey(BLACK)
    else:
        img = pygame.image.load(filepath).convert_alpha()
    return img


def render_textrect(string, font, rect, text_color, justification=0):
    final_lines = []
    requested_lines = string.splitlines()
    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(" ")
            for word in words:
                # TODO mad inefficient
                if font.size(word)[0] >= rect.width:
                    raise TextRectException("The word exceeds the width of the rectangle")

            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + ' '
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    surface = pygame.Surface(rect.size)
    surface.fill(BLACK)
    surface.set_colorkey(BLACK)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException("The text vertical height exceeds the height of the rectangle")
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException("Invalid justification argument")
            accumulated_height += font.size(line)[1]
    return surface


class TextRectException(Exception):
    pass


class House:
    value = 0
    winning = 1000000


class Rural:
    value = 125000
    winning = 137500


class Suburb:
    value = 400000
    winning = 440000


class GameObject:
    def __init__(self, balance=0, house=House()):
        self.balance = balance
        self.house = house
        self.value = 0
        self.repairs = []
        self.improvements = [("Install Solar", "install_solar"),
                             ("Change Paint", "change_paint"),
                             ("Add Addition", "add_addition"),
                             ]
        self.turn = 1

    def do_event(self, event):
        method = getattr(self, event)
        method()
        mark = None
        for t in self.improvements:
            if event == t[1]:
                mark = t
        if mark:
            self.improvements.remove(mark)
            print(self.improvements)
            return

        for t in self.repairs:
            if event == t[1]:
                mark = t

        if mark:
            self.repairs.remove(mark)
            return
        return

    # improvements
    def install_solar(self):
        self.balance -= 10000
        self.house.value += 8000

    def change_paint(self):
        self.balance -= 1000
        self.house.value *= 1.02

    def add_addition(self):
        self.balance -= 25000
        self.house.value += 20000

    # repairs
    def fix_leak(self):
        self.balance -= 10000
        self.house.value += 10000

    def fix_smash(self):
        self.balance -= 500
        self.house.value += 500

    def fix_splat(self):
        self.balance -= 5000
        self.house.value += 5000

    def end_turn(self):
        self.house.value *= 1.01
        if self.turn == 2:
            self.repairs.append(("Fix Leak", "fix_leak"))
            self.house.value *= .60
        if self.turn == 3:
            self.repairs.append(("Fix Smash", "fix_smash"))
            self.house.value *= .80
        if self.turn == 5:
            self.repairs.append(("Fix Splat", "fix_splat"))
            self.house.value *= .90
        self.turn += 1


class Scene:
    font_large = 42
    font_medium = 30
    font_small = 24
    title = ''
    prompt = ''
    background = None

    def __init__(self, gameobject):
        self.gameobject = gameobject
        self.choice_list()
        self.font_l = pygame.font.SysFont(None, self.font_large)
        self.font_m = pygame.font.SysFont(None, self.font_medium)
        self.font_s = pygame.font.SysFont(None, self.font_small)

    def choice_list(self):
        keys = {}
        choices = self.gameobject.repairs + self.gameobject.improvements
        self.choices = []
        for key, (text, event) in enumerate(choices, 1):
            keys[getattr(constants, "K_{}".format(key))] = event
            self.choices.append((key, text))
        self.keys = keys

    def render(self, screen):
        screen.fill(BLACK)
        if self.background:
            image = pygame.image.load(os.path.join(BASE_PATH, 'data', self.background))
            screen.blit(image, [0, 0])
        title = self.font_l.render(self.title, True, WHITE)
        screen.blit(title, XY_TITLE)
        prompt = self.font_m.render(self.prompt, True, WHITE)
        screen.blit(prompt, XY_PROMPT)
        accumulated_height = Y_CHOICES
        for choice, text in self.choices:
            choice = self.font_s.render("> {}. {}".format(choice, text), True, WHITE)
            screen.blit(choice, (X_CHOICES, accumulated_height))
            accumulated_height += INC_CHOICES

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key in self.keys:
                # fire event to game object
                self.gameobject.do_event(self.keys[e.key])
                return
            if e.type == KEYDOWN and e.key == K_SPACE:
                self.gameobject.end_turn()
                # self.update() #add night background animation

    def update(self):
        self.choice_list()


class TestScene(Scene):
    title = "Test"
    prompt = "Prompt Test"


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
            self.font_s.render("> Press 'O' to Load Game ", True, WHITE),
            # self.font_s.render("> Press 'I' for instructions", True, WHITE)
        ]
        super().__init__(gameobject)

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                terminate()
            # if e.type == KEYDOWN and e.key == K_o:
            #     chapterKey, page_index = load_file()
            #     self.manager.go_to(StoryScene(chapterKey, page_index))
            if e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(StartScene(self.gameobject))

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(pygame.image.load(os.path.join(BASE_PATH, 'data', 'background_image.png')), [0, 0])
        screen.blit(self.title, (20, 25))
        screen.blit(self.author, (20, 70))
        accumulated_height = 120
        for instruction in self.instructions:
            screen.blit(instruction, (25, accumulated_height))
            accumulated_height += 35


class StartScene(Scene):
    title = ''
    prompt = 'Choose your home type'

    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.instructions = [
            self.font_s.render("> A. 2BD/2BA in Suburbia", True, WHITE),
            self.font_s.render("> B. 2BD/2BA Rural Property", True, WHITE)
        ]

    def update(self):
        pass

    def render(self, screen):
        super().render(screen)
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


class InstructionScene(Scene):
    def __init__(self):
        self.font_l = pygame.font.SysFont(None, 32)
        self.font_s = pygame.font.SysFont(None, 18)
        self.title = self.font_l.render("Instructions", True, WHITE)
        self.instructions = [
            self.font_s.render("> ", True, WHITE),
            self.font_s.render("> ", True, WHITE)
        ]

    def update(self):
        pass

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.title, (45, 25))
        instruction_height = 100
        for instruction in self.instructions:
            screen.blit(instruction, (45, instruction_height))
            instruction_height += 25

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                self.manager.go_to(TitleScene())


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
