from enum import Enum

from protocol.storage.data_storage import DataStorage
from protocol.storage.file_system_storage import FileSystemStorage
from protocol.utils.config_utils import load_config


class StorageType(Enum):
    S3 = 1
    FS = 2


class StorageFactory:
    @staticmethod
    def get_storage(storage_type: int):
        match StorageType(storage_type):
            case StorageType.S3:
                return DataStorage(load_config()["STORAGE"]["BucketName"])
            case StorageType.FS:
                return FileSystemStorage()
