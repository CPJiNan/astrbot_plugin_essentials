from abc import ABC, abstractmethod
from typing import List


class PlaceholderExpansion(ABC):

    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    @property
    def author(self) -> str:
        return "unknown"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def name(self) -> str:
        return self.identifier

    @property
    def placeholders(self) -> List[str]:
        return []

    @abstractmethod
    def on_request(self, params: str) -> str:
        pass

    def can_register(self) -> bool:
        return True

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, PlaceholderExpansion):
            return False
        return (self.identifier == other.identifier
                and self.author == other.author
                and self.version == other.version)

    def __repr__(self):
        return (f"PlaceholderExpansion[name: '{self.name}', "
                f"author: '{self.author}', version: '{self.version}']")
