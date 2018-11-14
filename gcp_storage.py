from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver

from cloud_storage import CloudStorage

class GCPCloudStorage(CloudStorage):

  def __init__(self):
    super().__init__(self)
    pass

  def listFiles(self):
    pass

  def uploadFile(self):
    pass

  def uploadFiles(self):
    pass

  def getFile(self):
    pass

  def getFiles(self):
    pass