import copy
import math

import pygame

from pyNDL import NodePrefabs
from pyNDL.TextBox import TextBox

from pyNDL.Assets import images
from pyNDL.VariableAndFunction import Function, Variable
from pygame.constants import *

pygame.font.init()


class Button:
    def __init__(self, display, pos, size, on_pressed):
        self.display = display
        self.pos = pos
        self.size = size

        self._on_pressed = on_pressed

        self.parent_pos = (0, 0)

        self.center = True  # is the given position is the center or the top left of the button

        self._is_hovered = False

        self.click_check = True

    def frame(self, camera_delta, events, pos):
        self._is_hovered = self.is_hovered(pos)
        if self.click_check:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self._is_hovered:
                            self._on_pressed()
                            return False

        if self._is_hovered:
            self.blit_hovered()
        else:
            self.blit()
        return True

    def blit(self):
        pass

    def blit_hovered(self):
        self.blit()

    def is_hovered(self, mouse_pos):
        if self.center:
            if self.pos[0] - self.size[0] / 2 <= mouse_pos[0] - self.parent_pos[0] <= self.pos[0] + self.size[0] / 2 and \
                    self.pos[1] - self.size[
                1] / 2 <= mouse_pos[1] - self.parent_pos[1] <= self.pos[1] + \
                    self.size[1] / 2:
                return True
        else:
            if self.pos[0] <= mouse_pos[0] - self.parent_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= \
                    mouse_pos[1] - self.parent_pos[1] <= self.pos[1] + self.size[1]:
                return True
        return False

    def get_hovered_image(self, original):
        image = copy.copy(original)
        arr = pygame.surfarray.pixels3d(image)
        arr //= 2
        del arr
        return image

    def get_hovered_color(self, color):
        n = 0.8
        return color[0] * n, color[1] * n, color[2] * n


class GoBackButton(Button):
    def __init__(self, pyNDL, display, pos):
        super().__init__(display, pos, (50, 37), self.on_pressed)
        self.pyNDL = pyNDL

        self.go_back_arrow = images["go_back_arrow"]
        self.go_back_arrow = pygame.transform.scale(self.go_back_arrow, self.size)

        self.go_back_arrow_hovered = self.get_hovered_image(self.go_back_arrow)

        self.center = False

    def blit(self):
        self.display.blit(self.go_back_arrow, self.pos)

    def blit_hovered(self):
        self.display.blit(self.go_back_arrow_hovered, self.pos)

    def on_pressed(self):
        self.pyNDL.go_back()


class NameSetter:
    BACKGROUND_COLOR = (25, 25, 25)
    title_font = pygame.font.SysFont('arial', 18)

    def __init__(self, pyNDL, display, pin):
        self.display = display
        self.size = (350, 55)
        self.pos = None
        # (self.display.get_size()[0] / 2 - self.size[0]/2, self.display.get_size()[1] / 2 - self.size[1]/2)

        self.text_box = TextBox(self.display, self.on_changed, size=(self.size[0], 40))

        self.pin = pin

        self.pyNDL = pyNDL
        self.pyNDL.set_focus_blocked(True)

    def frame(self, camera_delta, events, pos):
        if self.pos is None:
            self.pos = pos
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, 0, 5)  # Background
        title = self.title_font.render("Set Name", True, (255, 255, 255))
        self.display.blit(title, (self.pos[0] + self.size[0] / 2 - title.get_rect().width / 2, self.pos[1] + 10))
        self.text_box.pos = (self.pos[0], self.pos[1] + title.get_rect().height + 20)
        self.text_box.frame(camera_delta, events, pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    if not self.is_hovered(pos):
                        self.disable()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.disable()

    def on_changed(self):
        pass

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

    def disable(self):
        if self.text_box.text != "":
            self.pin.name = self.text_box.text
        self.pin.node.function.add_input(self.pin.name)
        self.pin.node.outputs[self.pin.name] = self.pin
        self.pin.node.calculate_size()
        self.pyNDL.set_focus_blocked(False)
        self.pyNDL.gui_components.remove(self)
        del self


class ScrollView:

    def __init__(self, display, pos, size):
        self.main_display = display
        self.display = pygame.Surface(size)

        self.pos = pos
        self.size = size

        self.items = []
        self.height = 0

        self.y_delta = 0

        self.background_color = (25, 25, 25)

    def frame(self, camera_delta, events, pos):
        rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.background_color, rect, 0, 0)  # Background

        if self.is_hovered(pos):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.y_delta += 5
                        if self.y_delta > 0:
                            self.y_delta = 0
                    elif event.button == 5:
                        self.y_delta -= 5
        current_y_pos = 0
        for i, item in enumerate(self.items):
            item.parent_pos = self.pos
            item.pos = (0, current_y_pos + self.y_delta)
            item.delta_pos = self.pos
            if item.is_hovered(pos):
                item.hovered = True
            else:
                item.hovered = False
            current_y_pos += item.size[1]
            item.frame(camera_delta, events, pos)

        self.main_display.blit(pygame.transform.scale(self.display, self.size), self.pos)

        return True

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

    def calculate_height(self):
        height = 0
        for item in self.items:
            height += item.size[1]
        self.height = height

    def set_items(self, items):
        self.items = items
        self.calculate_height()


