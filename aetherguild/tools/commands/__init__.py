import os
import importlib
import glob
import inspect
from argparse import ArgumentParser


class BaseCommand(object):
    description = None

    @staticmethod
    def get_args(args: ArgumentParser):
        pass

    @classmethod
    def get_instance(cls):
        return cls()

    async def on_init(self):
        pass

    async def on_run(self, args, app):
        pass

    async def on_close(self):
        pass


class CommandLoader(object):
    classes = []

    @classmethod
    def load(cls):
        c_dir = os.path.dirname(os.path.abspath(__file__))
        for file in glob.glob("{}/*.py".format(c_dir)):
            filename, _ = os.path.splitext(os.path.basename(file))
            if filename in ['__init__']:
                continue
            module_name = '{}.{}'.format(__name__, filename)
            mod = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    if BaseCommand in obj.__bases__:
                        cls.classes.append(obj)
