#!C:/Python35/python.exe

# -*- coding: UTF-8 -*-
#
# belmih 2016
#

from multiprocessing import Pool
import time
import xml.etree.cElementTree as ET
import os
import shutil
import zipfile
import uuid
import string
import random
import argparse

# set working directory
abspath = os.path.abspath(__file__)
workdir = os.path.dirname(abspath)
os.chdir(workdir)


# settings
COUNTXMLFILES = 100
LENGTHRANDOMSTRING = 32
COUNTZIP = 50
DELETEXML = True
ZIPFOLDER = './zip'
XMLFOLDER = './xml'


# creates a folder for xml files with unique name
def make_xml_folder():
    foldername = str(uuid.uuid1())
    xmlfolder = os.path.join(XMLFOLDER, foldername)
    if not os.path.exists(xmlfolder):
        os.makedirs(xmlfolder)
    return foldername


# The generator of random strings
def generate_random_string(length):
    random.seed()
    randomstring = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])
    return randomstring


def make_count_xml(xmlfolder, countxmlfiles):
    for i in range(countxmlfiles):
        generate_xml(xmlfolder)


# put the files out folder in a zip archive
def zip_dir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)


# create xml of a given structure
def generate_xml(xmlfolder):
    random.seed()

    xmlfile = os.path.join(XMLFOLDER, xmlfolder, str(uuid.uuid1()) + ".xml")

    id = str(uuid.uuid1())
    level = str(random.randint(1, 101))
    objectscount = random.randint(1, 11)

    root = ET.Element("root")

    var = ET.SubElement(root, "var")
    var.set("name", "id")
    var.set("value", id)

    var = ET.SubElement(root, "var")
    var.set("name", "level")
    var.set("value", level)

    objects = ET.SubElement(root, "objects")
    for o in range(objectscount):
        randomstring = generate_random_string(LENGTHRANDOMSTRING)
        obj = ET.SubElement(objects, "object")
        obj.set("name", randomstring)

    tree = ET.ElementTree(root)
    tree.write(xmlfile)


# process worker
def make_zip(i):
    pass
    foldername = make_xml_folder()
    make_count_xml(foldername, COUNTXMLFILES)

    if not os.path.exists(ZIPFOLDER):
        os.makedirs(ZIPFOLDER)

    zipfilename = os.path.normpath(os.path.join(ZIPFOLDER, foldername + ".zip"))
    print(zipfilename)

    zipf = zipfile.ZipFile(zipfilename, 'w')
    try:
        zip_dir(os.path.join(XMLFOLDER, foldername), zipf)
    except:
        raise
    else:
        zipf.close()


def main():
    parser = argparse.ArgumentParser(description='Do 50 *.zip files.')
    parser.add_argument('-p', type=int, help='count processes', default=2)
    args = parser.parse_args()

    countprocesses = args.p
    start = time.perf_counter()
    print(os.getcwd())

    if DELETEXML and os.path.exists(ZIPFOLDER):
        shutil.rmtree(ZIPFOLDER)

    pool = Pool(processes=countprocesses)
    pool.map(make_zip, range(COUNTZIP))
    pool.close()
    pool.join()

    if DELETEXML:
        shutil.rmtree(XMLFOLDER)

    print('time:', time.perf_counter() - start)


if __name__ == '__main__':
    main()
