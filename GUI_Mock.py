import math
import array
import sys
import base64
import os
import json
import random
import string

from typing import List, Set, Dict, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from libcloud.storage.types import Provider
from libcloud.storage import providers

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import cloud_storage
import gcp_storage
import main

class Ui_Form(object):
    
    def readFile(self, fileName):
        if (fileName == ''):
            return " "
        file = open(fileName, 'r')
        return file.readline()
 
    
    def setupUi(self, Form):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        # Create Label for Config File Input
        self.textLabel = QLabel(self)
        self.textLabel.setText("Please Enter the Config File Name: ")
#        self.textLabel.resize(280,20)
#        self.textLabel.move(20,0)
        
        # Create textbox for config File Input
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,20)
 
        # Create a button to get Config File
        self.button = QPushButton('Retrieve Config', self)
        self.button.resize(120,30)
        self.button.move(20,80)
        
        # Create a button to Push a file into Cloud
        self.button2 = QPushButton('Add File', self)
        self.button2.resize(120,30)
        self.button2.move(140,80)
        
        # Create a button to Update Files in Cloud
        self.button4 = QPushButton('Update File List', self)
        self.button4.resize(120,30)
        self.button4.move(260,60)
        
        # Create a button to Retrieve from Cloud
        self.button3 = QPushButton('Retrieve File', self)
#        self.button3.resize(120,30)
#        self.button3.move(260,80)
        
        
        # Add a Text Box Saying what file is being uploaded
        self.uploadConfirm = QLabel(self)
        self.uploadConfirm.setText("File to upload: None")
        self.uploadConfirm.setWordWrap(True)
#        self.uploadConfirm.resize(600,40)
#        self.uploadConfirm.move(20,40)
        
        
        # Add in area with Files in Cloud
        self.remoteFiles = QLabel(self)
        self.remoteFiles.setText("Files in cloud: ")
#        self.remoteFiles.resize(400,400)
#        self.remoteFiles.move(20,50)
 
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        
        self.button4.clicked.connect(self.on_click2)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.button4,1,QtCore.Qt.AlignLeft)
        hbox.addStretch(1)
        hbox.addWidget(self.button2)
        hbox.addWidget(self.button3)
        
        hbox2 =QHBoxLayout()
        hbox2.addWidget(self.button,1,QtCore.Qt.AlignLeft)
        
        
        
        
        
        hbox4 =QHBoxLayout()
        hbox4.addWidget(self.textLabel)
        hbox4.addWidget(self.textbox,QtCore.Qt.AlignLeft)
        
        
        
        hbox6 =QHBoxLayout()
        hbox6.addWidget(self.uploadConfirm)
        hbox7 =QHBoxLayout()
        hbox7.addWidget(self.remoteFiles)
        
       


        vbox = QVBoxLayout()
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox2)

        
#        vbox.addLayout(hbox3)
        
         

        vbox.addLayout(hbox6)

        vbox.addLayout(hbox7)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        

        
        
        self.setLayout(vbox)
         
        
