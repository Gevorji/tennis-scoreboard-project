from abc import ABC, abstractmethod
from typing import Collection

class StorageServiceABC(ABC):

    @abstractmethod
    def fetch(self, obj_type):
        pass

    @abstractmethod
    def place(self, obj):
        pass

    @abstractmethod
    def remove(self, obj):
        pass
