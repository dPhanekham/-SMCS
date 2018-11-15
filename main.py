#!/usr/bin/python3

import math
import array
import sys
import base64
import os

from typing import List, Set, Dict, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import cloud_storage


MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
  sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

HEADER_LENGTH = 4

#TODO
# Add check for number of fragments
#   should be less <= 65536
#   should be less than bytes in file
# Add check for missing fragments


# ORDER OF OPERATIONS
# get password from user
# get file from user
# get clouds from user
# get number of fragments from user
# generate salt
# generate key from password and salt
# get byte array from file
# encrypt byte array
# append salt
# create headers for files
# split into multiple files plus 1 parity
# output files
# 

def main():
  #f = open('test1', 'r')
  password = "password"
  salt = generateSalt()
  key = generateKey(password, salt)
  print(key)
  print(salt)

  c = cloud_storage.CloudStorage()


  #key = Fernet.generate_key()

  with open('rabbit.svg', 'rb') as f:

    plain_text = readBytesFromFile(f)
    cipher_text = encryptByteArray(plain_text, key, salt)
    print(cipher_text)
    #cipher_text = plain_text
    fragments, parity = splitIntoFragments(cipher_text, 6, distributed_parity=True)

    for frag in fragments:
      print(frag)
    print(parity)

    cipher_text_bytearray = stitchFragments(fragments)
    print(cipher_text_bytearray)

    salt1 = getAndRemoveSaltFromFile(cipher_text_bytearray)
    print(cipher_text_bytearray)
    key1 = generateKey(password, salt1)
    plain_text_bytearray = decryptByteArray(cipher_text_bytearray, key1)

    print(plain_text_bytearray)
    with open('result.svg', 'wb') as f2:
      f2.write(plain_text_bytearray)


def readBytesFromFile(file) -> bytearray:
  b = bytearray(file.read())
  return b


def stitchFragments(b: List[bytearray], parity: bytearray) -> bytearray:
  pass

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


def orderFragmentsByHeader(fragments: List[bytearray]):
  pass
  

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



def splitIntoFragments(b: bytearray, num_fragments: int, distributed_parity=False) -> List[bytearray]:
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
  #TODO add header to fragments here
  addHeadersToFragments(outputFragments, 
                        num_fragments, 
                        total_file_length_bytes,
                        distributed_parity) 

  if distributed_parity:
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


  else:
    i = 0
    while i < len(b):
      arrayNum = 0
      for frag in outputFragments:
        if arrayNum == 0:
          parity.append(0)
          arrayNum = arrayNum + 1
        if i < len(b):
          frag.append(b[i])
          parity[len(parity)-1] = parity[len(parity)-1] ^ b[i]
          i += 1

  for output in outputFragments:
    print(len(output))


  #create parity string
  # for i in range(len(b1)):
  #   if i < len(b2):
  #     p.append(b1[i] ^ b2[i])
  # print("P " + str(len(p)))
  # print(p)

  return outputFragments, parity
  

  

if __name__ == "__main__":
  main()
