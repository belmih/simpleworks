#!C:/Python35/python.exe

# -*- coding: UTF-8 -*-
#
# belmih 2016
#

from multiprocessing import Process, Queue, Lock
import os
import xml.etree.cElementTree as ET
import shutil
import zipfile
import time
import csv
import argparse


abspath = os.path.abspath(__file__)
workdir = os.path.dirname(abspath)
os.chdir(workdir)

CSV_ID_LEVEL = "id_level.csv"
CSV_ID_OBJECT = "id_object_name.csv"
UNZIPFOLDER = './unzip'
DELETEXML = True


# create new csv file
def create_new_file(filename, fieldnames):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        
def print_lock(s,lock):
    lock.acquire()
    try:
        print(s)
    finally:
        lock.release()
        
        
# write csv file
def write_csv(filename, fieldnames, data, lock):
    lock.acquire()
    try:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
            writer.writerow(data)
    finally:        
        lock.release()
        

def unzip_archive(item):
    tmpfoldername = os.path.basename(item).split('.')[0]
    tmpfolderpath = os.path.join('unzip', tmpfoldername)
    zfile = zipfile.ZipFile(item)
    for name in zfile.namelist():
        (dirname, filename) = os.path.split(name)
        dirnamepath = os.path.join(tmpfolderpath, dirname)
        if not os.path.exists(dirnamepath):
            os.makedirs(dirnamepath)
        zfile.extract(name, dirnamepath)
    return tmpfolderpath


# xml parser and writer csv
def parse_xml(xmlfile, lock):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    id = root.findall("./var[@name='id']")[0].get('value')
    level = root.findall("./var[@name='level']")[0].get('value')

    write_csv(CSV_ID_LEVEL, ['id', 'level'], {'id': id, 'level': level}, lock)
    
    for obj in root.findall('./objects/object'):
        for key, value in obj.items():
            write_csv(CSV_ID_OBJECT, ['id', 'object_name'], {'id': id, 'object_name': value}, lock)
    os.remove(xmlfile)

            
def remove_unzip_folder():
    if DELETEXML and os.path.exists(UNZIPFOLDER):
        shutil.rmtree(UNZIPFOLDER)

        
# process worker
def worker(quezip, lock):
    while True:
        item = quezip.get()
        if (item == 'STOP'):
            break
        print_lock(item,lock)    
        tmpfolderpath = unzip_archive(item)  
        # find all xml
        for root, dirs, files in os.walk(tmpfolderpath):
            for file in files:
                if file.endswith(".xml"):
                    f = os.path.join(root, file)
                    parse_xml(f, lock)

                    
def main():
    parser = argparse.ArgumentParser(description='Do *.csv files.')
    parser.add_argument('-p', type=int, help='count processes', default=2)
    args = parser.parse_args()

    countprocesses = args.p

    start = time.perf_counter()

    print(os.getcwd())

    create_new_file(CSV_ID_LEVEL, ['id', 'level'])
    create_new_file(CSV_ID_OBJECT, ['id', 'object'])

    remove_unzip_folder()
    
    lock = Lock()
    quezip = Queue()
    
    # Submit tasks
    for root, dirs, files in os.walk("zip"):
        for file in files:
            zf = os.path.normpath(os.path.join(root, file))
            quezip.put(zf)

    processes = []
    for i in range(countprocesses):
        p = Process(target=worker, args=(quezip, lock))
        p.start()
        processes.append(p)

    # Tell child processes to stop
    for i in range(countprocesses):
        quezip.put('STOP')
    
    for p in processes:
        p.join()
    
    remove_unzip_folder()
    print('time:', time.perf_counter() - start)

    
if __name__ == '__main__':
    main()
