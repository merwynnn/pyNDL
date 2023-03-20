import copy
import random

from NodalLanguage.DataHandler import Data


class Variable:
    """ Custom variable """

    def __init__(self, name, vtype=None, custom_get=None, custom_set=None):
        self.id = random.randint(0, 1000000)

        self.name = name
        self.value = 0
        self.type = vtype
        self.custom_get = custom_get
        self.custom_set = custom_set

    def __getstate__(self):
        state = self.__dict__.copy()
        # Don't pickle display
        del state["value"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.value = 0

    def __copy__(self):
        return Variable(self.name, vtype=self.type, custom_get=self.custom_get, custom_set=self.custom_set)


class Function:
    """ Custom function """

    def __init__(self, name):
        self.name = name
        self.data = Data()
        self.data.is_main = False

        self.inputs = {}
        from NodalLanguage.Prefabs.VarAndFunc import FuncIn, ReturnNode
        self.inputs_node = FuncIn()
        self.inputs_node.on_function_change(self)
        self.inputs_node.pos = (-100, -10)

        self.return_node = ReturnNode()
        self.return_node.pos = (100, -10)

        self.callers = []

        self.data.nodes.append(self.inputs_node)
        self.data.nodes.append(self.return_node)

    def execute(self):
        self.inputs_node.execute()
        return self.return_node.return_value

    def add_input(self, name):
        self.inputs[name] = 0
        for caller in copy.copy(self.callers):
            if hasattr(caller, "display"):
                caller.update()
            else:
                self.callers.remove(caller)

    def remove_input(self, name):
        del self.inputs[name]
        for caller in copy.copy(self.callers):
            if hasattr(caller, "display"):
                caller.update()
            else:
                self.callers.remove(caller)

    def __copy__(self):
        func = Function(self.name)
        func.data = copy.copy(self.data)
        from NodalLanguage.Prefabs.VarAndFunc import FuncIn, ReturnNode
        for node in func.data.nodes:
            if type(node) is FuncIn:
                func.inputs_node = node
            elif type(node) is ReturnNode:
                func.return_node = node
        return func
