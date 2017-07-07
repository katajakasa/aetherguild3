# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging
from logging import basicConfig

from dynaconf import settings

from aetherguild.deprecated.hash import register_hash
from aetherguild.framework.web.cache import init_cache, close_cache
from aetherguild.framework.web.database import init_db, close_db
from .commands import CommandLoader

# Attempt to use uvloop if it is available
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


log = logging.getLogger(__name__)


class Application(object):
    def __init__(self, loop):
        self.loop = loop
        self._attrs = {}

    def __getitem__(self, item):
        return self._attrs[item]

    def __setitem__(self, key, value):
        self._attrs[key] = value


def main():
    settings.configure("aetherguild.settings")
    basicConfig(level=logging.ERROR)

    # Register our custom password hash function(s)
    register_hash()

    # Load all command files
    CommandLoader.load()

    parser = argparse.ArgumentParser(description='Aetherguild.net CLI')
    subparsers = parser.add_subparsers(title='Commands', help="Command help")

    for cls in CommandLoader.classes:
        command_name = str(cls.__name__).lower()
        sub_parser = subparsers.add_parser(command_name, help=cls.description)
        cls.get_args(sub_parser)
        sub_parser.set_defaults(func=cls.get_instance)

    args = parser.parse_args()

    # Initialize the command object
    command_obj = None
    try:
        command_obj = args.func()
    except AttributeError as e:
        print("Command is missing or not defined.")
        exit(1)

    loop = asyncio.get_event_loop()
    app = Application(loop)
    loop.run_until_complete(init_db(app))
    loop.run_until_complete(init_cache(app))
    loop.run_until_complete(command_obj.on_init())

    try:
        loop.run_until_complete(command_obj.on_run(args, app))
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Shutting down ...")
        loop.shutdown_asyncgens()
        loop.run_until_complete(command_obj.on_close())
        loop.run_until_complete(close_cache(app))
        loop.run_until_complete(close_db(app))
    loop.close()


if __name__ == '__main__':
    main()
