from PhotoObject import Photo
from PhotoStorageManager import PhotoStorageManager

if __name__ == '__main__':
    # test Photo
    test1 = Photo('1', '1', True)
    test2 = Photo('2', '1', False)
    test3 = Photo('1', '1', False)
    # test StorageManager
    manager = PhotoStorageManager()
    manager.add_photo_to_storage(test1)
    manager.add_photo_to_storage(test2)
    manager.add_photo_to_storage(test3)
    print(manager.get_photo_from_storage('2'))


