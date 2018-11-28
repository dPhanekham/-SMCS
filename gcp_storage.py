import json
import os

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from libcloud.storage.drivers import google_storage
from libcloud.storage.drivers.google_storage import GoogleStorageDriver
from cloud_storage import CloudStorage
from libcloud.storage.base import Object

class GCPCloudStorage(CloudStorage):

  def __init__(self, key, secret, owner=None, date_str=None):
    super().__init__(self)
    """Initializes a GCPCloudStorage object
    
    https://libcloud.readthedocs.io/en/latest/storage/drivers/google_storage.html
    
    Args:
      key: service account email
      secret: service account private key
      owner: owner metadata (default: {None})
      date_str: date created metadata (default: {None})
    """
    self.key = key
    self.secret = None
    self.container_name = 'smcs-123'
    if isJson(secret):
      self.secret = secret['private_key']
    else:
      self.secret = secret

    self.driver = GoogleStorageDriver(key=self.key, secret=self.secret)
    self.container = driver.get_container(container_name='smcs-123')
    self.metaData = {'meta_data': {}}
    setMetaData(owner, date_str)
    pass

  def setMetaData(self, owner, date_str, object_name):
    if owner:
      metaData['meta_data']['owner'] = owner
    if date_str:
      metaData['meta_data']['created'] = date_str

    metaData['meta_data'][''] = object_name

  def createContainer(self, container_name):
    self.driver.create_container(container_name)

  def deleteContainer(self, container_name):

    self.driver.delete_container()

  def listFiles(self, container_name):
    pass

  def uploadFile(self):
    pass

  def uploadFiles(self):
    pass

  def getFile(self, file_name) -> bytes:
    obj = driver.get_object(self.container_name, file_name)
    gen = driver.download_object_as_stream(obj)
    file_as_bytes = next(gen)
    return file_as_bytes

  def getFiles(self, files):
    file_list = []
    for f in files:
      file_list.append(getFile(f))

  def isJson(myjson):
    try:
      json_object = json.loads(myjson)
    except ValueError:
      return False
    return True




# FILE_PATH = 'rabbit.svg'

# cls = get_driver(Provider.GOOGLE_STORAGE)
# driver = GoogleStorageDriver(key=client_email, secret=private_key, ...)

# container = driver.get_container(container_name='SMCS')

# extra = {'meta_data': {'owner': 'myuser', 'created': '2018-11-14'}}

# with open(FILE_PATH, 'rb') as iterator:
#     obj = driver.upload_object_via_stream(iterator=iterator,
#                                           container=container,
#                                           object_name='rabbit.svg',
#                                           extra=extra)