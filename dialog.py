import pygame
from pygame.locals import *
from pgu import gui


class EventDialog(gui.Dialog):
    def __init__(self, title = '', text_stream = ''):
        title = gui.Label(title)

        width = 400
        height = 200
        doc = gui.Document(width = width)

        space = title.style.font.size(" ")

        doc.block(align=-1)
        lines = text_stream.split('\n')
        for line in lines:
            for word in line.split(" "):
                doc.add(gui.Label(word))
                doc.space(space)
            doc.br(space[1])
        super().__init__(title, gui.ScrollArea(doc, width, height))


if __name__ == '__main__':
    app = gui.Desktop()
    app.connect(gui.QUIT, app.quit, None)

    c = gui.Table(width = 640, height = 480)

    dialog = EventDialog("test for ips", "This is a paragraph\nAnd this is another one\n")

    e = gui.Button("About")
    e.connect(gui.CLICK, dialog.open, None)

    c.tr()
    c.td(e)

    app.run(c)
