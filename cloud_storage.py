import json
import os
import string
import random

from libcloud.storage.types import Provider
from libcloud.storage import providers
from libcloud.storage.providers import get_driver
from libcloud.storage.drivers import google_storage
from libcloud.storage.drivers.google_storage import GoogleStorageDriver
#from cloud_storage import CloudStorage
from libcloud.storage.base import Object
from typing import List, Set, Dict, Tuple, Optional


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
    self.container = None
    self.containers = self.listContainersWithPrefix('smcs-')
    print(self.containers)
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

  def setMetaData(self, owner, date_str, file_name = None):
    if owner:
      metaData['meta_data']['owner'] = owner
    if date_str:
      metaData['meta_data']['created'] = date_str
    if file_name:
      metaData['meta_data']['file_name'] = file_name

  def listContainers(self):
    return self.driver.list_containers()

  def listContainersWithPrefix(self, prefix):
    containerList = self.driver.list_containers()
    containersWithPrefix = []
    for container in containerList:
      if container.name.startswith(prefix):
       containersWithPrefix.append(container)
    return containersWithPrefix



  def createContainer(self, container_name=None):
    if container_name:
      self.driver.create_container(container_name)
    else:
      name = 'smcs-' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
      self.driver.create_container(name)

  def deleteContainer(self, container):
    self.driver.delete_container(container)

  def listObjects(self, container):
    self.driver.list_container_objects(container)

  def listObjectsWithPrefix(self, container):
    objList = self.driver.list_container_objects(container)
    objsWithPrefix = []
    for obj in objList:
      if obj.name.startswith(prefix):
       objsWithPrefix.append(obj)
    return objsWithPrefix

  def uploadObjectFromFile(self, file_path, file_name, container):
    upload_object(file_path, container, object_name, 
                  extra=None, verify_hash=True, 
                  ex_storage_class=None)

  def uploadObject(self, container, fragment: bytearray):
    iterator = iter(fragment)
    obj = driver.upload_object_via_stream(iterator=iterator,
                                          container=container,
                                          object_name='rabbit.svg',
                                          extra=extra)

  def uploadObjects(self):
    pass

  def getFile(self, file_name: str) -> bytes:
    """Gets a File from cloud given the filename
  
    Gets a file from the cloud given the exact name of the file
  
    Arguments:
    file_name {str} -- name of file to download

    Returns:
      bytes -- returns file as immutable bytes object
    """
    obj = self.driver.get_object(self.container_name, file_name)
    gen = self.driver.download_object_as_stream(obj)
    file_as_bytes = next(gen)
    return file_as_bytes

  def getFiles(self, file_names: List[str]) -> List[bytes]:
    """Gets multiple files given their filenames
    
    Calls getFile method for each filename in list
    
    Arguments:
      file_names {List[str]} list of filenames of files to retrieve
    
    Returns:
      List[bytes] -- returns files as list of bytes objects
    """
    file_list = []
    for f in file_names:
      file_list.append(getFile(f))

    return file_list

  def getFilesFromObjectList(self, objects):
    """Gets files given a list of libcloud.storage.base.Object objects
       Great naming there apache.
    
    Arguments:
      objects {List[Objects]} -- list of libcloud.Object objects
    
    Returns:
      List[bytes] -- returns files as list of bytes objects
    """
    file_list = []
    for obj in objects:
      gen = self.driver.download_object_as_stream(obj)
      file_as_bytes = next(gen)
      file_list.append(file_as_bytes)

    return file_list


  def getFilesWithPrefix(self, prefix):
    objs = listObjectsWithPrefix(prefix)
    return getFilesFromObjectList(objs)


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