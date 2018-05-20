import os, sys, pygame, os, random
from pygame.locals import *
from pgu import gui


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DISPLAY = (SCREEN_WIDTH, SCREEN_HEIGHT)
FLAGS = 0
DEPTH = 0
FPS = 0
TITLE = 'Have A House'

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
        else:final_lines.append(requested_line)

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


class Scene:
    def render(self, screen):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


class TitleScene(Scene):
    def __init__(self):
        self.font_l = pygame.font.SysFont(None, 42)
        self.font_m = pygame.font.SysFont(None, 26)
        self.font_s = pygame.font.SysFont(None, 24)
        self.title = self.font_l.render(TITLE, True, WHITE)
        self.author = self.font_m.render('By IPs', True, WHITE)
        self.instructions = [
            self.font_s.render("> Press 'Space Bar' for New Game", True, WHITE),
            self.font_s.render("> Press 'Escape' to Exit", True, WHITE),
            self.font_s.render("> Press 'O' to Load Game ", True, WHITE),
            self.font_s.render("> Press 'I' for instructions", True, WHITE)
        ]

    def update(self):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                terminate()
            if e.type == KEYDOWN and e.key == K_o:
                chapterKey, page_index = load_file()
                self.manager.go_to(StoryScene(chapterKey, page_index))
            if e.type == KEYDOWN and e.key == K_SPACE:
                self.manager.go_to(StoryScene('ChapterOne', 0))
            if e.type == KEYDOWN and e.key == K_i:
                self.manager.go_to(InstructionScene())

    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.title, (20, 25))
        screen.blit(self.author, (20, 70))
        accumulated_height = 120
        for instruction in self.instructions:
            screen.blit(instruction, (25, accumulated_height))
            accumulated_height += 35


class InstructionScene(Scene):
    def __init__(self):
        self.font_l = pygame.font.SysFont(None, 32)
        self.font_s = pygame.font.SysFont(None, 18)
        self.title = self.font_l.render("Intstructions", True, WHITE)
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
        self.go_to(TitleScene())

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
