from abc import ABC, abstractmethod

class AbstractPhoto(ABC):
    def __init__(self, uid: str, base64_photo: str, is_processed: bool):
        self._uid = uid
        self.base64_photo: str = base64_photo

    @property
    def uid(self) -> str:
        return self._uid

    @property
    @abstractmethod
    def is_processed(self) -> bool:
        pass

class Photo(AbstractPhoto):
    def __new__(cls, uid: str, base64_photo: str, is_processed: bool):
        if is_processed:
            return super().__new__(ProcessedPhoto)
        if not is_processed:
            return super().__new__(UnprocessedPhoto)

class ProcessedPhoto(Photo):
    @property
    def is_processed(self) -> bool:
        return True

class UnprocessedPhoto(Photo):
    @property
    def is_processed(self) -> bool:
        return False
