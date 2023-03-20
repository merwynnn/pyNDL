import time

from NodalLanguage.Node import *
from NodalLanguage.Pin import *


class Print(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["String"] = Input("String", self, ptype=str)

        self.name = "Print"

    def func(self):
        print(self.inputs["String"].value)


class CurrentTime(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.outputs = {"Time": Output("Time", self, ptype=float)}

        self.name = "Current Time"

        self.add_import("time")

    def func(self):
        self.outputs["Time"].stored_value = time.time()


class If(Node, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Exec": Input("", self, is_execution_pin=True),
                       "Condition": Input("Condition", self, ptype=bool)}
        self.outputs = {"True": Output("True", self, is_execution_pin=True),
                        "False": Output("False", self, is_execution_pin=True)}

        self.name = "If"

    def func(self):
        if self.inputs["Condition"].value:
            self.outputs["True"].execute()
        else:
            self.outputs["False"].execute()


class ForLoop(Node, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Exec": Input("", self, is_execution_pin=True), "Loop": Input("Loop", self, ptype=None)}
        self.outputs = {"Loop Body": Output("Loop Body", self, is_execution_pin=True),
                        "Value": Output("Value", self, ptype=None),
                        "Completed": Output("Completed", self, is_execution_pin=True)}

        self.name = "For Loop"

    def func(self):
        for value in self.inputs["Loop"].value:
            self.outputs["Value"].stored_value = value
            self.outputs["Loop Body"].execute()
        self.outputs["Completed"].execute()


class WhileLoop(Node, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Exec": Input("", self, is_execution_pin=True),
                       "Condition": Input("Condition", self, ptype=bool)}
        self.outputs = {"Loop Body": Output("Loop Body", self, is_execution_pin=True),
                        "Completed": Output("Completed", self, is_execution_pin=True)}

        self.name = "While Loop"

    def func(self):
        while self.inputs["Condition"].value:
            self.outputs["Loop Body"].execute()
        self.outputs["Completed"].execute()


class Range(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs = {"Start": Input("Start", self, ptype=int),
                       "End": Input("End", self, ptype=int)}
        self.outputs = {"Result": Output("Range", self, ptype=None)}

        self.name = "Range"

        self.compact = True

    def func(self):
        self.outputs['Result'].stored_value = range(self.inputs["Start"].value,self.inputs["End"].value)


class Delay(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Duration"] = Input("Duration", self, ptype=float)

        self.name = "Delay"

        self.add_import("time")

    def func(self):
        time.sleep(self.inputs["Duration"].value)


class WildCard(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.name = "WildCard"

        self.inputs = {"In": Input("", self, ptype=None, show_text_box=False)}
        self.outputs = {"Out": Output("", self, ptype=None)}

        self.compact = True
        self.show_name = False
        self.name_size = 0

    def func(self):
        self.outputs['Out'].stored_value = self.inputs["In"].value
