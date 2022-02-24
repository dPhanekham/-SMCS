#!/usr/bin/python3
import math
from re import S
import sys
import base64
import os
import json
import random
import string
import time

import multiprocessing as mp

from typing import List
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from libcloud.storage import providers

import cloud_storage

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

HEADER_LENGTH = 4

# TODO
# Add check for number of fragments
#   should be less <= 65536
#   should be less than bytes in file
# Add check for missing fragments
# Add block length, might speed things up


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

def SMCS():

    block_length = 4

    # file for recording runtimes
    file = open("runtime.txt", "w")

    file_name = 'plex.spk'
    #file_name = 'setSizeFiles/1MB'
    #file_name = 'test1.txt'
    config_name = 'config.json'
    frag_file_path = 'frags/'
    start_time = 0

    # Deletes the frags from the previous run
    deleteLocalFragments(file_name, frag_file_path)

    start_time = time.time()

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
    # print(f'CIPHERTEXT: {cipher_text}')
    # split into fragments

    distributed_parity = False

    print('Creating fragments...')
    fragments = splitIntoFragments(cipher_text, block_length, 6, distributed_parity=distributed_parity)
    
    # print("\nFRAGMENTS")
    # for fragment in fragments:
    #     print(fragment[4:])
    # store frags to cloud here
    fragNames = saveFragmentsToDisk(fragments, file_name, frag_file_path)

    print('Time to create fragments: ' + str(math.trunc((time.time() - start_time) * 1000)) + ' ms')
    file.write(str(math.trunc((time.time() - start_time) * 1000)) + ', ')

    #print('\nPushing fragments to clouds...')

    # load clouds from config file
    #csps = getCloudsFromConfig(config_name)

    # remove conatiners from previous runs
    #cleanupClouds(csps, True)

    start_time = time.time()

    # OLD
    #pushFragmentsToCloudFromFiles(fragNames, csps, file_name, frag_file_path)
    # NEW, use this one
    #pushFragmentsToCloudFromFilesNew(fragNames, csps, file_name, frag_file_path)

    #print('Time to push fragments to clouds: ' + str(math.trunc((time.time() - start_time) * 1000)) + ' ms')
    file.write(str(math.trunc((time.time() - start_time) * 1000)) + ', ')
    start_time = time.time()

    # retrieve from cloud here
    #print('\nRetreiving fragments from clouds...')
    #array = getFragmentsFromCloud(file_name, csps)
    #for i in range(len(array)):
    #    array[i] = bytearray(array[i])

    # Bypass cloud stuff
    array = fragments

    # print time to retrieve fragments
    #print('Time to retrieve fragments: ' + str(math.trunc((time.time() - start_time) * 1000)) + ' ms')
    file.write(str(math.trunc((time.time() - start_time) * 1000)) + ', ')
    start_time = time.time()

    print('\nReassembling fragments...')

    # order fragments the right way
    fragsOrdered = orderFragmentsByHeader(array)

    # TODO check header for parity distribution
    distributed_parity = False

    # stitch fragments back together
    cipher_text_bytearray = stitchFragments(fragsOrdered, block_length, distributed_parity=distributed_parity)

    # get salt from file
    salt1 = getAndRemoveSaltFromFile(cipher_text_bytearray)

    # generate key from salt (retrieved from cipher_text) and password
    key1 = generateKey(password, salt1)

    # decrypt ciphertext with key
    plain_text_bytearray = decryptByteArray(cipher_text_bytearray, key1)

    #print('\nReconstructed input:')
    # print(plain_text_bytearray)

    with open('output.txt', 'wb') as f2:
        f2.write(plain_text_bytearray)

    print('Time to reassemble fragments: ' + str(math.trunc((time.time() - start_time) * 1000)) + ' ms')
    file.write(str(math.trunc((time.time() - start_time) * 1000)) + '\n')
    file.close()


def readBytesFromFile(file) -> bytearray:
    b = bytearray(file.read())
    return b


