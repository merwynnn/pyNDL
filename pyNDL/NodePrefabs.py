
from NodalLanguage.Node import ImpureNode, PureNode, Event, NodePrefab, Node, EndingNode
from NodalLanguage.Pin import Input, Output

from NodalLanguage.Prefabs.PythonBasic import *
from NodalLanguage.Prefabs.Operations import *
from NodalLanguage.Prefabs.VarAndFunc import *
from NodalLanguage.Prefabs.List import *
from NodalLanguage.Prefabs.Numpy import *
from NodalLanguage.Prefabs.Pillow import *

class EventStart(Event, NodePrefab):

    def __init__(self):
        super().__init__()
        self.name = "On Start"



