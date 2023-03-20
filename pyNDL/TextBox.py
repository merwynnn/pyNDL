import pygame


class TextBox:
    INPUT_COLOR_ACTIVE = (45, 45, 45)
    INPUT_COLOR_PASSIVE = (31, 30, 30)

    def __init__(self, display, on_value_changed, pos=(0, 0), size=(0, 0), font_size=15, on_clicked = None, is_blocked=False, is_dropdown=False, dropdown=None):
        self.main_display = display
        self.display = pygame.Surface(size)

        self.pos = pos
        self.size = size

        self.is_dropdown = is_dropdown
        self.dropdown = dropdown
        self.parent = None
        self.current_dropdown = None

        self.delta_x = 0

        self.text = ""
        self.hint = ""
        self.value = None
        self.is_active = True
        self.is_blocked = is_blocked
        self.on_value_changed = on_value_changed
        self.on_clicked = on_clicked

        self.font_size = font_size

        self.main_font = pygame.font.SysFont('arial', self.font_size)

        self.forbidden_key = (pygame.K_DOWN, pygame.K_UP)

    def frame(self, camera_delta, events, pos):
        rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.INPUT_COLOR_ACTIVE if self.is_active else self.INPUT_COLOR_PASSIVE, rect, 0,
                         0)  # Input

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_hovered(pos):
                    if event.button == 1:
                        if not self.is_blocked:
                            if self.is_dropdown:
                                self.current_dropdown = self.dropdown(self.main_display, (self.pos[0], self.pos[1]+self.size[1]), (self.size[0]*3, 400))
                                self.current_dropdown.set_active(self)
                            else:
                                self.is_active = True
                        if self.on_clicked:
                            self.on_clicked()
                else:
                    self.is_active = False
            if event.type == pygame.KEYDOWN:
                if self.is_active:
                    if event.key == pygame.K_RETURN:
                        pass
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.on_value_changed()

                    elif event.key in self.forbidden_key:
                        pass
                    else:
                        self.text += event.unicode
                        self.on_value_changed()

        if len(self.text) == 0:
            text = self.main_font.render(self.hint, True, (86, 87, 87))
            d = 20
            self.display.blit(text, (20, self.size[1] / 2 - text.get_rect().height / 2))
        else:
            text = self.main_font.render(self.text, True, (255, 255, 255))
            d = 10
        self.display.blit(text, (d + self.delta_x, self.size[1] / 2 - text.get_rect().height / 2))

        if self.get_cursor_x(text.get_rect().width) >= self.size[0] - self.size[0] / 35:
            self.delta_x -= self.size[0] / 100
        elif text.get_rect().width < self.size[0] - self.size[0] / 35 and self.delta_x < 0:
            self.delta_x += self.size[0] / 50
        if self.is_active:
            rect = pygame.Rect(self.get_cursor_x(text.get_rect().width), 5, 2, self.size[1] - 10)
            pygame.draw.rect(self.display, (255, 255, 255), rect, 0,
                             5)

        if self.current_dropdown:
            self.current_dropdown.frame(camera_delta, events, pos)

        self.main_display.blit(pygame.transform.scale(self.display, self.size), self.pos)

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

    def get_cursor_x(self, text_size):
        return 10 + text_size + self.delta_x + 4 if len(self.text) != 0 else 14

    def reset(self):
        self.is_active = True
        self.text = ""

    def set_text(self, text):
        self.text = text
        self.on_value_changed()

