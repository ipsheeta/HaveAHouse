import os, sys, pygame, os, random
from pygame.locals import *
from pygame import constants
from pgu import gui

from constants import *

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
    image = None

class Rural:
    value = 125000
    winning = 137500
    image = 'rural_base_blue.png'


class Suburb:
    value = 400000
    winning = 440000
    image = 'rural_base_blue.png'


class GameObject:
    smash = ('smash.png', [390,370], [70,50])
    leak = ('leak.png', [550,450], [100,170])
    splat = ('splat.png', [500,375], [100,100])
    def __init__(self, balance=0, house=House()):
        self.balance = balance
        self.house = house
        self.value = 0
        self.visualizations = []
        self.repairs = []
        self.improvements = [("$10,000 - Install Solar", "install_solar"),
                             ("$1,000 - Change Paint", "change_paint"),
                             ("$25,000 - Add Addition", "add_addition"),
                             ]
        self.turn = 1

    def spend_money(self, cost):
        new_balance = self.balance-cost
        if new_balance < 0:
            print("Not enough money! Save some first.")
            raise Exception
        self.balance = new_balance

    def do_event(self, event):
        try:
            method = getattr(self, event)
            method()
        except:
            return
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
        self.spend_money(10000)
        self.house.value += 8000
        self.visualizations.append(("solar-panel.png", [500,275], [75,100]))

    def change_paint(self):
        self.spend_money(1000)
        self.house.value *= 1.02
        self.visualizations.append(("solar-panel.png", [120, 120], [100,100]))

    def add_addition(self):
        self.spend_money(25000)
        self.house.value += 20000
        self.visualizations.append(("addition.png", [285, 393], [150,150]))

    # repairs
    def fix_leak(self):
        self.spend_money(10000)
        self.house.value += 10000
        self.visualizations.remove(self.leak)

    def fix_smash(self):
        self.spend_money(500)
        self.house.value += 500
        self.visualizations.remove(self.smash)

    def fix_splat(self):
        self.spend_money(5000)
        self.house.value += 5000
        self.visualizations.remove(self.splat)

    def end_turn(self):
        self.house.value *= 1.01
        self.balance += 3000
        if self.turn == 2:
            self.repairs.append(("$ 10,000 - Fix Leak", "fix_leak"))
            self.visualizations.append(self.leak)
            self.house.value *= .60
        if self.turn == 3:
            self.repairs.append(("$500 - Fix Smash", "fix_smash"))
            self.visualizations.append(self.smash)
            self.house.value *= .80
        if self.turn == 5:
            self.repairs.append(("$5,000 - Fix Splat", "fix_splat"))
            self.visualizations.append(self.splat)
            self.house.value *= .90
        self.turn += 1


class Scene:
    font_large = 42
    font_medium = 30
    font_small = 24
    title = ''
    prompt = ''
    age = ''
    background = 'background_image.png'

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
            image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(image, [0, 0])
        title = self.font_l.render(self.title, True, WHITE)
        screen.blit(title, XY_TITLE)
        prompt = self.font_m.render(self.prompt, True, WHITE)
        screen.blit(prompt, XY_PROMPT)
        show_balance = self.font_m.render("Funds Available: $ "+str(self.gameobject.balance), True, GREEN)
        screen.blit(show_balance, XY_BALANCE)
        show_value = self.font_m.render("House Value: $ "+str(self.gameobject.house.value), True, YELLOW)
        screen.blit(show_value, XY_VALUE)
        show_value = self.font_s.render("Age: Q" + str(self.gameobject.turn), True, WHITE)
        screen.blit(show_value, [700,550])
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

