from pyNDL.Components import NameSetter
from pyNDL.Node import *
from pyNDL.Pin import *


class SetVariable(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Value"] = Input("Value", self, ptype=None)

        self.variable = None

        self.name = "Set"

        self.is_visible_on_search = False

    def on_variable_change(self, variable):
        self.variable = variable
        self.name = variable.name
        self.inputs["Value"].type = variable.type

    def func(self):
        self.variable.value = self.inputs["Value"].value

    def on_load(self):
        if self.variable:
            self.variable = self.pyNDL.get_variable_from_id(self.variable.id)


class GetVariable(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.outputs = {"Value": Output("", self, ptype=None)}

        self.variable = None

        self.name = "Get"
        self.show_name = False
        self.compact = True

        self.is_visible_on_search = False

    def on_variable_change(self, variable):
        self.variable = variable
        self.name = variable.name
        self.outputs["Value"].name = variable.name
        self.outputs["Value"].type = variable.type
        self.calculate_size()

    def func(self):
        self.outputs["Value"].stored_value = self.variable.value

    def on_load(self):
        if self.variable:
            self.variable = self.pyNDL.get_variable_from_id(self.variable.id)


class Func(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()
        self.name = "Function"

        self.outputs["Return"] = Output("Return", self, ptype=None)

        self.function = None

        self.is_visible_on_search = False

    def on_function_change(self, func):
        self.function = func
        self.name = func.name
        self.function.callers.append(self)
        self.update()

    def update(self):
        for name, i in self.function.inputs.items():
            if name not in self.inputs.keys():
                self.add_input_runtime(Input(name, self, default_value=i, ptype=None), name)

        for name, i in self.inputs.items():
            if name != "Sprite" and name != "Function" and not i.is_execution_pin:
                if name not in self.function.inputs.keys():
                    self.remove_input_runtime(name)

    def func(self):
        for k, o, in self.function.inputs_node.outputs.items():
            o.stored_value = self.inputs[k].value
        self.outputs["Return"].stored_value = self.function.execute()


class FuncIn(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()
        self.name = "Inputs"

        self.inputs = {}

        self.function = None

        self.is_visible_on_search = False
        self.is_deletable = False

        self.activate_add_input_btn()

    def on_function_change(self, func):
        self.function = func
        self.name = func.name

    def on_pin_delete(self, pin):
        self.function.remove_input(pin.name)
        self.calculate_size()

    def on_add_item_btn_pressed(self):
        new_input = Output("Name", self, ptype=None, is_deletable=True)
        self.pyNDL.gui_components.append(NameSetter(self.pyNDL, self.display, new_input))


class ReturnNode(EndingNode, NodePrefab):
    def __init__(self):
        super().__init__()
        self.name = "Return Node"

        self.inputs["Return"] = Input("Return", self, ptype=None)

        self.return_value = None

        self.is_visible_on_search = False
        self.is_deletable = False

    def func(self):
        self.return_value = self.inputs["Return"].value