def stitchFragments(b: List[bytearray],
                    block_length: int,
                    distributed_parity: bool = False) -> bytearray:
    """
       b: ordered list of fragments (bytearrays) to stitch together
       block_length: length of one block
    """

    stitched_bytearray = bytearray()
    total_length = 0
    num_fragments = len(b)

    for fragment in b:
        del fragment[0:HEADER_LENGTH]
        total_length += len(fragment)

    # print("\nFRAGMENTS in stitch fragments")
    # for fragment in b:
    #     print(fragment)

    if distributed_parity:
        pass
    else:

        # TODO, explore list(zip(*b))
        # as a possible method of stitching together the arrays
        i = 0
        parity_counter = 0
        #frag_position = 0
        frag_byte_counter = 0
        frag_array_position = 0
        #parity = bytearray(num_fragments)
        parity_byte_position = num_fragments - 1

        while i < total_length:
            # remove parity bit
            if parity_counter == parity_byte_position:
                parity_counter = 0
                i += 1
                frag_array_position += 1
                if frag_array_position >= num_fragments:
                    frag_array_position = 0
                    frag_byte_counter += 1

            if frag_byte_counter < len(b[frag_array_position]):
                stitched_bytearray.append(
                    b[frag_array_position][frag_byte_counter])
                parity_counter += 1
            frag_array_position += 1

            if frag_array_position >= num_fragments:
                frag_array_position = 0
                frag_byte_counter += 1

            i += 1

    # print('STITCHED FRAGMENTS')
    # print(stitched_bytearray)
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
    # TODO only delete the files with the correct name
    if os.path.isdir(frag_path):
        for f in os.listdir(frag_path):
            os.remove(os.path.join(frag_path, f))


# Sorts the fragments based on their position stored in their header
def orderFragmentsByHeader(fragments: List[bytearray]) -> List[bytearray]:
    fragmentsOrdered = [None] * len(fragments)
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

def bitwise_xor(b1: bytearray, b2: bytearray) -> bytearray:
    result = bytearray()
    for b1, b2 in zip(b1, b2):
        result.append(b1 ^ b2)
    return result

def bitwise_xor_array(ba: List[bytearray], 
                      indices: List[int],
                      start: int,
                      end: int) -> bytearray:
    """Bitwise XOR across multiple bytearrays in a list

    Args:
        ba (List[bytearray]): List of bytearrays to XOR
        indices (List[int]): List of indices in ba to XOR
        start (int): Start index of XOR operation in each bytearray
        end (int): End index of XOR operation in each bytearray
    
    Returns:
        bytearray: Description
    """
    result = bytearray()
    for b1, b2 in zip(b1, b2):
        result.append(b1 ^ b2)
    return result

def splitIntoFragments(b: bytearray, 
                       block_length: int, 
                       num_fragments: int,
                       distributed_parity: bool = False) -> List[bytearray]:
    """[summary]

    [description]

    Arguments:
      b {bytearray} -- [description]
      num_fragments {int} -- [description]

    Keyword Arguments:
      create_parity {bool} -- [description] (default: {True})
    """

    total_file_length_bytes = len(b)

    print("length of b:", total_file_length_bytes)
    print(f'block length: {block_length}')
    print("number of fragments:", num_fragments)
    print("len(b) mod num_fragments:", (total_file_length_bytes % num_fragments))

    outputFragments = []
    parity = bytearray()

    for i in range(num_fragments):
        outputFragments.append(bytearray())

    

    if distributed_parity:
        addHeadersToFragments(outputFragments,
                          num_fragments,
                          total_file_length_bytes,
                          True)

    else:
        addHeadersToFragments(outputFragments,
                          num_fragments,
                          total_file_length_bytes,
                          False)
        i = 0
        parity_counter = 0
        frag_position = 0
        #parity = bytearray(num_fragments)
        parity_bit_position = num_fragments - 1

        # for each byte in file
        while i < total_file_length_bytes:

            # insert parity bit
            if parity_counter == parity_bit_position:
                parity = 0
                for byte in b[i - (num_fragments - 1):i]:
                    parity = parity ^ byte
                # print(f'parity as position {frag_position}')
                outputFragments[frag_position].append(parity)
                parity_counter = 0
                frag_position += 1
                if frag_position >= num_fragments:
                    frag_position = 0

            outputFragments[frag_position].extend(b[i:i+block_length])
            frag_position += 1
            parity_counter += 1

            if frag_position >= num_fragments:
                frag_position = 0

            i += block_length

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
    """Summary
    
    Args:
        config_file (str): Description
    
    Returns:
        List[cloud_storage.CloudStorage]: Description
    """

    config = readConfig(config_file)

    clouds = []

    for cloud in config['clouds']:
        clouds.append(list(cloud.values()))

    cloud_storage_providers = []

    for cloud in clouds:
        if cloud[0].lower() in providers.DRIVERS:
            print("Creating cloud storage provider for", cloud[0])
            # unpacks the could config into a list of args
            # needed becasue some cloud providers require different args than others
            c = cloud_storage.CloudStorage(cloud)
            try:
                c.driver.list_containers()
            except:
                print("ERROR: Failed to connect to cloud:", cloud[0])
                continue
            cloud_storage_providers.append(c)
        else:
            print("ERROR: cloud provider", cloud[0].lower(), "not found")

    return cloud_storage_providers


