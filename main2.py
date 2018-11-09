#!/usr/bin/python3

import math
import array
import sys

# MIN_PYTHON = (3, 6)
# if sys.version_info < MIN_PYTHON:
#   sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


#TODO
# get byte array from file
# encrypt
# split into 2 files plus 1 parity
# output files

def main():
  #f = open('test1', 'r')

  with open('dude.jpg', 'rb') as f:

    b = bytearray(f.read())  
    print(b)
    print(len(b))

    splitByteArray(b, 2)
    # while fileIn1:
    #   fileIn1 = f.read(1)
    #   fileIn2 = f.read(1)
    #   string1 = string1 + fileIn1
    #   string2 = string2 + fileIn2
    # b1 = bytearray(string1, 'utf8')
    # b2 = bytearray(string2, 'utf8')
    # p = array.array('B', [])
    # print("B1 " + str(len(b1)))
    # print(b1)
    # print("B2 " + str(len(b2)))
    # print(b2)

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

def encryptByteArray(b: bytearray) -> bytearray:
  pass


def splitByteArray(b: bytearray, num_splits: int, create_parity=True):
  """[summary]
  
  [description]
  
  Arguments:
    b {bytearray} -- [description]
    num_splits {int} -- [description]
  
  Keyword Arguments:
    create_parity {bool} -- [description] (default: {True})
  """

  p = array.array('B', [])
  print("B1 " + str(len(b1)))
  print(b1)
  print("B2 " + str(len(b2)))
  print(b2)

  p = bytearray()
  #create parity string
  for i in range(len(b1)):
    if i < len(b2):
      p.append(b1[i] ^ b2[i])
  print("P " + str(len(p)))
  print(p)
  

  b2_recreated = bytearray()
  for i in range(len(b1)):
    if i < len(p):
      b2_recreated.append(b1[i] ^ p[i])

  print("b2_rec " + str(len(b2_recreated)))
  print(b2_recreated)

  result = bytearray()
  for i in range(len(b1)):
    result.append(b1[i])
    if i <  len(b2_recreated):
      result.append(b2_recreated[i])

  print(len(result))
  print(b2_recreated[len(b2_recreated)-1])
  with open('result.jpg', 'w') as f2:
    f2.write(result.decode('utf8'))


if __name__ == "__main__":
  main()
