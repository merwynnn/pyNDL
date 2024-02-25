import copy

import pygame

from pyNDL.Colors import colors
from pyNDL.Rope import Rope
from pyNDL.TextBox import TextBox
pygame.font.init()

small_text_size = 15

small_font = pygame.font.SysFont('arial', small_text_size)


class Pin:
    INPUT_HOVERED_COLOR = (105, 105, 105)

    def __init__(self):
        self.is_input = None

        self.name = "Default Name"
        self.is_execution_pin = False

        self.connected_pin = None
        self.connected_pins = set()

        self.pos = (0, 0)
        self.node = None

        self.is_hovered = False

        self.radius = 5

        self.type = None
        self._original_type = self.type

        self.ropes = set()

        self.is_deletable = False

    def __getstate__(self):
        """ Called on save (pickled) to prevent unpickable object to cause an error """
        state = self.__dict__.copy()
        # Don't pickle display
        del state["ropes"]
        return state

    def __setstate__(self, state):
        """ Called on load data from file (unpickle) """
        self.__dict__.update(state)
        # Add pyNDL and display back since it doesn't exist in the pickle
        self.ropes = set()

    def execute(self):
        """ Executes the connected node function if there is one """
        if self.is_execution_pin:
            if self.connected_pin:
                self.connected_pin.node.execute()

    def clear_ropes(self):
        """ Clear all the ropes """
        for rope in self.ropes:
            rope.delete()
        self.ropes.clear()

    def draw_execution_pin(self, display, pin):
        points = [(pin.pos[0] - 4, pin.pos[1] - 5), (pin.pos[0], pin.pos[1] - 5),
                  (pin.pos[0] + 5, pin.pos[1]), (pin.pos[0], pin.pos[1] + 5),
                  (pin.pos[0] - 4, pin.pos[1] + 5)]
        pygame.draw.polygon(display, self.get_hovered_color((255, 255, 255)) if pin.is_hovered else (255, 255, 255),
                            points=points, width=0 if pin.connected_pin is not None else 2)

    def get_hovered_color(self, color):
        return (color[0] + self.INPUT_HOVERED_COLOR[0]) / 2, (color[1] + self.INPUT_HOVERED_COLOR[1]) / 2, (
                color[2] + self.INPUT_HOVERED_COLOR[2]) / 2

    def connect(self, pin):
        """ Connect to another pin """
        if self.is_input or self.is_execution_pin:
            self.connected_pin = pin
            if self.type is None:
                self.type = self.connected_pin.type
        else:
            self.connected_pins.add(pin)
            if self.type is None and len(self.connected_pins) == 1:
                e = next(iter(self.connected_pins))
                self.type = e.type
        self.node.on_pin_connect(self)

    def disconnect(self, pin=None, all_pin=False, r=False):
        """ Disconnect and remove all the ropes and connections """
        if self.is_input or self.is_execution_pin:
            if not r:
                if self.connected_pin:
                    self.connected_pin.disconnect(pin=self, r=True)
            self.clear_ropes()
            self.connected_pin = None
        else:
            if not r:
                if all_pin:
                    for p in self.connected_pins:
                        p.disconnect(self, r=True)
                    self.connected_pins.clear()
                else:
                    if pin:
                        self.connected_pins.discard(pin)
                        pin.disconnect(self, r=True)
            else:
                self.connected_pins.discard(pin)
            self.delete_rope(pin, self)
        self.type = self._original_type
        self.node.on_pin_disconnect(self)

    def delete_rope(self, input, output):
        for rope in self.ropes:
            if rope.input == input and rope.output == output:
                self.ropes.remove(rope)
                rope.delete()

                return

    def delete(self):
        """ Deletes the current pin """
        self.disconnect()
        for k, v in self.node.inputs.items():
            if v is self:
                del self.node.inputs[k]
                break
        for k, v in self.node.outputs.items():
            if v is self:
                del self.node.outputs[k]
                break
        self.node.calculate_size()
        self.node.on_pin_delete(self)
        del self


