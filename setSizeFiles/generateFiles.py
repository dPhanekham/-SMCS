def generate_big_random_bin_file(filename,size):
    """
    generate big binary file with the specified size in bytes
    :param filename: the filename
    :param size: the size in bytes
    :return:void
    """
    import os 
    with open('%s'%filename, 'wb') as fout:
        fout.write(os.urandom(size))
    print ('big random binary file with size %f generated ok'%size)

def main():
    generate_big_random_bin_file('1MB.bin', 1024 * 1024 * 1)
    generate_big_random_bin_file('2MB.bin', 1024 * 1024 * 2)
    generate_big_random_bin_file('4MB.bin', 1024 * 1024 * 4)
    generate_big_random_bin_file('8MB.bin', 1024 * 1024 * 8)
    generate_big_random_bin_file('16MB.bin', 1024 * 1024 * 16)
    generate_big_random_bin_file('32MB.bin', 1024 * 1024 * 32)
    generate_big_random_bin_file('64MB.bin', 1024 * 1024 * 64)
    generate_big_random_bin_file('128MB.bin', 1024 * 1024 * 128)
    generate_big_random_bin_file('256MB.bin', 1024 * 1024 * 256)
    generate_big_random_bin_file('512MB.bin', 1024 * 1024 * 512)
    generate_big_random_bin_file('1024MB.bin', 1024 * 1024 * 1024)

if __name__ == '__main__':
    main()