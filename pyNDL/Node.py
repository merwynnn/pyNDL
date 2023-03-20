import inspect
import math
import copy

from NodalLanguage import Components
from NodalLanguage.Pin import *

pygame.font.init()

title_size = 17
small_text_size = 15
title_font = pygame.font.SysFont('arial', title_size)
small_font = pygame.font.SysFont('arial', small_text_size)


class Node:
    BACKGROUND_COLOR = (53, 53, 54)
    EVENT_COLOR = (199, 50, 50)
    SELECTED_COLOR = (245, 229, 86)
    INPUT_HOVERED_COLOR = (105, 105, 105)
    DELTA = 5  # Distance between inputs and outputs
    D = 10  # Distance between title and inputs or outputs

    def __init__(self):

        self.inputs = {}
        self.outputs = {}

        self.name = "Node"
        self.pos = (0, 0)
        self.size = (0, 0)  # Width, Height

        self.compact = False
        self.show_name = True

        self.name_size = 0  # Name size if show_name is False

        self.is_selected = False

        self.is_event = False

        self.nodalLanguage = None

        self.display = None

        self.is_deletable = True
        self.is_visible_on_search = True

        self.add_input_btn = False
        self.add_item_btn = None

        self.initial_pos_on_move = (0, 0)  # Used when moving a node
        self.visibility_delta = 40
        self.stashed_inputs = {}        # Inputs that will be added next frame
        self.to_be_removed_inputs = []  # Inputs that will be removed next frame

        self.unpickle_vars = []  # Variables to unpickle to prevent pickling surfaces or unwanted objects

        self.imports = []       # Library to import
        self.custom_vars = []

    def setNodalLanguage(self, nodalLanguage):
        self.nodalLanguage = nodalLanguage
        self.display = self.nodalLanguage.display
        self.add_item_btn = Components.AddItemButton(self.display, (0, 0), (10, 10), self)
        self.add_item_btn.display = self.display
        self.calculate_size()

        for input in self.inputs.values():
            input.set_text_box()

    def frame(self, camera_delta, events, mouse_pos):
        pos = self.get_pos_with_delta(self.pos, camera_delta)
        y_delta = 0 if self.compact else small_text_size + self.D
        if self.is_on_screen(pos, self.visibility_delta) or self.is_on_screen((pos[0] + self.size[0], pos[1]), self.visibility_delta) or self.is_on_screen(
                (pos[0] + self.size[0], pos[1] + self.size[1]), self.visibility_delta) or self.is_on_screen((pos[0], pos[1] + self.size[1]), self.visibility_delta):
            rect = pygame.Rect(pos[0], pos[1], self.size[0], self.size[1])
            pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, 0, 10)

            name = title_font.render(self.name, True, (255, 255, 255))

            if self.is_event:
                rect = pygame.Rect(pos[0], pos[1], self.size[0], name.get_rect().height + self.D / 2 - 4)
                pygame.draw.rect(self.display, self.EVENT_COLOR, rect, 0, border_top_right_radius=10,
                                 border_top_left_radius=10)

            if self.is_selected:
                rect = pygame.Rect(pos[0], pos[1], self.size[0], self.size[1])
                pygame.draw.rect(self.display, self.SELECTED_COLOR, rect, 1, 10)

            y_delta = self.D

            if self.compact:
                if self.show_name:
                    if len(self.inputs.values()) == 0:
                        self.display.blit(name, (pos[0] + self.size[1] / 2 - name.get_rect().width / 2,
                                                 pos[1] + self.size[1] / 2 - name.get_rect().height / 2))
                    else:
                        self.display.blit(name, (pos[0] + self.size[0] / 2 - name.get_rect().width / 2,
                                                 pos[1] + self.size[1] / 2 - name.get_rect().height / 2))
            else:
                if self.show_name:
                    self.display.blit(name, (pos[0] + self.size[0] / 2 - name.get_rect().width / 2, pos[1]))
                y_delta = name.get_rect().height + self.D

            if self.add_input_btn:
                self.add_item_btn.pos = (
                    pos[0] + 12, pos[1] + self.size[1] - self.D - 3)
                self.add_item_btn.frame(camera_delta, events, mouse_pos)

                if self.add_item_btn._is_hovered:
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                self.on_add_item_btn_pressed()

        l = len(self.inputs.values())
        for i, input in enumerate(self.inputs.values()):
            y = 0
            if self.compact:
                if l % 2 == 0:
                    y = (pos[1] + self.size[1] / 2) - self.DELTA / 2 - (
                            self.DELTA + small_text_size) * l / 4 + i * (self.DELTA + small_text_size)
                else:
                    y = (pos[1] + self.size[1] / 2) - (self.DELTA + small_text_size) * (l // 2) + i * (
                            self.DELTA + small_text_size)
            else:
                y = pos[1] + y_delta + i * (small_text_size + self.DELTA) + input.radius

            input.pos = (pos[0] + 10 + input.radius / 2, y)

            input.frame(camera_delta, events, mouse_pos)

        l = len(self.outputs.values())
        for i, output in enumerate(self.outputs.values()):
            y = 0
            if self.compact:
                if l % 2 == 0:
                    y = (pos[1] + self.size[1] / 2) - self.DELTA / 2 - (
                            self.DELTA + small_text_size) * l / 4 + i * (self.DELTA + small_text_size)
                else:
                    y = (pos[1] + self.size[1] / 2) - (self.DELTA + small_text_size) * (l // 2) + i * (
                            self.DELTA + small_text_size)
            else:
                y = pos[1] + y_delta + i * (small_text_size + self.DELTA) + output.radius

            output.pos = (pos[0] + self.size[0] - 10 - output.radius / 2, y)

            output.frame(camera_delta, events, mouse_pos)

        if self.stashed_inputs:
            self.inputs.update(self.stashed_inputs)
            self.stashed_inputs = {}
            self.calculate_size()

        for name in self.to_be_removed_inputs:
            del self.inputs[name]
        self.to_be_removed_inputs = []

    def calculate_size(self):
        if self.compact:
            height = max((len(self.inputs.values()), len(self.outputs.values()))) * (
                    small_text_size + self.DELTA) + self.D
        else:
            height = max((len(self.inputs.values()), len(self.outputs.values()))) * (
                    small_text_size + self.DELTA) + title_size + self.D
        if self.add_input_btn:
            height += self.add_item_btn.size[1] + self.DELTA * 2
            pass

        if self.compact:
            width = (max([len(i.name) + 3 for i in self.inputs.values()] + [0]) + max(
                [len(i.name) for i in self.outputs.values()] + [0])) * small_text_size + (
                        len(self.name) if self.show_name else self.name_size) * small_text_size + 20
        else:
            width = max((max([len(i.name) + 3 for i in self.inputs.values()] + [0]) + max(
                [len(i.name) + 1 for i in self.outputs.values()] + [0])) * small_text_size,
                        len(self.name) * small_text_size)

        self.size = (width, height)
        return width, height

    def is_on_screen(self, pos, delta):
        if -delta <= pos[0] <= self.display.get_width()+delta and -delta <= pos[1] <= self.display.get_height()+delta:
            return True
        return False

    def get_pos_with_delta(self, pos, delta):
        return pos[0] - delta[0], pos[1] - delta[1]

    def is_hovered(self, mouse_pos_raw, delta):
        pos = self.get_pos_with_delta(self.pos, delta)
        if pos[0] <= mouse_pos_raw[0] <= pos[0] + self.size[0] and pos[1] <= mouse_pos_raw[1] <= pos[1] + self.size[1]:
            return True
        return False

    def get_hovered_pin(self, mouse_pos_raw):
        for input in self.inputs.values():
            if math.sqrt((mouse_pos_raw[0] - input.pos[0]) ** 2 + (
                    mouse_pos_raw[1] - input.pos[1]) ** 2) <= input.radius:
                return input

        for output in self.outputs.values():
            if math.sqrt((mouse_pos_raw[0] - output.pos[0]) ** 2 + (
                    mouse_pos_raw[1] - output.pos[1]) ** 2) <= output.radius:
                return output

        return None

    def on_pin_connect(self, pin):
        pass

    def on_pin_disconnect(self, pin):
        pass

    def on_pin_delete(self, pin):
        pass

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        memo = {-1: result}
        result.inputs = copy.deepcopy(self.inputs, memo)
        result.outputs = copy.deepcopy(self.outputs, memo)
        return result

    def delete(self):
        for output in self.outputs.values():
            output.disconnect(all_pin=True)

        for input in self.inputs.values():
            input.disconnect(all_pin=True)

        del self

    def func(self):
        pass

    def execute(self):
        self.func()

    def activate_add_input_btn(self):
        self.add_input_btn = True

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle display
        try:
            del state["display"]
            del state["nodalLanguage"]
            del state["add_item_btn"]
            for var in self.unpickle_vars:
                del state[var]
        except KeyError:
            pass
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.is_selected = False

    def on_add_item_btn_pressed(self):
        pass

    def get_center(self):
        return self.pos[0] + self.size[0] / 2, self.pos[1] + self.size[1] / 2

    def add_input_runtime(self, input, name):
        """ Used when adding a new input at runtime. Only adds the input at the end of the current frame"""
        input.set_text_box()
        self.stashed_inputs[name] = input

    def remove_input_runtime(self, name):
        """ Used when removing a new input at runtime. Only removes the input at the end of the current frame"""
        self.to_be_removed_inputs.append(name)

    def on_load(self):
        pass

    def get_func(self, split=False):
        func = inspect.getsource(self.func)  # Returns the function func in string format
        func = func.replace("   def func(self):\n", '')
        func = func[:-1]

        lines_obj = []

        # Unindent
        lines = func.split("\n")
        for i, line in enumerate(lines):
            for _ in range(2):
                if lines[i][0:4] == "    ":
                    lines[i] = lines[i][4:]
            if lines[i][0] == " " and lines[i][1] != " ":
                lines[i] = lines[i][1:]
            if split:
                lines_obj.append(Line(lines[i]))

        func = "\n".join(lines)

        if split:
            return lines_obj

        return func

    def add_import(self, name):
        self.imports.append(name)


