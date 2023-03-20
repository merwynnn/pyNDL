from NodalLanguage.Node import *
from NodalLanguage.Pin import *


class List(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.outputs = {"List": Output("List", self, ptype=list)}

        self.name = "List"

        self.activate_add_input_btn()

    def func(self):
        self.outputs['List'].stored_value = [item.value for item in self.inputs.values()]

    def on_add_item_btn_pressed(self):
        new_input = Input("Item", self, ptype=None, is_deletable=True)
        new_input.set_text_box()
        self.inputs[len(self.inputs) + 1] = new_input
        self.calculate_size()


class Append(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Item"] = Input("Item", self, ptype=None)

        self.name = "Append"

    def func(self):
        self.inputs["List"].value.append(self.inputs["Item"].value)


class GetByIndex(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Index"] = Input("Index", self, ptype=int)

        self.outputs = {"Item": Output("Item", self, ptype=None)}

        self.name = "GetByIndex"

    def func(self):
        self.outputs["Item"].stored_value = self.inputs["List"].value[self.inputs["Index"].value]


class SetByIndex(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Index"] = Input("Index", self, ptype=int)
        self.inputs["Value"] = Input("Value", self, ptype=None)

        self.name = "SetByIndex"

    def func(self):
        self.inputs["List"].value[self.inputs["Index"].value] = self.inputs["Value"].value


class Sum(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)

        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "Sum"

    def func(self):
        self.outputs["Result"].stored_value = sum(self.inputs["List"].value)


class Max(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)

        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "Max"

    def func(self):
        self.outputs["Result"].stored_value = max(self.inputs["List"].value)


class Min(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)

        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "Min"

    def func(self):
        self.outputs["Result"].stored_value = min(self.inputs["List"].value)


class Remove(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Item"] = Input("Item", self, ptype=None)

        self.name = "Remove"

    def func(self):
        self.inputs["List"].value.remove(self.inputs["Item"].value)


class Pop(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Index"] = Input("Index", self, ptype=int)

        self.name = "Pop"

    def func(self):
        self.inputs["List"].value.pop(self.inputs["Index"].value)


class InList(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.inputs["Item"] = Input("Item", self, ptype=None)

        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "Is In List"

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["Item"].value in self.inputs["List"].value
