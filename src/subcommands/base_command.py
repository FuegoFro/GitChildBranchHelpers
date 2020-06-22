from abc import abstractmethod
from argparse import ArgumentParser, Namespace

from type_utils import ABC, MYPY

if MYPY:
    from typing import Text


class BaseCommand(ABC):
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
