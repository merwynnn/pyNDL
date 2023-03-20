from pyNDL.Node import *
from pyNDL.Pin import *


class Addition(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=int),
                       "B": Input("B", self, ptype=int)}
        self.outputs = {"Result": Output("Result", self, ptype=int)}

        self.name = "+"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value + self.inputs["B"].value


class Substraction(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=int),
                       "B": Input("B", self, ptype=int)}
        self.outputs = {"Result": Output("Result", self, ptype=int)}

        self.name = "-"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value - self.inputs["B"].value


class ToInt(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Value": Input("", self, ptype=float, show_text_box=False)}
        self.outputs = {"Result": Output("", self, ptype=int)}

        self.name = " To Int"
        self.show_name = False

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = int(self.inputs["Value"].value)


class ToStr(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Value": Input("Value", self, ptype=None, show_text_box=False)}
        self.outputs = {"Result": Output("Result", self, ptype=str)}

        self.name = "To Str"
        self.show_name = False

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = str(self.inputs["Value"].value)


class Multiplication(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=float),
                       "B": Input("B", self, ptype=float)}
        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "*"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value * self.inputs["B"].value


class Division(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=float),
                       "B": Input("B", self, ptype=float)}
        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "/"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value / self.inputs["B"].value


class Equal(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "=="

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value == self.inputs["B"].value


class GreaterOrEqual(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = ">="

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value >= self.inputs["B"].value


class Greater(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = ">"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value > self.inputs["B"].value


class LessOrEqual(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "<="

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value <= self.inputs["B"].value


class Less(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "<"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value < self.inputs["B"].value


class NotEqual(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=None),
                       "B": Input("B", self, ptype=None)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "!="

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value != self.inputs["B"].value


class NotBool(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Bool": Input("Bool", self, ptype=bool)}
        self.outputs = {"Result": Output("Result", self, ptype=bool)}

        self.name = "Not"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = not self.inputs["Bool"].value


class Modulo(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"A": Input("A", self, ptype=float),
                       "B": Input("B", self, ptype=float)}
        self.outputs = {"Result": Output("Result", self, ptype=float)}

        self.name = "%"

        self.compact = True

    def func(self):
        self.outputs["Result"].stored_value = self.inputs["A"].value % self.inputs["B"].value