class Input(Pin):
    def __init__(self, name, node, is_execution_pin=False, default_value=0, ptype=int, is_deletable=False, show_text_box = True, text_box_width_mult = 1, is_dropdown = False, dropdown = None):
        super().__init__()
        self.is_input = True

        self.name = name
        self.node = node

        self.is_dropdown = is_dropdown
        self.dropdown = dropdown
        self.is_execution_pin = is_execution_pin

        self._value = default_value
        self._display_value = "0"      # Used when input is dropdown and stores the value displayed on the textbox
        self.type = ptype
        self._original_type = self.type

        self.show_text_box = show_text_box
        self.text_box = None
        self.text_box_width_mult = text_box_width_mult

        self.is_deletable = is_deletable

    def get_value(self):
        if not self.connected_pin:
            return self._value

        return self.connected_pin.stored_value

    def set_value(self, value):
        self._value = value

    def on_value_changed(self):
        last_value = self._value
        if not self.is_dropdown:
            try:
                self.value = eval(self.text_box.text)
            except (NameError, TypeError, SyntaxError):
                self.value = self.text_box.text
        else:
            self.value = self.text_box.value
            self._display_value = self.text_box.text
        if self._value != last_value:
            self.node.pyNDL.action()

    def frame(self, camera_delta, events, pos):
        input_name = small_font.render(self.name, True, (255, 255, 255))

        if self.is_execution_pin:
            self.draw_execution_pin(self.node.display, self)

        else:
            if not self.connected_pin and self.type != "var" and self.show_text_box:
                if self.text_box:
                    self.text_box.pos = (self.pos[0] + self.radius + 10 + input_name.get_rect().width + 10,
                                         self.pos[1] - small_text_size / 2 - 1)
                    self.text_box.frame(camera_delta, events, pos)

            pygame.draw.circle(self.node.display, self.get_hovered_color(
                colors[self.type]) if self.is_hovered else colors[
                self.type], self.pos,
                               self.radius)

        self.node.display.blit(input_name, (self.pos[0] + self.radius + 10,
                                            self.pos[1] - small_text_size / 2 - 1))

    value = property(get_value, set_value)

    def set_text_box(self):
        if self.show_text_box:
            self.text_box = TextBox(self.node.display, self.on_value_changed,
                                    size=((60 if self.is_dropdown else 30)*self.text_box_width_mult, small_text_size + 6), is_dropdown=self.is_dropdown, dropdown=self.dropdown)
            self.text_box.parent = self
            if not self.connected_pin:
                if self.is_dropdown:
                    self.text_box.text = self._display_value
                    self.text_box.value = self._value
                else:
                    self.text_box.text = str(self._value)
            self.text_box.is_active = False
        try:
            from Shyne.Sprite import Sprite
            if type(self._value) is Sprite:
                self._value = self.node.pyNDL.parent.shyne.get_sprite_with_id(self._value.id)
        except:
            pass

    def __deepcopy__(self, memo):
        new_input = Input(self.name, memo[-1], is_execution_pin=self.is_execution_pin, ptype=self.type, text_box_width_mult=self.text_box_width_mult, show_text_box=self.show_text_box, is_deletable=self.is_deletable, is_dropdown=self.is_dropdown, dropdown=self.dropdown)
        new_input.value = self._value
        new_input._display_value = self._display_value
        new_input.connected_pin = self.connected_pin
        return new_input

    def __getstate__(self):
        """ Called on save (pickled) to prevent unpickable object to cause an error """
        state = self.__dict__.copy()
        # Don't pickle display
        try:
            del state["ropes"]
            del state["text_box"]
        except KeyError:
            pass

        return state

    def __setstate__(self, state):
        """ Called on load data from file (unpickle) """
        self.__dict__.update(state)
        self.ropes = set()
        self.text_box = None


class Output(Pin):
    def __init__(self, name, node, is_execution_pin=False, ptype=int, is_deletable=False):
        super().__init__()
        self.is_input = False

        self.name = name
        self.node = node
        self.is_execution_pin = is_execution_pin

        self._stored_value = None
        self.type = ptype
        self._original_type = self.type

        self.is_deletable = is_deletable

        from pyNDL.Node import PureNode
        self.need_reload = True if isinstance(self.node, PureNode) else False

    def __deepcopy__(self, memo):
        new_output = Output(self.name, memo[-1], is_execution_pin=self.is_execution_pin, ptype=self.type)
        new_output.connected_pin = copy.copy(self.connected_pin)
        new_output.connected_pins = copy.copy(self.connected_pins)
        return new_output

    def get_stored_value(self):
        if self.need_reload:
            self.node.func()
        return self._stored_value

    def set_stored_value(self, value):
        self._stored_value = value

    def frame(self, camera_delta, events, pos):
        output_name = small_font.render(self.name, True, (255, 255, 255))

        if self.is_execution_pin:
            self.draw_execution_pin(self.node.display, self)
        else:
            pygame.draw.circle(self.node.display, self.get_hovered_color(
                colors[self.type]) if self.is_hovered else colors[
                self.type], self.pos,
                               self.radius)

        self.node.display.blit(output_name, (self.pos[0] - self.radius - 10 - output_name.get_rect().width,
                                             self.pos[1] - small_text_size / 2 - 1))

        if self.connected_pin:
            if not self.ropes:
                rope = Rope(self.node.display)
                rope.input = self.connected_pin
                rope.output = self
                self.ropes.add(rope)

        if self.connected_pins:
            if not self.ropes:
                for p in self.connected_pins:
                    rope = Rope(self.node.display)
                    rope.input = p
                    rope.output = self
                    self.ropes.add(rope)

        for rope in self.ropes:
            rope.draw(mouse_pos=pos)

    def clear_var(self):
        self.stored_value = None

    def __getstate__(self):
        """ Called on save (pickled) to prevent unpickable object to cause an error """
        state = self.__dict__.copy()
        # Don't pickle display
        del state["ropes"]
        del state["_stored_value"]
        return state

    def __setstate__(self, state):
        """ Called on load data from file (unpickle) """
        self.__dict__.update(state)
        # Add pyNDL and display back since it doesn't exist in the pickle
        self.ropes = set()
        self._stored_value = None

    stored_value = property(get_stored_value, set_stored_value)
