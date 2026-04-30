from abc import ABC, abstractmethod


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
        return (f"PlaceholderExpansion[identifier: '{self.identifier}', "
                f"author: '{self.author}', version: '{self.version}']")
