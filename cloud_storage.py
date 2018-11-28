import json
import os

from libcloud.storage.types import Provider
from libcloud.storage import providers
from libcloud.storage.providers import get_driver
from libcloud.storage.drivers import google_storage
from libcloud.storage.drivers.google_storage import GoogleStorageDriver
#from cloud_storage import CloudStorage
from libcloud.storage.base import Object


class CloudStorage():

  def __init__(self, cloud, key, secret, owner=None, date_str=None):
    """Initializes a GCPCloudStorage object
    
    https://libcloud.readthedocs.io/en/latest/storage/drivers/google_storage.html
    
    Args:
      key: key
      secret: secret key
      owner: owner metadata (default: {None})
      date_str: date created metadata (default: {None})
    """
    self.cloud = cloud
    self.key = key
    self.secret = None
    #self.container_name = 'smcs-123'
    if self.isJson(secret):
      self.secret = secret['private_key']
    else:
      self.secret = secret

    #TODO check if provider is in providers.DRIVERS
    self.cls = None
    if self.cloud in providers.DRIVERS:
      self.cls = get_driver(self.cloud)
    else:
      print("cloud", cloud, "not supported")

    self.driver = self.cls(key=self.key, secret=self.secret)
    self.container = self.driver.get_container(container_name='smcs-123')
    self.containers = self.listContainersWithPrefix('smcs-')
    self.files = []
    self.metaData = {'meta_data': {}}
    self.setMetaData(owner, date_str)
    pass

  def checkConnection(self):
    try:
        self.driver.list_containers()
    except:
      print("ERROR: Failed to connect to cloud:", cloud['cloud'])
      return False

    return True

  def setMetaData(self, owner, date_str, file_name):
    if owner:
      metaData['meta_data']['owner'] = owner
    if date_str:
      metaData['meta_data']['created'] = date_str

  def listContainers(self):
    return self.driver.list_containers()

  def listContainersWithPrefix(self, prefix):
    containerList = driver.list_containers()
    containersWithPrefix = []
    for container in containerList:
      if container.name.startswith(prefix):
       containersWithPrefix.append(container)
    return containersWithPrefix



  def createContainer(self, container_name):
    self.driver.create_container(container_name)

  def deleteContainer(self, container_name):
    self.driver.delete_container(container_name)

  def listObjects(self, container_name):
    self.driver.list_container_objects(container_name)

  def uploadObjectFromFile(self, file_path, file_name):
    upload_object(file_path, container_name, object_name, 
                  extra=None, verify_hash=True, 
                  ex_storage_class=None)

  def uploadObject(self):
    with open(FILE_PATH, 'rb') as iterator:
        obj = driver.upload_object_via_stream(iterator=iterator,
                                              container=container,
                                              object_name='rabbit.svg',
                                              extra=extra)

  def uploadObjects(self):
    pass

  def getFile(self, file_name) -> bytes:
    obj = self.driver.get_object(self.container_name, file_name)
    gen = self.driver.download_object_as_stream(obj)
    file_as_bytes = next(gen)
    return file_as_bytes

  def getFiles(self, files):
    file_list = []
    for f in files:
      file_list.append(getFile(f))

    return file_list

  def isJson(self, myjson):
    try:
      json_object = json.loads(myjson)
    except ValueError:
      return False
    return True


# cls = get_driver(Provider.GOOGLE_STORAGE)
# driver = GoogleStorageDriver(key=client_email, secret=private_key, ...)

# container = driver.get_container(container_name='SMCS')

# extra = {'meta_data': {'owner': 'myuser', 'created': '2018-11-14'}}

# with open(FILE_PATH, 'rb') as iterator:
#     obj = driver.upload_object_via_stream(iterator=iterator,
#                                           container=container,
#                                           object_name='rabbit.svg',
#                                           extra=extra)