def get_pos_with_delta(delta, pos):
    return pos[0] + delta[0], pos[1] + delta[1]


class Selector:
    BACKGROUND_COLOR = (18, 18, 18)
    title_font = pygame.font.SysFont('arial', 20)

    def __init__(self, display, pos, size, hint, items, viewer, create_viewer=None, pyNDL=None):
        self.pyNDL = pyNDL

        self.display = display

        self.size = size

        self.pos = pos

        self.is_visible = True

        self.text_box = TextBox(self.display, self.on_changed, size=(self.size[0], 40))
        self.text_box.hint = hint

        self.text_box.is_active = False

        self.scroll_view = ScrollView(self.display, (0, 0), (self.size[0], self.size[1] - self.text_box.size[1]))

        self.items = items

        self.viewer = viewer
        self.create_viewer = create_viewer

        self.scroll_view.pos = (self.pos[0], self.pos[1] + self.text_box.size[1])
        self.search()

        self.skip_next = False  # Skips the next frame to prevent bugs

        self._start_pos = None
        self._current_viewer = None

    def frame(self, camera_delta, events, pos):
        if self.is_visible:
            rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, 0, 5)  # Background

            self.text_box.pos = (self.pos[0], self.pos[1])
            self.text_box.frame(camera_delta, events, pos)

            self.scroll_view.frame(camera_delta, events, pos)

            if not self.skip_next:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if self.is_hovered(pos):
                                for viewer in self.scroll_view.items:
                                    if viewer.is_hovered(pos):
                                        self._start_pos = pos
                                        self._current_viewer = viewer
                            else:
                                self.on_unfocus()
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self._start_pos:
                            if math.sqrt((self._start_pos[0] - pos[0]) ** 2 + (self._start_pos[1] - pos[1]) ** 2) < 15:
                                self.on_clicked(self._current_viewer)
                                self.search()

                        self._start_pos = None
                        self.on_end_drag(self._current_viewer)
                        self._current_viewer = None

                if self._start_pos:
                    if math.sqrt((self._start_pos[0] - pos[0]) ** 2 + (self._start_pos[1] - pos[1]) ** 2) >= 15:
                        self.on_drag(self._current_viewer, camera_delta, pos)
            else:
                self.skip_next = False

    def on_changed(self):
        self.search()

    def search(self):
        viewers = []
        item_names = set()
        text = self.text_box.text.lower()
        for item in self.items:
            if item.name.lower().find(text) != -1:
                func_viewer = self.viewer(self.pyNDL, self.scroll_view.display, item, size=(self.size[0], 40), pos=(0, 0),
                                          delta_pos=self.scroll_view.pos)

                if item.name.lower() == self.text_box.text.lower():
                    viewers.insert(0, func_viewer)
                else:
                    viewers.append(func_viewer)
                item_names.add(item.name)
        if self.text_box.text != "" and self.text_box.text not in item_names:
            if self.create_viewer:
                viewers.insert(0,
                               self.create_viewer(self.pyNDL, self.scroll_view.display, size=(self.size[0], 40),
                                                  delta_pos=self.scroll_view.pos))
        self.scroll_view.set_items(viewers)

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False

    def disable(self):
        self.pyNDL.set_focus_blocked(False)
        self.pyNDL.gui_components.remove(self)
        del self

    def on_clicked(self, viewer):
        pass

    def on_drag(self, viewer, camera_delta, mouse_pos):
        pass

    def on_end_drag(self, viewer):
        pass

    def on_unfocus(self):
        pass

    def update(self):
        if self.pos != self.scroll_view.pos or self.size != self.scroll_view.size:
            self.scroll_view = ScrollView(self.display, (0, 0), (self.size[0], self.size[1] - self.text_box.size[1]))
            self.scroll_view.pos = (self.pos[0], self.pos[1] + self.text_box.size[1])
        self.search()


