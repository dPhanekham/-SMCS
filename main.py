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


MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
  sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

#TODO
# Add check for number of fragments
#   should be less <= 65536
#   should be less than bytes in file

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


  #key = Fernet.generate_key()

  with open('test1.txt', 'rb') as f:

    plain_text = readBytesFromFile(f)
    cipher_text = encryptByteArray(plain_text, key, salt)

    fragments, parity = splitIntoFragments(cipher_text, 3)

    for frag in fragments:
      print(frag)
    print(parity)

    plain_text_bytearray = stitchFragments(fragments, parity)

    #recreateMissingArray(parts, parity)

    # p = bytearray()
    # #create parity string
    # for i in range(len(b1)):
    #   if i < len(b2):
    #     p.append(b1[i] ^ b2[i])
    # print("P " + str(len(p)))
    # print(p)
    

    # b2_recreated = bytearray()
    # for i in range(len(b1)):
    #   if i < len(p):
    #     b2_recreated.append(b1[i] ^ p[i])

    # print("b2_rec " + str(len(b2_recreated)))
    # print(b2_recreated)

    # result = bytearray()
    # for i in range(len(b1)):
    #   result.append(b1[i])
    #   if i <  len(b2_recreated):
    #     result.append(b2_recreated[i])

    # print(len(result))
    # print(b2_recreated[len(b2_recreated)-1])
    # with open('result.jpg', 'w') as f2:
    #   f2.write(result.decode('utf8'))


def readBytesFromFile(file) -> bytearray:
  b = bytearray(file.read())
  return b


def stitchFragments(b: List[bytearray], parity: bytearray) -> bytearray:
  pass

def stitchFragments(b: List[bytearray]) -> bytearray:
  pass

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
  cipher_text = cipher_text[0:len(cipher_text) - 16]
  return salt


def encryptByteArray(plain_text: bytearray, key: bytes, salt: bytes) -> bytearray:
  cipher_suite = Fernet(key)
  cipher_text = cipher_suite.encrypt(bytes(plain_text))
  cipher_array = bytearray(cipher_text)
  concatSaltWithFile(cipher_array, salt)
  return cipher_array


def decryptByteArray(cipher_text: bytearray, key: bytes) -> bytearray:
  cipher_suite = Fernet(key)
  plain_text = cipher_suite.decrypt(cipher_text)
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


def calculateMissingFragment(fragments: List[bytearray], parity: bytearray) -> bytearray:
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


def calculateMissingFragment(arrays: List[bytearray]) -> bytearray:
  pass


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

  # if distributed_parity:
  #   i = 0
  #   while i < len(b):
  #     x = 0
  #     parity_bit_position = num_fragments - 1
  #     parity = bytearray(num_fragments)
  #     while x < num_fragments:
  #       parity

  # else:
  #   pass
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
        i = i + 1

  for output in outputFragments:
    print(len(output))

  print(len(parity))

  #create parity string
  # for i in range(len(b1)):
  #   if i < len(b2):
  #     p.append(b1[i] ^ b2[i])
  # print("P " + str(len(p)))
  # print(p)

  return outputFragments, parity
  

  

if __name__ == "__main__":
  main()
