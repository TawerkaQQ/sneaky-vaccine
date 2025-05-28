from PhotoObject import Photo

class PhotoStorage:
    def __init__(self):
        self.storage = {}

    def add_photo_to_storage(self, photo: Photo):
        photo_to_update = {photo.uid: photo}
        self.storage.update(photo_to_update)
        return self

    def get_photo_from_storage(self, uid: str):
        return self.storage.get(uid)

class ProcessedPhotoStorage(PhotoStorage):
    pass

class UnProcessedPhotoStorage(PhotoStorage):
    pass