def saveFragmentsToDisk(fragments: List[bytearray], file_name, file_path='') -> List[str]:
    # returns a list of filenames for the fragments saved to disk
    fragNameList = []
    for frag in fragments:
        frag_name = name = os.path.basename(file_name) + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        frag_path = file_path + frag_name
        fragNameList.append(frag_name)
        with open(frag_path, 'wb') as f:
            f.write(frag)
    return fragNameList


def pushFragmentsToCloudFromFiles(fragNameList: List[str], clouds: List[cloud_storage.CloudStorage], file_name: str, frag_path=''):
    for cloud in clouds:
        cloud.establishContainer()

    cloud_num = 0
    for frag_name in fragNameList:
        clouds[cloud_num].setMetaData(file_name=os.path.basename(file_name))
        file_path = frag_path + frag_name
        clouds[cloud_num].uploadObjectFromFile(file_path, frag_name)
        print("File: " + frag_name + " uploaded to " + clouds[cloud_num].cloud)

        cloud_num += 1
        if cloud_num >= len(clouds):
            cloud_num = 0


def pushFragmentsToCloudFromFilesNew(fragNameList: List[str], clouds: List[cloud_storage.CloudStorage], file_name: str, frag_path=''):
    for cloud in clouds:
        cloud.establishContainer()

    upload_pool = mp.Pool(mp.cpu_count())

    cloud_num = 0
    for frag_name in fragNameList:
        clouds[cloud_num].setMetaData(file_name=os.path.basename(file_name))
        file_path = frag_path + frag_name

        upload_pool.apply_async(clouds[cloud_num].threadUploadObjectFromFile, args=(file_path, frag_name))

        print("File: " + frag_name + " uploading to " + clouds[cloud_num].cloud)

        cloud_num += 1
        if cloud_num >= len(clouds):
            cloud_num = 0

    upload_pool.close()
    upload_pool.join()


# does not currently work for azure because libcloud is stupid
def pushFragmentsToCloud(fragments: List[bytearray], clouds: List[cloud_storage.CloudStorage], file_name: str):
    # name fragments
    cloud_num = 0
    print("Uploading files to cloud...")
    print(file_name)
    for frag in fragments:
        frag_name = name = file_name + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        print("File: " + frag_name + " uplaoded to " + clouds[cloud_num].cloud)
        clouds[cloud_num].setMetaData(file_name=file_name)
        clouds[cloud_num].uploadObject(frag, frag_name)

        cloud_num += 1
        if cloud_num >= len(clouds):
            cloud_num = 0


def getFragmentsFromCloud(file_name: str, clouds: List[cloud_storage.CloudStorage]):
    # multhi-threaded version of getFragmentsFromCloudOld
    pool = mp.Pool(mp.cpu_count())
    result_opjects = []
    fragments = []

    for cloud in clouds:
        objectsToDownload = cloud.listObjectsWithPrefix(os.path.basename(file_name))

        for obj in objectsToDownload:
            result_opjects.append(pool.apply_async(cloud.threadDownload, (obj,)))

    fragments = [p.get() for p in result_opjects]

    pool.close()

    return fragments


def getFragmentsFromCloudOld(file_name: str, clouds: List[cloud_storage.CloudStorage]):
    fragments = []

    for cloud in clouds:
        fragments.extend(cloud.getFilesWithPrefix(os.path.basename(file_name)))

    return fragments


def cleanupClouds(clouds: List[cloud_storage.CloudStorage], removeExistingContainers: bool):
    for cloud in clouds:
        cloud.cleanUp(removeExistingContainers)


def main():
    DEBUG = True

    if DEBUG:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            SMCS()

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        # stats.print_stats()
        stats.dump_stats(filename='profilingStats.prof')
    else:
        SMCS()


if __name__ == "__main__":
    main()
