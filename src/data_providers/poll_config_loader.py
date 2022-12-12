from abc import ABC, abstractmethod

from models.templates import PollConfig


class PollConfigLoaderBase(ABC):
    @abstractmethod
    def load_template(self) -> PollConfig:
        pass


class JsonPollConfigLoader(PollConfigLoaderBase):
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load_template(self) -> PollConfig:
        return PollConfig.parse_file(self.config_path)