#        self.setGeometry(300, 300, 300, 150)
#        self.setWindowTitle('Buttons')    
        self.show()
       

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "PushButton"))
        
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        if(textboxValue != "" and os.path.exists(textboxValue)):
            
            QMessageBox.question(self, 'Message - Cloud Storage', "Your Config File is: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
            self.textbox.setText(textboxValue)
            csps = getCloudsFromConfig(textboxValue)
            print(csps)

        else:
            self.textbox.setText("")
        
    @pyqtSlot()
    def on_click2(self):
        self.remoteFiles.setText("File in cloud: None")

 


class Widget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.title = 'CSE 8377 Cloud Storage'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 600
        self.setupUi(self)
        self.button2.clicked.connect(self.openFile)

    def openFile(self):   
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName == "":
            self.uploadConfirm.setText("File to upload: None")
        if fileName != "":
            buttonReply = QMessageBox.question(self, 'Message - Cloud Storage', "You are wanting to upload: " + fileName, QMessageBox.Yes, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')
                self.uploadConfirm.setText("File to upload: " + fileName)
            if buttonReply == QMessageBox.No:
                print('No clicked.')
                self.uploadConfirm.setText("File to upload: None")
            if buttonReply == QMessageBox.Cancel:
                print('Cancel')
                self.uploadConfirm.setText("File to upload: None")

def readBytesFromFile(file) -> bytearray:
  b = bytearray(file.read())
  return b


def stitchFragments(b: List[bytearray]) -> bytearray:
  
  stitched_bytearray = bytearray()
  total_length = 0
  num_fragments = len(b)

  for fragment in b:
    del fragment[0:HEADER_LENGTH]
    total_length += len(fragment)

  for fragment in b:
    print(fragment)

  i = 0
  parity_counter = 0
  #frag_position = 0
  frag_counter = 0
  #parity = bytearray(num_fragments)
  parity_bit_position = num_fragments - 1

  while i < total_length:
    #insert parity bit
    for fragment in b:
      if parity_counter == num_fragments - 1:
        parity_counter = 0
        frag_counter += 1
      if frag_counter < len(fragment):
        stitched_bytearray.append(fragment[frag_counter])
      parity_counter += 1
    i += 1

  return stitched_bytearray


def generateSalt(length = 16) -> bytes:
  salt = os.urandom(16)
  return salt

def generateKey(password: str, salt: bytes) -> bytes:
  #TODO maybe change this in utf16
  if type(password) is not bytes:
    password = password.encode('utf8')
  print(password)
  kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
        )
  key = base64.urlsafe_b64encode(kdf.derive(password))
  return key

def concatSaltWithFile(cipher_text: bytearray, salt: bytes):
  cipher_text.extend(salt)
  

def getAndRemoveSaltFromFile(cipher_text: bytearray) -> bytes:
  salt = bytes(cipher_text[len(cipher_text) - 16:])
  del cipher_text[len(cipher_text) - 16:]
  return salt


def encryptByteArray(plain_text: bytearray, key: bytes, salt: bytes) -> bytearray:
  cipher_suite = Fernet(key)
  cipher_text = cipher_suite.encrypt(bytes(plain_text))
  cipher_array = bytearray(cipher_text)
  concatSaltWithFile(cipher_array, salt)
  print(cipher_array)
  return cipher_array


def decryptByteArray(cipher_text: bytearray, key: bytes) -> bytearray:
  #TODO maye don't have to remove salt here?
  cipher_suite = Fernet(key)
  plain_text = cipher_suite.decrypt(bytes(cipher_text))
  return plain_text


# TODO maybe do this when the fragments are created
def addHeadersToFragments(fragments: List[bytearray], num_fragments: int,
                          total_file_length_bytes: int, distributed_parity: bool):
  """Add headers to fragments.
  
  Add headers to all fragments.
  Current header is 4 bytes
  currently header includes
    -total fragments
    -position
    -total_file_length % num_fragments
    -placeholder
  
  Args:
    fragments: List of bytearrays
  """
  #TODO add check for num frags size
  last_block = total_file_length_bytes % num_fragments

  for i in range(num_fragments):
    fragments[i].append(num_fragments)
    fragments[i].append(i)
    fragments[i].append(last_block)
    fragments[i].append(distributed_parity)

# def removeHeadersFromFragments(fragments: List[bytearray]):
#   pass

def deleteLocalFragments(file_name, frag_path):
  pass


def orderFragmentsByHeader(fragments: List[bytearray]) -> List[bytearray]:
  
  fragmentsOrdered = [None] * len(fragments)
  print("LENGTH FRAGMENTS:", len(fragments))
  print("LENGTH FRAGMENTSORDERED:", len(fragmentsOrdered))
  #TODO add check to see if num of frags we have matches the num in headers

  for frag in fragments:
    fragmentsOrdered[frag[1]] = frag

  return fragmentsOrdered



def calculateMissingFragment(arrays: List[bytearray]) -> bytearray:
  """Calculate a missing fragment
  
  If 1 fragment is missing from the file, this method can caculate
  that fragment based off the parity bits
  
  Args:
    fragments: List of bytearrays representing the fragments of the files
    parity: [description]
  """
  b2_recreated = bytearray()
  for i in range(len(outputArrays[0])):
    if i < len(p):
      b2_recreated.append(outputArrays[0][i] ^ p[i])

  print("b2_rec " + str(len(b2_recreated)))
  print(b2_recreated)

  result = bytearray()
  for i in range(len(outputArrays[0])):
    result.append(outputArrays[0][i])
    if i < len(b2_recreated):
      result.append(b2_recreated[i])

  print(len(result))
  print(result)
  # print(b2_recreated[len(b2_recreated)-1])
  # with open('result.jpg', 'w') as f2:
  #   f2.write(result.decode('utf8'))

def splitIntoFragments(b: bytearray, num_fragments: int) -> List[bytearray]:
  """[summary]
  
  [description]
  
  Arguments:
    b {bytearray} -- [description]
    num_fragments {int} -- [description]
  
  Keyword Arguments:
    create_parity {bool} -- [description] (default: {True})
  """
  print("length of b:", len(b))
  total_file_length_bytes = len(b)
  print("len(b) mod num_fragments:", (len(b) % num_fragments))
  outputFragments = []
  parity = bytearray()

  for i in range(num_fragments):
    outputFragments.append(bytearray())

  addHeadersToFragments(outputFragments, 
                        num_fragments, 
                        total_file_length_bytes,
                        True) 

  #if distributed_parity:
  i = 0
  parity_counter = 0
  frag_position = 0
  #parity = bytearray(num_fragments)
  parity_bit_position = num_fragments - 1

  while i < len(b):

    #insert parity bit
    if parity_counter == num_fragments - 1:
      parity = 0
      for byte in b[i - (num_fragments - 1):i]:
        parity = parity ^ byte
      outputFragments[frag_position].append(parity)
      parity_counter = 0

    outputFragments[frag_position].append(b[i])
    frag_position += 1
    parity_counter += 1

    if frag_position >= num_fragments:
      frag_position = 0

    i += 1


  # else:
  #   i = 0
  #   while i < len(b):
  #     arrayNum = 0
  #     for frag in outputFragments:
  #       if arrayNum == 0:
  #         parity.append(0)
  #         arrayNum = arrayNum + 1
  #       if i < len(b):
  #         frag.append(b[i])
  #         parity[len(parity)-1] = parity[len(parity)-1] ^ b[i]
  #         i += 1

  # for output in outputFragments:
  #   print(len(output))


  #create parity string
  # for i in range(len(b1)):
  #   if i < len(b2):
  #     p.append(b1[i] ^ b2[i])
  # print("P " + str(len(p)))
  # print(p)

  return outputFragments  #, parity
  

def readConfig(config_file: str):
  config = None
  with open(config_file, 'r') as f:
    config = f.read()
  #config_dict = None
  try:
    config = json.loads(config)
  except ValueError as e:
    print("Config File needs to be properly formatted JSON")
    print("Error:", e)
  print(config)
  for cloud in config['clouds']:
    if cloud['cloud'].lower() in providers.DRIVERS:
      cloud['cloud'] = cloud['cloud'].lower()
      print("something")
    else:
      print("ERROR: cloud provider", cloud['cloud'].lower(), "not found")

  return config

def getCloudsFromConfig(config_file: str) -> List[cloud_storage.CloudStorage]:
  config = readConfig(config_file)

  cloud_storage_providers = []

  for cloud in config['clouds']:
    if cloud['cloud'].lower() in providers.DRIVERS:
      c = cloud_storage.CloudStorage(cloud['cloud'], cloud['key'], cloud['secret'])
      try:
        c.driver.list_containers()
      except:
        print("ERROR: Failed to connect to cloud:", cloud['cloud'])
        continue
      cloud_storage_providers.append(c)
    else:
      print("ERROR: cloud provider", cloud['cloud'].lower(), "not found")

  return cloud_storage_providers

def saveFragmentsToDisk(fragments: List[bytearray], file_name, file_path = '') -> List[str]:
  #returns a list of filenames for the fragments saved to disk
  fragNameList = []
  for frag in fragments:
    frag_name = name = file_name + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    frag_path = file_path + frag_name
    fragNameList.append(frag_name)
    with open(frag_path, 'wb') as f:
      f.write(frag)
  return fragNameList

def pushFragmentsToCloudFromFiles(fragNameList: List[str], clouds: List[cloud_storage.CloudStorage],
                                  file_name: str, frag_path=''):
  cloud_num = 0
  print("PUSH TO CLOUD")
  print(file_name)
  for frag_name in fragNameList:
    print(frag_name)
    clouds[cloud_num].setMetaData(file_name=file_name)
    file_path = frag_path + frag_name
    print(file_path)
    clouds[cloud_num].uploadObjectFromFile(file_path, frag_name)
    cloud_num += 1
    if cloud_num >= len(clouds):
      cloud_num = 0


#does not currently work for azure because libcloud is stupid
def pushFragmentsToCloud(fragments: List[bytearray], clouds: List[cloud_storage.CloudStorage], file_name: str):
  #name fragments
  cloud_num = 0
  print("PUSH TO CLOUD")
  print(file_name)
  for frag in fragments:
    frag_name = name = file_name + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    print(frag_name)
    print(clouds[cloud_num])
    clouds[cloud_num].setMetaData(file_name=file_name)
    clouds[cloud_num].uploadObject(frag, frag_name)

    cloud_num += 1
    if cloud_num >= len(clouds):
      cloud_num = 0

def getFragmentsFromCloud(file_name: str, clouds: List[cloud_storage.CloudStorage]):
  #give prefix
  #download all with prefix
  fragments = []

  for cloud in clouds:
    fragments = fragments + cloud.getFilesWithPrefix(file_name)

  return fragments

                
                

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = Widget()
    ui = Ui_Form()
    Form.show()
    sys.exit(app.exec_())