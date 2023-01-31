from abc import abstractmethod
from argparse import ArgumentParser, Namespace

from type_utils import ABC
from typing import Text


class BaseCommand(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_short_description(self) -> str:
        pass

    @abstractmethod
    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        pass

    @abstractmethod
    def run_command(self, args: Namespace) -> None:
        pass