class NodePrefab:
    pass


class ImpureNode(Node):
    def __init__(self):
        super().__init__()
        self.inputs = {"Exec": Input("", self, is_execution_pin=True)}
        self.outputs = {"Exec": Output("", self, is_execution_pin=True)}

    def execute(self):
        self.func()
        self.outputs["Exec"].execute()


class EndingNode(Node):
    def __init__(self):
        super().__init__()
        self.inputs = {"Exec": Input("", self, is_execution_pin=True)}

    def execute(self):
        self.func()


class PureNode(Node):
    def __init__(self):
        super().__init__()


class Event(Node):
    instances = []

    def __init__(self):
        super().__init__()
        Event.instances.append(self)
        self.is_event = True
        self.outputs = {"Exec": Output("", self, is_execution_pin=True)}

    def execute(self):
        self.func()
        self.outputs["Exec"].execute()


class Line:
    def __init__(self, line):
        self.line = line
        self.delta = 0

    def get_increments(self):
        i = 0
        line = self.line
        while True:
            if line[:4] == "    ":
                i += 1
                line = line[4:]
            else:
                return i

    def set_increments(self, nb):
        # Removes increments
        line = self.line
        while True:
            if line[:4] == "    ":
                line = line[4:]
            else:
                break

        for _ in range(nb):
            line = "    " + line

        self.line = line
