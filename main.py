#!/usr/bin/python3
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

import cloud_storage

MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

HEADER_LENGTH = 4

# GOOGLE_STORAGE = 'gcp'
# DUMMY = 'dummy'

# DRIVERS = {
#   DUMMY:
#   ('cloud_storage', 'CloudStorage'),
#   GOOGLE_STORAGE:
#   ('gcp_storage', 'GCPCloudStorage')
#   }

# TODO
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
def main():
    file_name = 'test1.txt'
    config_name = 'config_private.json'
    frag_file_path = 'frags/'

    # REMOVE THIS IF YOU WANT TO KEEP FRAGS BETWEEN RUNS
    if os.path.isdir("frags"):
        for f in os.listdir("frags"):
            os.remove(os.path.join("frags", f))

    # here user will input password
    password = "password"
    # random salt is generated (later appended to cipher text)
    salt = generateSalt()
    # generate key from salt and password
    key = generateKey(password, salt)

    # read bytes from files
    plain_text = None
    with open(file_name, 'rb') as f:
        plain_text = readBytesFromFile(f)

    # encrypt plain text to cypher text
    cipher_text = encryptByteArray(plain_text, key, salt)
    #cipher_text = plain_text

    # split into fragments
    fragments = splitIntoFragments(cipher_text, 6)

    # store frags to cloud here
    fragNames = saveFragmentsToDisk(fragments, file_name, frag_file_path)

    # load clouds from config file
    csps = getCloudsFromConfig(config_name)

    # remove conatiners from previous runs
    cleanupClouds(csps, True)

    #pushFragmentsToCloud(fragments, csps, file_name)
    pushFragmentsToCloudFromFiles(fragNames, csps, file_name, frag_file_path)

    # retrieve from cloud here
    array = getFragmentsFromCloud(file_name, csps)
    for i in range(len(array)):
        array[i] = bytearray(array[i])

    # order fragments the right way
    fragsOrdered = orderFragmentsByHeader(array)

    # stitch fragments back together
    cipher_text_bytearray = stitchFragments(fragsOrdered)

    # get salt from file
    salt1 = getAndRemoveSaltFromFile(cipher_text_bytearray)

    # generate key from salt (retrieved from cipher_text) and password
    key1 = generateKey(password, salt1)

    # decrypt ciphertext with key
    plain_text_bytearray = decryptByteArray(cipher_text_bytearray, key1)

    print(plain_text_bytearray)

    with open('test1.output', 'wb') as f2:
        f2.write(plain_text_bytearray)

    # removes the containers from the cloud
    # cleanupClouds(csps)


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
        # insert parity bit
        for fragment in b:
            if parity_counter == num_fragments - 1:
                parity_counter = 0
                frag_counter += 1
            if frag_counter < len(fragment):
                stitched_bytearray.append(fragment[frag_counter])
            parity_counter += 1
        i += 1

    return stitched_bytearray


def generateSalt(length=16) -> bytes:
    salt = os.urandom(16)
    return salt


def generateKey(password: str, salt: bytes) -> bytes:
    # TODO maybe change this in utf16
    if type(password) is not bytes:
        password = password.encode('utf8')
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=default_backend())
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
    return cipher_array


def decryptByteArray(cipher_text: bytearray, key: bytes) -> bytearray:
    # TODO maye don't have to remove salt here?
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
    # TODO add check for num frags size
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
    # TODO add check to see if num of frags we have matches the num in headers

    for frag in fragments:
        fragmentsOrdered[frag[1]] = frag

    return fragmentsOrdered


