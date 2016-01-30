#!C:/Python35/python.exe

# -*- coding: UTF-8 -*-
#
# belmih 2016
#

import threading
import queue
import argparse
import os
import time
import zipfile
import shutil
import xml.etree.cElementTree as ET
import csv

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
        
        
# write csv file
def write_csv(filename, fieldnames, data):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
        writer.writerow(data)
        
        
# xml parser and writer csv
def parse_xml(xmlfile):
    # with lock:
        # print(xmlfile)
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    id = root.findall("./var[@name='id']")[0].get('value')
    level = root.findall("./var[@name='level']")[0].get('value')
    quecsvidlevel.put({'id': id, 'level': level})
    for obj in root.findall('./objects/object'):
        for key, value in obj.items():
            quecsvidobject.put({'id': id, 'object_name': value})
            
            
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
    
    
def worker1():
    while True:
        item = quecsvidlevel.get()
        if item is None:
            with lock:
                print(CSV_ID_LEVEL + ' done.') 
            break
        write_csv(CSV_ID_LEVEL, ['id', 'level'], item)
        quecsvidlevel.task_done()
        
        
def worker2():
    while True:
        item = quecsvidobject.get()
        if item is None:
            with lock:
                print(CSV_ID_OBJECT + ' done.')
            break
        write_csv(CSV_ID_OBJECT, ['id', 'object_name'], item)
        quecsvidobject.task_done()        
        
        
def worker():
    while True:
        item = quezip.get()
        if item is None:
            break
        with lock:
            print(item)
        tmpfolderpath = unzip_archive(item) 
        # find all xml
        for root, dirs, files in os.walk(tmpfolderpath):
            for file in files:
                if file.endswith(".xml"):
                    f = os.path.join(root, file)
                    parse_xml(f)
        quezip.task_done()

        
def remove_unzip_folder():
    if DELETEXML and os.path.exists(UNZIPFOLDER):
        print ("remove {} ...".format(UNZIPFOLDER))
        shutil.rmtree(UNZIPFOLDER) 
                    
                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Do *.csv files.')
    parser.add_argument('-p', type=int, help='count processes', default=2)
    args = parser.parse_args()

    numworkerthreads = args.p

    start = time.perf_counter()

    print(os.getcwd())

    create_new_file(CSV_ID_LEVEL, ['id', 'level'])
    create_new_file(CSV_ID_OBJECT, ['id', 'object'])

    remove_unzip_folder()

    lock = threading.Lock()    
    
    quezip = queue.Queue()
    quecsvidlevel = queue.Queue()
    quecsvidobject = queue.Queue()
    
    threads = []
    for i in range(numworkerthreads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for root, dirs, files in os.walk("zip"):
        for file in files:
            zf = os.path.normpath(os.path.join(root, file))
            quezip.put(zf)

    quezip.join()
        
    for i in range(numworkerthreads):
        quezip.put(None)
        
    for t in threads:
        t.join()
        

        
    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)
    
    t1.start()
    t2.start()
    
    quecsvidlevel.join()
    quecsvidobject.join()   
    
    quecsvidlevel.put(None)
    quecsvidobject.put(None)
 
    t1.join
    t2.join

    time.sleep(.1)

    remove_unzip_folder()
    
    print('time:', time.perf_counter() - start)
