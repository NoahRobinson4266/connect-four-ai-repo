import pygame

colour1 = (0, 0, 0)
colour2 = (80, 80, 80)
colour3 = (150, 150, 150)
colour4 = (255, 255, 255)

pygame.init()


class Text:
    def __init__(self, x_pos, y_pos, text, colour=colour1, font="roboto", font_size=20, code="", is_centred=True):
        self.x = x_pos
        self.y = y_pos

        self.code = code
        self.text = text
        self.font = pygame.font.SysFont(font, int(font_size), True)
        self.colour = colour

        self.centred = is_centred

    def draw(self, win):

        text = self.font.render(self.text, True, self.colour)

        x_pos = self.x
        y_pos = self.y

        if self.centred:
            x_pos -= text.get_width() / 2
            y_pos -= text.get_height() / 2

        win.blit(text, (x_pos, y_pos))


class Button:
    def __init__(self, x_pos, y_pos, width, height, code, text, start_colour=colour1, hover_colour=colour2,
                 select_colour=colour3, text_colour=colour4, font="roboto", font_size=20, is_centred=True):
        self.x = x_pos
        self.y = y_pos
        self.w = width
        self.h = height

        if is_centred:
            self.x -= self.w / 2
            self.y -= self.h / 2

        self.code = code
        self.text = text
        self.font = pygame.font.SysFont(font, int(font_size), True)
        self.start_colour = start_colour
        self.hover_colour = hover_colour
        self.text_colour = text_colour
        self.select_colour = select_colour

    def draw(self, win, mouse_pos, is_clicking):

        draw_colour = self.start_colour
        if self.x < mouse_pos[0] < self.x + self.w:
            if self.y < mouse_pos[1] < self.y + self.h:
                draw_colour = self.hover_colour

                if is_clicking:
                    draw_colour = self.select_colour

        text = self.font.render(self.text, True, self.text_colour)

        pygame.draw.rect(win, draw_colour, (self.x, self.y, self.w, self.h))
        win.blit(text, ((self.x + self.w / 2) - text.get_width() / 2, (self.y + self.h / 2) - text.get_height() / 2))


class TextBox:

    def __init__(self, x_pos, y_pos, width, height, colour=colour1, text_colour=colour4,
                 font="roboto", font_size=60):
        self.x = x_pos
        self.y = y_pos
        self.w = width
        self.h = height

        self.text = ""
        self.font = pygame.font.SysFont(font, int(font_size), True)
        self.colour = colour
        self.text_colour = text_colour

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.w, self.h))

        text = self.font.render(self.text, True, self.text_colour)
        win.blit(text, (self.x + 5, (self.y + self.h / 2) - text.get_height() / 2))
