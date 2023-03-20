
from pyNDL.Node import ImpureNode, PureNode, Event, NodePrefab, Node, EndingNode
from pyNDL.Pin import Input, Output

from pyNDL.Prefabs.PythonBasic import *
from pyNDL.Prefabs.Operations import *
from pyNDL.Prefabs.VarAndFunc import *
from pyNDL.Prefabs.List import *
from pyNDL.Prefabs.Numpy import *
from pyNDL.Prefabs.Pillow import *

class EventStart(Event, NodePrefab):

    def __init__(self):
        super().__init__()
        self.name = "On Start"



