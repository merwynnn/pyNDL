from PIL import Image

from NodalLanguage.Node import *
from NodalLanguage.Pin import *


class OpenImage(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Name"] = Input("Name", self, ptype=str)
        self.outputs = {"Image": Output("Image", self, ptype="array")}

        self.name = "Open Image"

    def func(self):
        self.outputs["Image"].stored_value = Image.open("./Custom/" + self.inputs["Name"].value)


class CreateImage(PureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Width"] = Input("Width", self, ptype=int)
        self.inputs["Height"] = Input("Height", self, ptype=int)

        self.outputs = {"Image": Output("Image", self, ptype="array")}

        self.name = "Create Image"

    def func(self):
        self.outputs["Image"].stored_value = Image.new("RGB", (self.inputs["Width"].value, self.inputs["Height"].value))


class ShowImage(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Image"] = Input("Image", self, ptype="array")

        self.name = "Show Image"

    def func(self):
        image = self.inputs["Image"].value
        image.show()


class SetPixel(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Image"] = Input("Image", self, ptype="array")
        self.inputs["X"] = Input("X", self, ptype=int)
        self.inputs["Y"] = Input("Y", self, ptype=int)
        self.inputs["Color"] = Input("Color", self, ptype=list)

        self.name = "Set Pixel"

    def func(self):
        self.inputs["Image"].value.putpixel((self.inputs["X"].value, self.inputs["Y"].value),
                                            tuple(self.inputs["Color"].value))


class GetPixel(ImpureNode, NodePrefab):
    def __init__(self):
        super().__init__()

        self.inputs["Image"] = Input("Image", self, ptype="array")
        self.inputs["X"] = Input("X", self, ptype=int)
        self.inputs["Y"] = Input("Y", self, ptype=int)

        self.outputs["Color"] = Output("Color", self, ptype=list)

        self.name = "Get Pixel"

    def func(self):
        self.inputs["Color"].value = self.inputs["Image"].value.getpixel(
            (self.inputs["X"].value, self.inputs["Y"].value))
