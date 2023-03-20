import os
import sys
import pygame

from pyNDL.NodePrefabs import *
from pyNDL.NodeSelector import NodeSelector
from pyNDL.Rope import Rope
from pyNDL.Components import TopBar, VariableSelector, LeftBar, GoBackButton
import copy
from pyNDL.DataHandler import load_data, save_data, Data, copy_data, get_clipboard_data
from pyNDL import Assets, ThreadedProcess
from pyNDL.Colors import colors


class pyNDL:
    BACKGROUND_COLOR = (61, 61, 61)

    def __init__(self, filename, win, pos, size, show_top_bar=True, allow_save=True, parent=None,
                 additional_colors=None, on_action=None):
        self.parent = parent

        self.filename = filename

        self.win = win
        self.display = pygame.Surface(size)

        if additional_colors:
            colors.update(additional_colors)
        Assets.init()

        self.pos = pos
        self.size = size
        self.zoom = 1

        self.node_prefabs = set()  # Stores all the nodes prefab

        nodes = NodePrefab.__subclasses__()
        for node in nodes:
            self.add_node_to_prefabs(node())

        self.node_selector = NodeSelector(self, self.display, self.node_prefabs)
        self.main_data = None

        self.selected_node = None
        self.selected_nodes = []

        self.hovered_node = None
        self.hovered_pin = None

        self.is_camera_moving = False
        self.last_pos = (0, 0)

        self.is_object_moving = False
        self.initial_mouse_pos = (0, 0)
        self.initial_object_pos = (0, 0)

        self.is_pin_pressed = False
        self.current_pin_pressed = None

        self.focus_blocked = False

        self.data = load_data(self.filename)
        self.data.camera_delta = self.get_screen_center_delta()
        self.load_data(self.data)

        if show_top_bar:
            self.top_bar_height = 40
        else:
            self.top_bar_height = 0

        self.top_bar = TopBar(self, self.display, (0, 0), (size[0], self.top_bar_height))

        self.leftBar = LeftBar(self, self.display, (0, self.top_bar_height), (200, self.size[1] - self.top_bar_height))

        self.go_back_btn = GoBackButton(self, self.display, (205, self.top_bar_height + 5))

        self.gui_components = [self.top_bar, self.leftBar]

        self.threads = []

        self.action_history = []
        self.last_action_index = 0

        self.is_in_function = False
        self.current_function = None

        self.allow_save = allow_save

        self.box_selection_pos = None

        self.on_action = on_action

    def frame(self, events, pos):
        """ Called every frame : main """
        # Background
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.display, self.BACKGROUND_COLOR, rect, width=0)

        pos = (pos[0] / self.zoom, pos[1] / self.zoom)  # mouse position

        # Loops for every node in the file
        for node in reversed(self.data.nodes):
            node.frame(self.data.camera_delta, events, pos)

        self.keyboard_handler(events, pos)

        self.node_selector.frame(self.data.camera_delta, events, pos)

        for gui_component in self.gui_components:
            gui_component.frame(self.data.camera_delta, events, pos)

        self.win.blit(pygame.transform.scale(self.display, self.size), (0, 0))

    def keyboard_handler(self, events, pos):
        """ Handles all of the global keyboard events """
        pos_delta = self.get_pos_with_delta(pos)
        keys = pygame.key.get_pressed()
        if not self.focus_blocked:
            self.hovered_node = self.get_hovered_node(pos)
            if self.hovered_node is not None:
                if self.hovered_pin is not None:
                    self.hovered_pin.is_hovered = False

                self.hovered_pin = self.get_hovered_pin(pos)
                if self.hovered_pin is not None:
                    self.hovered_pin.is_hovered = True
            else:
                if self.hovered_pin:
                    self.hovered_pin.is_hovered = False
                    self.hovered_pin = None

            for event in events:
                if event.type == pygame.QUIT:
                    self.save()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:  # Delete
                        if self.selected_node is not None:
                            self.delete_node(self.selected_node)
                            self.selected_node = None
                        for node in self.selected_nodes:
                            self.delete_node(node)
                        self.selected_nodes = []
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:  # On Save
                        if self.allow_save:
                            self.save()

                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:    # Copy
                        if self.selected_node is not None:
                            copy_data([self.selected_node] + self.selected_nodes)
                    if event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:    # Paste
                        data = get_clipboard_data()
                        self.select_node(None)
                        if data:
                            self.action()
                            nodes_pos = data[-1].pos
                            for node in data:
                                node.setNodalLanguage(self)
                                for pin in list(node.inputs.values()) + list(node.outputs.values()):
                                    if pin.is_input:
                                        pin.set_text_box()
                                    if pin.is_input or pin.is_execution_pin:
                                        if pin.connected_pin is not None:
                                            if pin.connected_pin.node not in data:
                                                pin.disconnect()
                                    else:
                                        for connected_pin in copy.copy(pin.connected_pins):
                                            if connected_pin.node not in data:
                                                pin.disconnect(connected_pin)
                                node.pos = (pos[0] + self.data.camera_delta[0] + node.pos[0] - nodes_pos[0],
                                            pos[1] + self.data.camera_delta[1] + node.pos[1] - nodes_pos[1])
                                self.data.nodes.append(node)
                                self.select_node(node, shift=True)
                    if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:    # Undo
                        self.undo()
                    if event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:    # Redo
                        self.redo()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right click
                        self.node_selector.pos = pos
                        self.node_selector.enable() # Enable the node selector

                    if event.button == 1:  # Left click
                        if keys[pygame.K_LALT]:
                            rope = self.get_hovered_rope(pos)
                            if rope:  # Delete rope
                                self.action()
                                rope.input.disconnect(rope.output)
                                return
                            else:  # Delete Pin
                                if self.hovered_pin:
                                    if self.hovered_pin.is_deletable:
                                        self.hovered_pin.delete()
                                        self.hovered_pin = None
                                        self.current_pin_pressed = None
                                        return
                        if keys[pygame.K_LSHIFT]:
                            if self.hovered_pin:
                                if self.hovered_pin.is_input:
                                    if self.hovered_pin.type == "vec2":
                                        self.select_node(None)
                                        new_node = self.add_node(MakeVec2(), (
                                            self.hovered_pin.pos[0] - 200, self.hovered_pin.pos[1] - 30))
                                    elif self.hovered_pin.type == "vec3":
                                        self.select_node(None)
                                        new_node = self.add_node(MakeVec3(), (
                                            self.hovered_pin.pos[0] - 200, self.hovered_pin.pos[1] - 30))
                                    else:
                                        return
                                    rope = Rope(self.display)
                                    self.connect_pins(self.hovered_pin, list(new_node.outputs.values())[0], rope)
                                    return
                                else:
                                    if self.hovered_pin.type == "vec2":
                                        self.select_node(None)
                                        new_node = self.add_node(BreakVec2(), (
                                            self.hovered_pin.pos[0] + 50, self.hovered_pin.pos[1] - 30))
                                    elif self.hovered_pin.type == "vec3":
                                        self.select_node(None)
                                        new_node = self.add_node(BreakVec3(), (
                                            self.hovered_pin.pos[0] + 50, self.hovered_pin.pos[1] - 30))
                                    else:
                                        return
                                    rope = Rope(self.display)
                                    self.connect_pins(list(new_node.inputs.values())[0], self.hovered_pin, rope)
                                    return

                        if (not (self.hovered_node is not None and len(self.selected_nodes) > 0)) or (self.hovered_node is not self.selected_node and self.hovered_node not in self.selected_nodes):
                            self.select_node(self.hovered_node, keys[pygame.K_LSHIFT])

                    if event.button == 4:
                        self.set_zoom(self.zoom / 1.1)
                    elif event.button == 5:
                        self.set_zoom(self.zoom * 1.1)
                if event.type == pygame.MOUSEBUTTONUP:
                    self.box_selection_pos = None
                    if self.is_object_moving:
                        self.is_object_moving = False
                    if self.current_pin_pressed:
                        if self.hovered_pin is not None:
                            if self.hovered_pin != self.current_pin_pressed:  # On click release on input or output
                                if type(self.hovered_pin) is not type(self.current_pin_pressed):
                                    if self.hovered_pin.is_execution_pin == self.current_pin_pressed.is_execution_pin:
                                        rope = Rope(self.display)
                                        if type(self.current_pin_pressed) is Input:
                                            self.action()
                                            self.connect_pins(self.current_pin_pressed, self.hovered_pin, rope)

                                        if type(self.hovered_pin) is Input:
                                            self.action()
                                            self.connect_pins(self.hovered_pin, self.current_pin_pressed, rope)
                        else:
                            self.node_selector.pos = pos
                            self.node_selector.enable(current_pin=self.current_pin_pressed)
                    self.current_pin_pressed = None

            mouse_btn = pygame.mouse.get_pressed()
            if mouse_btn[1]:  # Move camera

                if not self.is_camera_moving:
                    self.last_pos = pos
                self.is_camera_moving = True

                self.data.camera_delta = (
                    (self.data.camera_delta[0] + (self.last_pos[0] - pos[0])),
                    self.data.camera_delta[1] + (self.last_pos[1] - pos[1]))

                self.last_pos = pos
            else:

                if self.is_camera_moving:
                    self.is_camera_moving = False
                    self.last_pos = (0, 0)

            if mouse_btn[0]:  # Left click
                if self.box_selection_pos:  # Drawing the box selection rectangle
                    if self.is_object_moving:
                        self.box_selection_pos = None
                        return
                    # Getting the top left of the rectangle
                    if self.box_selection_pos[0] < pos[0]:
                        if self.box_selection_pos[1] < pos[1]:
                            p = self.box_selection_pos
                        else:
                            p = (self.box_selection_pos[0], pos[1])
                    else:
                        if self.box_selection_pos[1] < pos[1]:
                            p = (pos[0], self.box_selection_pos[1])
                        else:
                            p = pos
                    size = (abs(self.box_selection_pos[0] - pos[0]), abs(self.box_selection_pos[1] - pos[1]))
                    rect = pygame.Rect(p, size)
                    pygame.draw.rect(self.display, (255, 255, 255), rect, 2)
                    p = self.get_pos_with_delta(p)
                    for node in self.data.nodes:
                        node_pos = node.get_center()
                        if p[0] <= node_pos[0] <= p[0] + size[0] and p[1] <= node_pos[1] <= p[1] + size[1]:
                            if node not in self.selected_nodes + [self.selected_node]:
                                self.select_node(node, shift=True)
                        else:
                            if node in self.selected_nodes + [self.selected_node]:
                                if self.selected_node is node:
                                    node.is_selected = False
                                    if len(self.selected_nodes) > 0:
                                        n_node = self.selected_nodes.pop(-1)
                                        self.selected_node = n_node
                                    else:
                                        self.selected_node = None
                                else:
                                    self.selected_nodes.remove(node)
                                    node.is_selected = False

                elif self.current_pin_pressed:  # On output or input drag
                    Rope(self.display).draw(pos1=self.current_pin_pressed.pos, pos2=pos, pin=self.current_pin_pressed)
                elif self.is_object_moving:  # Move node
                    for node in self.selected_nodes + [self.selected_node]:
                        mouse_delta = (
                            pos_delta[0] - self.initial_mouse_pos[0], pos_delta[1] - self.initial_mouse_pos[1])
                        if node:
                            node.pos = (node.initial_pos_on_move[0] + mouse_delta[0],
                                        node.initial_pos_on_move[1] + mouse_delta[1])
                elif self.hovered_node is not None:
                    if not self.is_object_moving:
                        if self.hovered_pin is None:  # Move node initiate
                            if not keys[pygame.K_LSHIFT] and self.selected_node is not None:
                                self.action()
                                self.initial_mouse_pos = pos_delta
                                self.selected_node.initial_pos_on_move = self.selected_node.pos
                                for node in self.selected_nodes:
                                    node.initial_pos_on_move = node.pos
                                self.is_object_moving = True
                        else:
                            self.current_pin_pressed = self.hovered_pin
                else:
                    if not self.box_selection_pos:
                        if not keys[pygame.K_LSHIFT]:
                            self.select_node(None)
                        self.box_selection_pos = pos



    def connect_pins(self, inp, out, rope):
        """ Connects 2 pin to each other """
        if type(inp) is Input:
            input = inp
            output = out
        else:
            input = out
            output = inp

        if input.is_execution_pin != output.is_execution_pin:
            return

        if output.is_execution_pin:
            output.disconnect()
        input.disconnect(pin=output)
        input.connect(output)
        output.connect(input)

        rope.input = input
        rope.output = output

        output.ropes.add(rope)

    def add_node_to_prefabs(self, node):
        """ Add a node prefab to the available nodes """
        self.node_prefabs.add(node)

    def add_node(self, node, pos):
        """ Add a new node to the script """
        self.action()
        new_node = copy.copy(node)
        new_node.pos = self.get_pos_with_delta(pos)
        new_node.setNodalLanguage(self)
        self.data.nodes.append(new_node)
        self.select_node(new_node)
        return new_node

    def delete_node(self, node):
        """ Deletes a specific node """
        if node.is_deletable:
            self.action()
            self.data.nodes.remove(node)
            node.delete()

    def get_hovered_node(self, mouse_pos):
        """ Returns the currently hovered node """
        for node in self.data.nodes:
            if node.is_hovered(mouse_pos, self.data.camera_delta):
                return node
        return None

    def get_hovered_rope(self, mouse_pos):
        """ Returns the currently hovered rope """
        for node in self.data.nodes:
            for output in node.outputs.values():
                for rope in output.ropes:
                    if rope.is_hovered:
                        return rope
        return None

    def get_hovered_pin(self, mouse_pos):
        """ Returns the currently hovered pin """
        return self.hovered_node.get_hovered_pin(mouse_pos)

    def select_node(self, node, shift=False):
        """ Select a node """
        if shift:
            if self.selected_node is None or node is None:
                self.select_node(node, shift=False)
            else:
                self.selected_nodes.append(node)
                node.is_selected = True
                self.data.nodes.remove(node)
                self.data.nodes.insert(0, node)
        else:
            for n in self.selected_nodes:
                n.is_selected = False
            self.selected_nodes = []
            if self.selected_node is not None:
                self.selected_node.is_selected = False
            self.selected_node = node
            if self.selected_node is not None:
                self.selected_node.is_selected = True
                self.data.nodes.remove(node)
                self.data.nodes.insert(0, node)

    def get_pos_with_delta(self, pos):
        """ Returns the mouse position with the camera delta (the current on-board position) """
        return pos[0] + self.data.camera_delta[0], pos[1] + self.data.camera_delta[1]

    def set_zoom(self, new_zoom):
        pass
        # self.zoom = new_zoom
        # self.display = pygame.Surface((self.size[0]/new_zoom, self.size[1]/new_zoom))

    def start(self):
        """ Start the current script """
        print("--------------------New Start Call--------------------")
        for t in self.threads:
            t.raise_exception()
            t.join()
        self.threads = []

        for variable in self.data.variables:
            variable.value = 0

        event_start_nodes = []
        nodes = self.get_main_data().nodes

        for i, node in enumerate(nodes):
            if type(node) is EventStart:
                event_start_nodes.append(node)
                t = ThreadedProcess.ThreadedProcess(f"Thread {i}", node.execute)
                t.start()
                self.threads.append(t)

    def load_data(self, data):
        """ Load datas """
        self.data = data
        nodes = self.data.get_all_nodes()
        for func in self.data.functions:
            func.callers = []

        for node in nodes:
            for input in node.inputs.values():
                input.ropes = []
            node.setNodalLanguage(self)

    def add_variable(self, variable, is_local=False):
        """ Add a new variable """
        self.action()
        if is_local:
            self.data.variables.add(variable)
        else:
            self.get_main_data().variables.add(variable)
        self.leftBar.update()

    def delete_variable(self, variable, is_local=False):
        """ Deletes a variable """
        self.action()
        if is_local:
            self.data.variables.discard(variable)
        else:
            self.get_main_data().variables.discard(variable)
        for node in copy.copy(self.data.nodes):
            if type(node) is GetVariable or type(node) is SetVariable:
                if node.variable == variable:
                    self.delete_node(node)
        self.leftBar.update()

    def add_function(self, func):
        """ Adds a new function """
        self.action()
        self.get_main_data().functions.add(func)
        self.leftBar.update()

    def delete_function(self, function):
        """ Deletes a function """
        self.action()
        self.get_main_data().functions.discard(function)
        self.go_back()
        for node in copy.copy(self.data.nodes):
            if type(node) is Func:
                if node.function == function:
                    self.delete_node(node)
        self.leftBar.update()

    def set_focus_blocked(self, focus):
        """ Block the focus (on a window is opened for example) """
        if focus:
            self.focus_blocked = True
        else:
            self.focus_blocked = False
            self.reset_current_action()

    def reset_current_action(self):
        """ Resets the current action to prevent glitches """
        self.hovered_pin = None
        self.current_pin_pressed = None
        self.hovered_node = None
        self.is_pin_pressed = False

    def action(self):
        """ Notice the program that a change has been made (for undo-redo) """
        selected_node_index = self.data.nodes.index(self.selected_node) if self.selected_node else None
        self.action_history.append((self.copy_nodes(), selected_node_index))
        self.last_action_index = -1
        if self.on_action:
            self.on_action()

    def undo(self):
        """ Undo the last action """
        if len(self.action_history) - 1 > self.last_action_index * -1:
            self.undo_redo(self.action_history[self.last_action_index])
            self.last_action_index -= 1

    def redo(self):
        """ Redo the last undo """
        if self.last_action_index != -1:
            self.last_action_index += 1
            self.undo_redo(self.action_history[self.last_action_index])

    def undo_redo(self, action):
        self.data.nodes = action[0]
        for node in self.data.nodes:
            node.setNodalLanguage(self)
            for pin in node.inputs.values():
                pin.set_text_box()

        if action[1]:
            self.select_node(self.data.nodes[action[1]])
        else:
            self.select_node(None)

    def copy_nodes(self):
        """ Copy all the current nodes """
        new_nodes = []
        for node in self.data.nodes:
            c = copy.copy(node)
            c.is_selected = False
            new_nodes.append(c)
        return new_nodes

    def open_function(self, function):
        """ Open a specific function """
        if not self.main_data:
            self.main_data = self.data
            self.gui_components.append(self.go_back_btn)

        function.data.camera_delta = self.get_screen_center_delta()
        self.load_data(function.data)
        self.is_in_function = True
        self.current_function = function
        self.leftBar.update()

    def go_back(self):
        """ Go back to the main script and leave a function """
        if self.is_in_function:
            self.data = self.main_data
            self.main_data = None
            self.gui_components.remove(self.go_back_btn)
        self.is_in_function = False
        self.current_function = None
        self.leftBar.update()

    def get_screen_center_delta(self):
        """ Returns the screen center """
        return -self.display.get_width() / 2, -self.display.get_height() / 2

    def get_main_data(self):
        """ Returns the main script data """
        return self.data if self.main_data is None else self.main_data

    def save(self):
        """ Save the current script """
        save_data(self.filename, self.get_main_data())

    def get_variable_from_id(self, id):
        for variable in self.get_main_data().variables:
            if variable.id == id:
                return variable
        if self.current_function:
            for variable in self.data.variables:
                if variable.id == id:
                    return variable
        return None

    def get_function_from_name(self, name):
        for func in self.data.functions:
            if func.name == name:
                return func
        return None

    def get_builded_node(self, node, imports, variables, cur_outputs=None, compute_replacements=None):
        func = node.get_func(split=True)

        if compute_replacements:
            replacements = compute_replacements(node, variables)
        else:
            replacements = {}

        if cur_outputs is None:
            current_outputs = {}
        else:
            current_outputs = cur_outputs

        for imp in node.imports:
            if imp not in imports:
                imports.append(imp)

        for var in node.custom_vars:
            if var not in variables:
                variables.append((var, None))

        for o, r in replacements.items():
            if r == 0:  # Delete line
                n_func = copy.copy(func)
                for i, line in enumerate(n_func):
                    if line.line.find(o) != -1:
                        func.pop(i)
            else:
                for line in func:
                    line.line = line.line.replace(o, r)

        for line in func:
            if "self.rotation" in line.line:
                self._has_rotation = True
                break

        while True:
            output = self.get_framed_position(func, 'self.outputs["', '"].stored_value', single=True)
            output_exec = self.get_framed_position(func, 'self.outputs["', '"].execute', single=True)
            input = self.get_framed_position(func, 'self.inputs["', '"].value', single=True)

            if output:
                rank_output = output[1] + func.index(output[3]) * len(output[3].line)
            else:
                rank_output = 999999

            if output_exec:
                rank_output_exec = output_exec[1] + func.index(output_exec[3]) * len(output_exec[3].line)
            else:
                rank_output_exec = 999999
            if input:
                rank_input = input[1] + func.index(input[3]) * len(input[3].line)
            else:
                rank_input = 999999

            if rank_output < rank_output_exec and rank_output < rank_input:
                last_name, s, e, l = output
                s = s - len('self.outputs["')
                e = e + len('"].stored_value')
                name = last_name.replace(' ', '_')
                o = current_outputs.get(node.outputs[last_name])
                if o is not None:
                    name = o
                else:
                    if name in current_outputs.values():
                        nb = list(current_outputs.values()).count(name)
                        name = name + str(nb)
                current_outputs[node.outputs[last_name]] = name
                l.line = l.line[:s] + name + l.line[e:]

            elif rank_output_exec < rank_output and rank_output_exec < rank_input:
                name, s, e, line = output_exec

                if node.outputs[name].connected_pin:
                    builded_func, current_outputs = self.get_builded_node(node.outputs[name].connected_pin.node,
                                                                          imports, variables,
                                                                          cur_outputs=current_outputs, compute_replacements=compute_replacements)
                    for l in builded_func:
                        l.set_increments(l.get_increments() + line.get_increments())
                else:
                    pass_line = Line("pass")
                    pass_line.set_increments(line.get_increments())
                    builded_func = [pass_line]

                li = func.index(line)
                func.pop(li)
                func = func[:li] + builded_func + func[li:]
            elif rank_input < rank_output and rank_input < rank_output_exec:
                input_name, start, end, line = input
                current_input = node.inputs[input_name]
                if current_input.connected_pin:
                    if current_outputs.get(current_input.connected_pin) is None:
                        builded_func, current_outputs = self.get_builded_node(current_input.connected_pin.node, imports,
                                                                              variables,
                                                                              cur_outputs=current_outputs, compute_replacements=compute_replacements)
                        if len(builded_func) == 1:  # If single lined
                            l = builded_func[0]
                            l.line = l.line[l.line.find("=") + 2:]
                            l.line = f"({l.line})"

                            s = start - len('self.inputs["')
                            e = end + len('"].value')

                            line.line = line.line[:s] + l.line + line.line[e:]

                        else:
                            li = func.index(line)
                            func = func[:li] + builded_func + func[li:]

                            s = start - len('self.inputs["')
                            e = end + len('"].value')

                            n = current_outputs.get(current_input.connected_pin)
                            line.line = line.line[:s] + n + line.line[e:]
                    else:
                        s = start - len('self.inputs["')
                        e = end + len('"].value')

                        line.line = line.line[:s] + current_outputs[current_input.connected_pin] + line.line[e:]

                else:
                    s = start - len('self.inputs["')
                    e = end + len('"].value')
                    value = current_input._value

                    if type(value) is str:
                        value = f'"{value}"'
                    else:
                        value = str(value)

                    line.line = line.line[:s] + value + line.line[e:]
            else:
                break

        if isinstance(node, ImpureNode) or isinstance(node, Event):
            if node.outputs["Exec"].connected_pin is not None:
                builded_func, current_outputs = self.get_builded_node(node.outputs["Exec"].connected_pin.node, imports,
                                                                      variables, cur_outputs=current_outputs, compute_replacements=compute_replacements)
                func = func + builded_func
        return func, current_outputs

    def get_framed_position(self, func, start, end, single=False):
        """ Get the names of a framed string and its position in a function """

        pins = []
        run = True
        for f in func:
            d = 0
            text = f.line
            while run:
                s = text.find(start) + len(start)
                e = text.find(end)
                if s == -1 or e == -1:
                    break
                pins.append((text[s:e], s + d, e + d, f))
                if single:
                    return pins[0]

                d += e + len(end)
                text = text[e + len(end):]

        return pins