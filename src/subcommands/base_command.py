from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser, Namespace


class BaseCommand(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_name(self):
        # type: () -> str
        pass

    @abstractmethod
    def get_short_description(self):
        # type: () -> str
        pass

    @abstractmethod
    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        pass

    @abstractmethod
    def run_command(self, args):
        # type: (Namespace) -> None
        pass