class FunctionSelector(Selector):
    def __init__(self, pyNDL, display, pos, size):
        super().__init__(display, pos, size, "Select a function", pyNDL.data.functions,
                         FunctionViewer, create_viewer=CreateFunction, pyNDL=pyNDL)

        self.current_moving_func = None

    def on_clicked(self, viewer):
        if type(viewer) == CreateFunction:
            new_func = Function(self.text_box.text)
            self.pyNDL.add_function(new_func)
        else:
            viewer.on_open()
        self.text_box.text = ""
        self.current_moving_func = None

    def on_drag(self, viewer, camera_delta, mouse_pos):
        if isinstance(viewer, CreateFunction):
            return
        if not self.current_moving_func:
            from pyNDL.Prefabs import VarAndFunc
            func = self.pyNDL.add_node(VarAndFunc.Func(), mouse_pos)
            func.on_function_change(viewer.function)
            self.current_moving_func = func
            self.pyNDL.is_object_moving = True
        else:
            self.current_moving_func.pos = get_pos_with_delta(camera_delta, mouse_pos)

    def on_end_drag(self, viewer):
        self.current_moving_func = None


class Viewer:
    FOCUSED_COLOR = (25, 25, 25)
    main_font = pygame.font.SysFont('arial', 15)

    def __init__(self, pyNDL, display, pos, delta_pos, size):
        self.pyNDL = pyNDL

        self.display = display
        self.pos = pos
        self.delta_pos = delta_pos
        self.size = size

        self.hovered = False

        self.text = "Empty Viewer"

        self.parent_pos = (0, 0)

        self.show_delete_btn = True
        self.delete_button = DeleteButton(self.display, self.pos, (15, 15), self.on_delete)

    def frame(self, camera_delta, events, pos):
        if self.hovered:
            rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            pygame.draw.rect(self.display, self.FOCUSED_COLOR, rect, 0, 1)  # Background

        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, (50,50, 50), rect, 1, 1)

        text = self.main_font.render(self.text, True, (255, 255, 255))
        self.display.blit(text, (self.pos[0] + 10, self.pos[1] + self.size[1] / 2 - text.get_rect().height / 2))

        if self.show_delete_btn:
            if self.delete_button:
                self.delete_button.pos = (self.pos[0] + self.size[0] - 30, self.pos[1] + self.size[1] / 2)
                self.delete_button.parent_pos = self.parent_pos
                self.delete_button.frame(camera_delta, events, pos)

    def is_hovered(self, mouse_pos):
        if self.pos[0] + self.delta_pos[0] <= mouse_pos[0] <= self.pos[0] + self.delta_pos[0] + self.size[0] and \
                self.pos[1] + self.delta_pos[1] <= mouse_pos[1] <= self.pos[1] + self.delta_pos[1] + \
                self.size[1]:
            return True
        return False

    def on_delete(self):
        pass


class CreateFunction(Viewer):

    def __init__(self, pyNDL, display, pos=(0, 0), delta_pos=(0, 0), size=(0, 0)):
        super().__init__(pyNDL, display, pos, delta_pos, size)
        self.text = "Create new function"
        self.show_delete_btn = False


class FunctionViewer(Viewer):

    def __init__(self, pyNDL, display, function, pos=(0, 0), delta_pos=(0, 0), size=(0, 0)):
        super().__init__(pyNDL, display, pos, delta_pos, size)
        self.function = function
        self.text = self.function.name
        self._is_deleted = False

    def frame(self, camera_delta, events, pos):
        super().frame(camera_delta, events, pos)

    def on_delete(self):
        self.pyNDL.delete_function(self.function)
        self._is_deleted = True

    def on_open(self):
        if not self._is_deleted:
            self.pyNDL.open_function(self.function)


