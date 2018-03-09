from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, Namespace

if False:
    from typing import Text


class BaseCommand(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_name(self):
        # type: () -> Text
        pass

    @abstractmethod
    def get_short_description(self):
        # type: () -> Text
        pass

    @abstractmethod
    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        pass

    @abstractmethod
    def run_command(self, args):
        # type: (Namespace) -> None
        pass
