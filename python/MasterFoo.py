# !/usr/bin/python
# -*- coding: utf-8 -*-


# import cProfile
import argparse
import hmac
import itertools
import logging
import os
import string
import sys
import time
from hashlib import sha1
from multiprocessing import Process, Pipe

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

abspath = os.path.abspath(__file__)
workdir = os.path.dirname(abspath)
os.chdir(workdir)


class MasterFoo:
    def __init__(self, filein, fileout):
        self.filein = filein
        self.fileout = fileout

    def worker(self, filein, fileout, conn):
        logging.debug("call MasterFoo.worker()")
        lines = self.read_my_file(filein)
        if not lines:
            logging.error("Empty file")
            return

        num_lines = len(lines)

        hash_part = 100000 / num_lines
        k = hash_part * num_lines

        try:
            f = open(fileout, 'w')

            line_index = 0
            count_hash_part = 0
            count_all_hashes = 0

            while True:
                hash = conn.recv()
                if hash is None:
                    break

                if count_hash_part == hash_part and count_all_hashes < k:
                    count_hash_part = 0
                    line_index += 1
                    f.flush()

                foo_string = "{0}::{1}\n".format(lines[line_index], hash)
                f.write(foo_string)

                count_hash_part += 1
                count_all_hashes += 1

            f.close()
        except IOError as e:
            logging.error(e)
            sys.exit(1)

    def read_my_file(self, filename):
        """ read input file """
        logging.debug("call MasterFoo.read_my_file()")
        try:
            with open(filename, 'r') as my_file:
                lines = list(s for s in map(string.strip, my_file))
        except IOError as e:
            logging.error(e)
            sys.exit(1)
        return lines

    def get_hashes(self, conn):
        """ get 100k salt """
        logging.debug("call MasterFoo.get_salt()")
        a = map(str, xrange(10))
        salts = itertools.imap(''.join, itertools.product(a, repeat=5))

        for salt in salts:
            conn.send(self.foo(salt))
        conn.send(None)

    def foo(self, salt,
            key='\xe1\xc8\x2d\xAF\xFC\xE6\x65\x62\xDC\x51\xDB\x60\x24\x9B\xA2\x45\xA2\xA1\xEB\x8F\xCE\x44\xAF\x42'):
        """ magic foo """
        # logging.debug("call MasterFoo.foo()")
        v = hmac.new(key, salt, sha1).digest()
        return ''.join('{0:02x}'.format(s) for s in map(ord, v))

    def make_foo_file(self):
        """read input file, foo() and write output file """
        logging.debug("call MasterFoo.make_foo_file()")

        conn_r, conn_s = Pipe()

        p1 = Process(target=self.worker, args=(self.filein, self.fileout, conn_r))
        p1.daemon = True
        p1.start()

        hashes = self.get_hashes(conn_s)

        p1.join()


def arg_parse():
    parser = argparse.ArgumentParser(description='masterfoo')
    parser.add_argument('file', help='path to file')
    args = parser.parse_args()
    return args.file


def make_input_file(filename, num_lines):
    """ make input file (for debug) """
    logging.debug("call make_input_file()")
    f = open(filename, "w")
    f.writelines("line_{}\n".format(num) for num in xrange(num_lines))
    f.close()


def main():
    logging.debug("call main()")
    input_file = arg_parse()
    my_master = MasterFoo(input_file, 'foo_file.txt')
    my_master.make_foo_file()


if __name__ == '__main__':
    start_time = time.time()
    try:
        # make_input_file("lines.txt", 7)
        # cProfile.run('main()')
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    logging.info("--- %s seconds ---" % (time.time() - start_time))
    sys.exit(0)
