import _pickle as cPickle
import copy
import pickle
import random
import string
import os
import pyperclip as pc


class Data:
    def __init__(self):
        self.is_main = True     # if it is the main script or a function

        self.nodes = []  # Stores all the created nodes

        self.camera_delta = (0, 0)

        self.variables = set()
        self.functions = set()

    def get_all_nodes(self):
        func_nodes = [node for func in self.functions for node in func.data.nodes]
        nodes = self.nodes + func_nodes
        return nodes

    def __copy__(self):
        data = Data()
        data.is_main = self.is_main
        for node in self.nodes:
            data.nodes.append(copy.copy(node))
        for var in self.variables:
            data.variables.add(copy.copy(var))
        for func in self.functions:
            data.functions.add(copy.copy(func))
        return data

def save_data(filename, data):
    with open(filename, "wb") as f:
        cPickle.dump(data, f)


def load_data(filename):
    try:
        with open(filename, "rb") as f:
            data = cPickle.load(f)
    except:
        data = Data()
    return data


def copy_data(data):
    d = str(pickle.dumps(data))
    pc.copy(d)


def get_clipboard_data():
    d = pc.paste()
    try:
        data = cPickle.loads(eval(d))
    except:
        return False
    return data

