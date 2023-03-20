from NodalLanguage.Node import *
from NodalLanguage.Pin import *

import numpy


class ToArray(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["List"] = Input("List", self, ptype=list)
        self.outputs = {"Array": Output("Array", self, ptype="array")}

        self.name = "To Array"

        self.add_import("numpy")

    def func(self):
        self.outputs["Array"].stored_value = numpy.array(self.inputs["List"].value)


class NdArray(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Dim"] = Input("Dimensions", self, ptype=list)
        self.outputs = {"Array": Output("Array", self, ptype="array")}

        self.name = "Nd Array"

        self.add_import("numpy")

    def func(self):
        self.outputs["Array"].stored_value = numpy.zeros(self.inputs["Dim"].value)


class MakeVec2(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["X"] = Input("X", self, ptype=float)
        self.inputs["Y"] = Input("Y", self, ptype=float)
        self.outputs = {"Vector2": Output(" Vec2", self, ptype="vec2")}

        self.name = "Make Vector2"
        self.compact = True
        self.show_name = False

        self.add_import("numpy")

    def func(self):
        self.outputs["Vector2"].stored_value = numpy.array((self.inputs["X"].value, self.inputs["Y"].value))


class BreakVec2(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Vector2"] = Input("Vector2", self, ptype="vec2")
        self.outputs["X"] = Output("X", self, ptype=float)
        self.outputs["Y"] = Output("Y", self, ptype=float)

        self.name = "Break Vector2"
        self.compact = True
        self.show_name = False

    def func(self):
        vector2 = self.inputs["Vector2"].value
        self.outputs["X"].stored_value = vector2[0]
        self.outputs["Y"].stored_value = vector2[1]


class MakeVec3(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["X"] = Input("X", self, ptype=float)
        self.inputs["Y"] = Input("Y", self, ptype=float)
        self.inputs["Z"] = Input("Z", self, ptype=float)
        self.outputs = {"Vector3": Output(" Vec3", self, ptype="vec3")}

        self.name = "Make Vector3"
        self.compact = True
        self.show_name = False

        self.add_import("numpy")

    def func(self):
        self.outputs["Vector3"].stored_value = numpy.array((self.inputs["X"].value, self.inputs["Y"].value, self.inputs["Z"].value))


class BreakVec3(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Vector3"] = Input("Vector3", self, ptype="vec3")
        self.outputs["X"] = Output("X", self, ptype=float)
        self.outputs["Y"] = Output("Y", self, ptype=float)
        self.outputs["Z"] = Output("Z", self, ptype=float)

        self.name = "Break Vector3"
        self.compact = True
        self.show_name = False

    def func(self):
        vector3 = self.inputs["Vector3"].value
        self.outputs["X"].stored_value = vector3[0]
        self.outputs["Y"].stored_value = vector3[1]
        self.outputs["Z"].stored_value = vector3[2]