class VariableSelector(Selector):
    def __init__(self, pyNDL, display, pos, size, is_local=False):
        super().__init__(display, pos, size,
                         "Select a local variable" if is_local else "Select a variable",
                         pyNDL.data.variables if is_local else pyNDL.get_main_data().variables,
                         VariableViewer, create_viewer=CreateVariable, pyNDL=pyNDL)

        self.is_local = is_local

        self.current_moving_var = None

    def update_items(self):
        self.items = self.pyNDL.data.variables if self.is_local else self.pyNDL.get_main_data().variables
        self.search()

    def on_clicked(self, viewer):
        if type(viewer) == CreateVariable:
            new_variable = Variable(self.text_box.text)
            self.pyNDL.add_variable(new_variable, is_local=self.is_local)
        self.text_box.text = ""
        self.current_moving_var = None

    def on_drag(self, viewer, camera_delta, mouse_pos):
        if isinstance(viewer, CreateVariable):
            return
        if not self.current_moving_var:
            keys = pygame.key.get_pressed()
            var = None
            if keys[pygame.K_LALT]:
                if viewer.variable.custom_set:
                    var = viewer.variable.custom_set()
                else:
                    var = NodePrefabs.SetVariable()
            else:
                if viewer.variable.custom_get:
                    var = viewer.variable.custom_get()
                else:
                    var = NodePrefabs.GetVariable()
            var = self.pyNDL.add_node(var, mouse_pos)
            var.on_variable_change(viewer.variable)
            self.current_moving_var = var
            self.pyNDL.is_object_moving = True
        else:
            self.current_moving_var.pos = get_pos_with_delta(camera_delta, mouse_pos)

    def on_end_drag(self, viewer):
        self.current_moving_var = None


class VariableViewer(Viewer):

    def __init__(self, pyNDL, display, variable, pos=(0, 0), delta_pos=(0, 0), size=(0, 0), is_local=False):
        super().__init__(pyNDL, display, pos, delta_pos, size)
        self.variable = variable
        self.text = self.variable.name
        self.is_local = is_local

    def on_delete(self):
        self.pyNDL.delete_variable(self.variable, is_local=self.is_local)


class CreateVariable(Viewer):

    def __init__(self, pyNDL, display, pos=(0, 0), delta_pos=(0, 0), size=(0, 0)):
        super().__init__(pyNDL, display, pos, delta_pos, size)
        self.text = "Create new variable"
        self.show_delete_btn = False


class TopBar:
    BACKGROUND_COLOR = (18, 18, 18)

    def __init__(self, pyNDL, display, pos, size):
        self.pyNDL = pyNDL
        self.display = display
        self.pos = pos
        self.size = size

        self.gui_components = [StartButton(self.pyNDL, self.display, (self.pos[0] + 10, self.pos[1] + 5))]

    def frame(self, camera_delta, events, pos):
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, 0)  # Background

        for gui_component in self.gui_components:
            gui_component.frame(camera_delta, events, pos)


class LeftBar:
    BACKGROUND_COLOR = (18, 18, 18)

    def __init__(self, pyNDL, display, pos, size):

        self.pyNDL = pyNDL

        self.display = display
        self.pos = pos
        self.size = size

        self.function_selector = FunctionSelector(self.pyNDL, self.display, pos=self.pos,
                                                  size=(self.size[0], self.size[1] / 2))
        self.variable_selector = VariableSelector(self.pyNDL, self.display,
                                                  pos=(self.pos[0], self.pos[1] + self.function_selector.size[1]),
                                                  size=(self.size[0], self.size[1] / 2))

        self.local_variable_selector = VariableSelector(self.pyNDL, self.display,
                                                        pos=(self.pos[0], self.pos[1] + self.function_selector.size[1] +
                                                             self.variable_selector.size[1] / 2),
                                                        size=(self.size[0], self.size[1] / 4), is_local=True)

        self.gui_components = [self.function_selector, self.variable_selector]

    def frame(self, camera_delta, events, pos):
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, 0)  # Background

        for gui_component in self.gui_components:
            gui_component.frame(camera_delta, events, pos)

    def update(self):
        if self.pyNDL.is_in_function:
            if self.local_variable_selector not in self.gui_components:
                self.gui_components.append(self.local_variable_selector)
                self.local_variable_selector.update_items()
                self.local_variable_selector.skip_next = True
                self.variable_selector.size = (self.variable_selector.size[0], self.size[1] / 4)
                self.variable_selector.update()
        else:
            if self.local_variable_selector in self.gui_components:
                self.gui_components.remove(self.local_variable_selector)
                self.variable_selector.size = (self.variable_selector.size[0], self.size[1] / 2)
                self.variable_selector.update()

        self.variable_selector.search()
        self.variable_selector.skip_next = True
        self.function_selector.search()
        self.function_selector.skip_next = True


