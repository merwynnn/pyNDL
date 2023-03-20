import sys
import threading
import ctypes
import logging


class ThreadedProcess(threading.Thread):
    def __init__(self, name, func):
        threading.Thread.__init__(self)
        self.name = name

        self.func = func

    def run(self):
        debug = True
        if debug:
            self.func()
        else:
            # target function of the thread class
            try:
                self.func()
            except Exception as ex:
                logging.warning(ex)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
