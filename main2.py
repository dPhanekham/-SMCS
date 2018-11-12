#!/usr/bin/python3

import math
import array
import sys

from typing import List, Set, Dict, Tuple, Optional

MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
  sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


#TODO
# get byte array from file
# encrypt
# split into multiple files plus 1 parity
# output files

def main():
  #f = open('test1', 'r')

  with open('test1.txt', 'rb') as f:

    b = readBytesFromFile(f)
    print(b)
    print(len(b))

    fragments, parity = splitIntoFragments(b, 3)

    for frag in fragments:
      print(frag)
    print(parity)

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


def encryptByteArray(b: bytearray) -> bytearray:
  pass

#TODO maybe do this when the fragments are created
def addHeadersToFragments(fragments: List[bytearray]):
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
    if i <  len(b2_recreated):
      result.append(b2_recreated[i])

  print(len(result))
  print(result)
  # print(b2_recreated[len(b2_recreated)-1])
  # with open('result.jpg', 'w') as f2:
  #   f2.write(result.decode('utf8'))


def calculateMissingFragment(arrays: List[bytearray]) -> bytearray:
  pass

def splitIntoFragments(b: bytearray, num_fragments: int, create_parity=True) -> List[bytearray]:
  """[summary]
  
  [description]
  
  Arguments:
    b {bytearray} -- [description]
    num_fragments {int} -- [description]
  
  Keyword Arguments:
    create_parity {bool} -- [description] (default: {True})
  """
  print("length of b:", len(b))
  print("b mod num_fragments:", (len(b) % num_fragments))
  outputFragments = []
  parity = bytearray()

  for i in range(num_fragments):
    outputFragments.append(bytearray())

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
