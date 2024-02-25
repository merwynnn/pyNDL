import pygame

from pyNDL.Pin import Input, Output
from pyNDL.Rope import Rope
from pyNDL.TextBox import TextBox


class NodeSelector:
    BACKGROUND_COLOR = (25, 25, 25)

    def __init__(self, pyNDL, display, nodes):
        self.pyNDL = pyNDL
        self.display = display
        self.nodes = nodes

        self.isvisible = False
        self.pos = (0, 0)
        self.size = (350, 400)

        self.text_box = TextBox(self.display, self.search, size=(self.size[0], 40))

        self.node_pickers = []

        self.node_picker_height = 40
        self.result_amount = 9

        self.selected_row = 0

        self.current_pin = None

        self.search()

    def frame(self, camera_delta, events, pos):
        if self.isvisible:
            rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, width=0)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 or event.button == 3:
                        if self.is_hovered(pos):
                            for node_picker in self.node_pickers:
                                if node_picker.is_hovered(pos):
                                    # Add a new node on click
                                    self.add_node(node_picker.node)
                                    self.disable()
                        else:
                            self.disable()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(self.node_pickers) > 0:
                            # Add a new node on ENTER
                            self.add_node(self.node_pickers[self.selected_row].node)
                            self.disable()
                    if event.key == pygame.K_DOWN:
                        if self.selected_row < self.result_amount-1:
                            self.selected_row += 1
                    if event.key == pygame.K_UP:
                        if self.selected_row > 0:
                            self.selected_row -= 1

            if len(self.node_pickers) > 0:
                self.node_pickers[self.selected_row].hovered = True
            self.text_box.pos = self.pos
            self.text_box.frame(camera_delta, events, pos)

            for i, node_picker in enumerate(self.node_pickers):
                node_picker.pos = (self.pos[0], self.pos[1] + self.text_box.size[1] + i * self.node_picker_height)
                if node_picker.is_hovered(pos):
                    node_picker.hovered = True
                elif i != self.selected_row:
                    node_picker.hovered = False
                node_picker.draw(pos)

    def add_node(self, node):
        new_node = self.pyNDL.add_node(node, self.pos)
        if self.current_pin is not None:
            if type(self.current_pin) is Input:
                for output in new_node.outputs.values():
                    if output.is_execution_pin == self.current_pin.is_execution_pin:
                        rope = Rope(self.display)
                        self.pyNDL.connect_pins(self.current_pin, output, rope)
                        return
            elif type(self.current_pin) is Output:
                for input_ in new_node.inputs.values():
                    if input_.is_execution_pin == self.current_pin.is_execution_pin:
                        rope = Rope(self.display)
                        self.pyNDL.connect_pins(input_, self.current_pin, rope)
                        return

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

    def search(self):
        self.node_pickers = []
        self.selected_row = 0
        text = self.text_box.text.lower()
        index = 0
        for node in self.nodes:
            if node.is_visible_on_search:
                if node.name.lower().find(text) != -1:
                    node_picker = NodePicker(self.display, node, size=(self.size[0], self.node_picker_height))
                    if node.name.lower() == self.text_box.text.lower():
                        self.node_pickers.insert(0, node_picker)
                    else:
                        self.node_pickers.append(node_picker)

                    index += 1
                if index == self.result_amount:
                    return

    def enable(self, current_pin = False):
        if current_pin is not False:
            self.current_pin = current_pin
        self.isvisible = True
        self.pyNDL.focus_blocked = True
        self.text_box.reset()
        self.node_pickers = []
        self.search()

    def disable(self):
        self.isvisible = False
        self.current_pin = None
        self.pyNDL.focus_blocked = False


class NodePicker:
    FOCUSED_COLOR = (35, 35, 35)
    main_font = pygame.font.SysFont('arial', 15)

    def __init__(self, display, node, pos=(0, 0), size=(0, 0)):
        self.display = display
        self.node = node
        self.pos = pos
        self.size = size

        self.hovered = False

    def draw(self, mouse_pos):
        if self.hovered:
            rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            pygame.draw.rect(self.display, self.FOCUSED_COLOR, rect, 0, 1)  # Background

        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, (0, 0, 0), rect, 1, 1)

        text = self.main_font.render(self.node.name, True, (255, 255, 255))
        self.display.blit(text, (self.pos[0] + 10, self.pos[1] + self.size[1] / 2 - text.get_rect().height / 2))

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