# This function is not used and I'm not 100% sure it works
# I'm not even sure I got the function signature right
def calculateMissingFragment(arrays: List[bytearray], p: List[bool]) -> bytearray:
    """Calculate a missing fragment

    If 1 fragment is missing from the file, this method can caculate
    that fragment based off the parity bits

    Args:
      fragments: List of bytearrays representing the fragments of the files
      parity: [description]
    """
    b2_recreated = bytearray()
    for i in range(len(arrays[0])):
        if i < len(p):
            b2_recreated.append(arrays[0][i] ^ p[i])

    print("b2_rec " + str(len(b2_recreated)))
    print(b2_recreated)

    result = bytearray()
    for i in range(len(arrays[0])):
        result.append(arrays[0][i])
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

    # if distributed_parity:
    i = 0
    parity_counter = 0
    frag_position = 0
    #parity = bytearray(num_fragments)
    parity_bit_position = num_fragments - 1

    while i < len(b):

        # insert parity bit
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
    #   arrayNum = 0
    #   for frag in outputFragments:
    #   if arrayNum == 0:
    #   parity.append(0)
    #   arrayNum = arrayNum + 1
    #   if i < len(b):
    #   frag.append(b[i])
    #   parity[len(parity)-1] = parity[len(parity)-1] ^ b[i]
    #   i += 1

    # for output in outputFragments:
    #   print(len(output))

    # create parity string
    # for i in range(len(b1)):
    #   if i < len(b2):
    #   p.append(b1[i] ^ b2[i])
    # print("P " + str(len(p)))
    # print(p)

    return outputFragments  # , parity


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
    for cloud in config['clouds']:
        if cloud['cloud'].lower() in providers.DRIVERS:
            cloud['cloud'] = cloud['cloud'].lower()
        else:
            print("ERROR: cloud provider", cloud['cloud'].lower(), "not found")

    return config


def getCloudsFromConfig(config_file: str) -> List[cloud_storage.CloudStorage]:
    config = readConfig(config_file)

    cloud_storage_providers = []

    for cloud in config['clouds']:
        if cloud['cloud'].lower() in providers.DRIVERS:
            c = cloud_storage.CloudStorage(
                cloud['cloud'], cloud['key'], cloud['secret'])
            try:
                c.driver.list_containers()
            except:
                print("ERROR: Failed to connect to cloud:", cloud['cloud'])
                continue
            cloud_storage_providers.append(c)
        else:
            print("ERROR: cloud provider", cloud['cloud'].lower(), "not found")

    return cloud_storage_providers


def saveFragmentsToDisk(fragments: List[bytearray], file_name, file_path='') -> List[str]:
    # returns a list of filenames for the fragments saved to disk
    fragNameList = []
    for frag in fragments:
        frag_name = name = file_name + \
            ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        frag_path = file_path + frag_name
        fragNameList.append(frag_name)
        with open(frag_path, 'wb') as f:
            f.write(frag)
    return fragNameList


def pushFragmentsToCloudFromFiles(fragNameList: List[str], clouds: List[cloud_storage.CloudStorage], file_name: str, frag_path=''):
    cloud_num = 0
    print("Uploading files to cloud...")
    for frag_name in fragNameList:
        clouds[cloud_num].setMetaData(file_name=file_name)
        file_path = frag_path + frag_name
        clouds[cloud_num].uploadObjectFromFile(file_path, frag_name)
        print("File: " + frag_name + " uplaoded to " + clouds[cloud_num].cloud)
        cloud_num += 1
        if cloud_num >= len(clouds):
            cloud_num = 0


# does not currently work for azure because libcloud is stupid
def pushFragmentsToCloud(fragments: List[bytearray], clouds: List[cloud_storage.CloudStorage], file_name: str):
    # name fragments
    cloud_num = 0
    print("Uploading files to cloud...")
    print(file_name)
    for frag in fragments:
        frag_name = name = file_name + \
            ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        print("File: " + frag_name + " uplaoded to " + clouds[cloud_num].cloud)
        clouds[cloud_num].setMetaData(file_name=file_name)
        clouds[cloud_num].uploadObject(frag, frag_name)

        cloud_num += 1
        if cloud_num >= len(clouds):
            cloud_num = 0


def getFragmentsFromCloud(file_name: str, clouds: List[cloud_storage.CloudStorage]):
    # give prefix
    # download all with prefix
    fragments = []

    for cloud in clouds:
        fragments = fragments + cloud.getFilesWithPrefix(file_name)

    return fragments


def cleanupClouds(clouds: List[cloud_storage.CloudStorage], removeExistingContainers: bool):
    for cloud in clouds:
        cloud.cleanUp(removeExistingContainers)


if __name__ == "__main__":
    main()