class DeleteButton(Button):
    def __init__(self, display, pos, size, on_pressed):
        super().__init__(display, pos, size, on_pressed)
        self.color = (99, 99, 99)
        self.cross = images["cross"]
        self.cross = pygame.transform.scale(self.cross, self.size)

        self.cross_hovered = self.get_hovered_image(self.cross)

    def blit(self):
        self.display.blit(self.cross, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))

    def blit_hovered(self):
        self.display.blit(self.cross_hovered, (self.pos[0] - self.size[0] / 2, self.pos[1] - self.size[1] / 2))


class AddItemButton(Button):
    def __init__(self, display, pos, size, mother_class):
        super().__init__(display, pos, size, self.on_btn_pressed)
        self.color = (150, 150, 150)
        self.mother_class = mother_class

        self.click_check = False

    def blit(self):
        self._blit(self.color)

    def blit_hovered(self):
        self._blit(self.get_hovered_color(self.color))

    def _blit(self, color):
        pygame.draw.line(self.display, color, (self.pos[0], self.pos[1] - self.size[1] / 2),
                         (self.pos[0], self.pos[1] + self.size[1] / 2), 3)
        pygame.draw.line(self.display, color, (self.pos[0] + self.size[0] / 2, self.pos[1]),
                         (self.pos[0] - self.size[0] / 2, self.pos[1]), 3)

    def on_btn_pressed(self):
        self.mother_class.on_add_item_btn_pressed()


class StartButton(Button):
    def __init__(self, pyNDL, display, pos):
        super().__init__(display, pos, (20, 30), self.on_btn_pressed)
        self.pyNDL = pyNDL

    def blit(self):
        pygame.draw.polygon(self.display, (46, 163, 77),
                            [self.pos, (self.pos[0] + self.size[0], self.pos[1] + self.size[1] / 2),
                             (self.pos[0], self.pos[1] + self.size[1])])

    def blit_hovered(self):
        pygame.draw.polygon(self.display, self.get_hovered_color((46, 163, 77)),
                            [self.pos, (self.pos[0] + self.size[0], self.pos[1] + self.size[1] / 2),
                             (self.pos[0], self.pos[1] + self.size[1])])

    def on_btn_pressed(self):
        self.pyNDL.start()

    def is_hovered(self, mouse_pos):
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] <= self.pos[1] + \
                self.size[1]:
            return True
        return False


class KeyPicker(Selector):
    def __init__(self, display, pos, size):
        keys = []
        for name, val in globals().items():
            if name.startswith("K_"):
                keys.append(key(name[2::], val))

        super().__init__(display, pos, size, "Choose a key", keys, KeyViewer)
        self.text_box.is_active = True
        self.is_visible = False
        self.current_text_box = None

    def on_clicked(self, viewer):
        self.is_visible = False
        self.current_text_box.value = viewer.key.key
        self.current_text_box.set_text(viewer.text)

    def set_active(self, text_box):
        self.is_visible = True
        self.text_box.set_text("")
        self.current_text_box = text_box
        self.skip_next = True

    def on_unfocus(self):
        self.is_visible = False


class KeyViewer(Viewer):
    def __init__(self, pyNDL, display, item, pos=(0, 0), delta_pos=(0, 0), size=(0, 0)):
        super().__init__(pyNDL, display, pos, delta_pos, size)
        self.key = item
        self.text = self.key.name
        self.show_delete_btn = False


class key:
    def __init__(self, name, key):
        self.name = name
        self.key = key
