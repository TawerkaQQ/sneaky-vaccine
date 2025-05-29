from PhotoStorage import ProcessedPhotoStorage, UnProcessedPhotoStorage
from PhotoObject import Photo

class PhotoStorageManager:
    def __init__(self):
        self.processed_photo_storage = ProcessedPhotoStorage()
        self.unprocessed_photo_storage = UnProcessedPhotoStorage()
    
    def add_photo_to_storage(self, photo: Photo):
        if photo.is_processed:
            self.processed_photo_storage.add_photo_to_storage(photo)
        elif not photo.is_processed:
            self.unprocessed_photo_storage.add_photo_to_storage(photo)
        return self
    
    def form_photo_object(self):
        pass

    def get_photo_from_storage(self, uid: str, is_processed: bool = None) -> Photo | list[Photo]:
        if is_processed is None:
            processed_photo = self.processed_photo_storage.get_photo_from_storage(uid)
            unprocessed_photo = self.unprocessed_photo_storage.get_photo_from_storage(uid)
            return [processed_photo, unprocessed_photo]
        if is_processed:
            return self.processed_photo_storage.get_photo_from_storage(uid)
        if not is_processed:
            return self.unprocessed_photo_storage.get_photo_from_storage(uid)
