#!C:/Python32/python.exe

import os
import sys
import datetime
import string
import logging
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Deletes files older than N days')
    parser.add_argument('rootdir', metavar='DirRoot', help='Folder with files')
    parser.add_argument('daysold', metavar='N', type=int, help='Number of days')
    parser.add_argument('-l', '--logfile', metavar='LogFile', default = sys.argv[0]+'.log',
        help='Log file')
    parser.add_argument('-c', '--column', metavar='C', type=int, default=60,
        help='Column Width')
    args = parser.parse_args()
     
    return args.rootdir, args.daysold, args.logfile, args.column 
    

def configure_logging(logfile):
    logging.basicConfig(level = logging.DEBUG,
        format = '%(asctime)s {%(filename)s} %(levelname)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        filename = logfile,
        filemode='a')

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s {%(filename)s} %(levelname)s:%(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    #logging.info('')
    return logging.getLogger('myapp')


def delete_old_files(rootdir, daysold, columnw, logger):
    if not os.path.exists(rootdir) :
        sys.exit('Missing folder: %s', rootdir)
   
    fileList = []
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            fileList.append(os.path.join(root, file))

    dnow = datetime.datetime.now()

    for file in fileList:
        try:
            dmodify = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            days_diff = (dnow-dmodify).days
            if days_diff > daysold :
                os.remove(file)
                logger.info('%s %s %s deleted', file.ljust(columnw), 
                    dmodify.strftime('%Y-%m-%d %H:%M:%S'), days_diff)
            else :
                logger.info('%s %s %s', file.ljust(columnw), 
                    dmodify.strftime('%Y-%m-%d %H:%M:%S'), days_diff)
        except OSError as e:
            logger.error('OSError: {}. File: {}'.format(e.strerror, e.filename))

def main():
    (rootdir, daysold, logfile, columnw) = parse_arguments()
    logger = configure_logging(logfile)
    delete_old_files(rootdir, daysold, columnw, logger)

if __name__ == '__main__':
    main()
