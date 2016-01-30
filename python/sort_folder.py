#!C:/Python34/python.exe
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import argparse
from datetime import date


def parse_arguments():
    parser = argparse.ArgumentParser(description='Sort files')
    parser.add_argument('-s', '--source', required=True, help='Source folder')
    parser.add_argument('-d', '--destination', required=True, help='Destination folder')
    parser.add_argument('-t', '--type', required=True, choices=['ext', 'year', 'month', 'day'],
                        help='Sort type')
    args = parser.parse_args()

    return args.source, args.destination, args.type


def get_dest_folder(sourceFolder, file, destFolder, sortType):
    if sortType == "ext":
        (filename, ext) = os.path.splitext(file)
        destFolder = os.path.join(destFolder, ext)
    else:
        sourceFile = os.path.join(sourceFolder, file)
        fileModifDate = date.fromtimestamp(os.path.getmtime(sourceFile))
        fmYear = fileModifDate.strftime("%Y")
        fmMonth = fileModifDate.strftime("%m")
        fmDay = fileModifDate.strftime("%d")
        if sortType == "year":
            destFolder = os.path.join(destFolder, fmYear)
        elif sortType == "month":
            destFolder = os.path.join(destFolder, fmYear + '-' + fmMonth)
        elif sortType == "day":
            destFolder = os.path.join(destFolder, fmYear + '-' + fmMonth + '-' + fmDay)

    return destFolder


def get_dest_file(file, destFolder):
    (filename, ext) = os.path.splitext(file)
    destFile = os.path.join(destFolder, file)
    numFile = 0
    while os.path.exists(destFile):
        numFile += 1
        newfile = "{0}_{1}{2}".format(filename, numFile, ext)
        destFile = os.path.join(destFolder, newfile)
    return destFile


def main():
    (sourceFolder, destinationFolder, sortType) = parse_arguments()
    if not os.path.exists(sourceFolder):
        sys.exit('Missing folder: %s', sourceFolder)
    for root, dirs, files in os.walk(sourceFolder):
        for file in files:
            sourceFile = os.path.join(root, file)
            destFolder = get_dest_folder(root, file, destinationFolder, sortType)
            if not os.path.exists(destFolder):
                os.makedirs(destFolder)
            destFile = get_dest_file(file, destFolder)
            print("{0} -> {1}".format(sourceFile, destFile))
            shutil.move(sourceFile, destFile)


if __name__ == '__main__':
    main()
