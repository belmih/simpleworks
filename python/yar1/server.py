#!C:/python27/python.exe

import asyncore
from smtpd import SMTPServer
import threading
import time
from datetime import datetime
import sys, os
import csv
import re
import logging

IP_ADDRESS = "127.0.0.1"
SMTP_PORT = 25
CSV_FILE = "test.csv"
    
abspath = os.path.abspath(__file__)
workdir = os.path.dirname(abspath)
os.chdir(workdir)
    
class CustomSMTPServer(SMTPServer):
    
    class CSV_file:
        def __init__(self, filename):
            self.filename = filename
            with open(self.filename, 'w') as csvfile:
                fieldnames = ['IP', 'DATE', 'FROM', 'TO', 'SUBJECT', 'BODY']
                writer = csv.DictWriter(csvfile, dialect='excel', lineterminator='\n', delimiter=';', fieldnames=fieldnames)
                writer.writeheader()

        def write_row(self, row):
            with open(self.filename, 'a') as csvfile:
                spamwriter = csv.writer(csvfile, dialect='excel', lineterminator='\n', delimiter=';')
                spamwriter.writerow(row)
    
    
    csv_file = CSV_file(CSV_FILE)    
    email_count = 0
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        """ generates the data for the file """
        ip_addr = peer[0]
        date = datetime.now()

        from_addr = ""
        m = re.search('^from:\s(.+)$', data, re.I | re.M)
        if m:
            from_addr = m.group(1)
        else:
            from_addr = mailfrom

        to_addr = ""
        m = re.search('^to:\s(.+)$', data, re.I | re.M)
        if m:
            to_addr = m.group(1)
        else:
            to_addr = rcpttos

        subject = ""
        m = re.search('^subject:\s(.+)$', data, re.I | re.M)
        if m:
            subject = m.group(1)

        body = ""
        m = re.search('\n\n(.+)$', data, re.I | re.S)
        if m:
            body = m.group(1)

        self.csv_file.write_row([ip_addr, date, from_addr, to_addr, subject, body])
        self.email_count += 1
        return


class MyReceiver(object):

    def __init__(self):
        self.run = False
        
    def start(self):
        """ Start the listening service """
        if self.run:
            print "The server is already running"
            return
        #create an instance of the SMTP server, derived from  asyncore.dispatcher
        self.smtp = CustomSMTPServer((IP_ADDRESS, SMTP_PORT), None)
        # and also start the asyncore loop, listening for SMTP connection, within a thread
        self.thread = threading.Thread(target=asyncore.loop, kwargs={'timeout': 1})
        self.thread.daemon = True
        self.thread.start()
        self.run = True

    def stop(self):
        """ Stop listening now to port """
        if self.run:
            # close the SMTPserver to ensure no channels connect to asyncore
            self.smtp.close()
            # now it is save to wait for the thread to finish, i.e. for asyncore.loop() to exit
            self.thread.join()
            self.run = False
            self.smtp = None

    def get_statistic(self):
        """ displays the number of received emails """
        print "receive e-mails: %s" % self.smtp.email_count
        

def configure_logging():
    logging.basicConfig(level = logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        filename='smtpserver.log',
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
def main():
    print "Hello! Use: start|stop|restart|statistic|exit"
    reciver = MyReceiver()
    reciver.start()
    try:
        while True:
            command = str(raw_input('smtp server:'))
            if 'start' == command:
                reciver.start()
            elif 'stop' == command:
                reciver.stop()
                reciver.get_statistic()
            elif 'restart' == command:
                reciver.stop()
                time.sleep(.5)
                reciver.start()
            elif 'statistic' == command:
                reciver.get_statistic()
            elif 'exit' == command:
                reciver.stop()
                sys.exit(0)
            else:
                print "Unknown command"
            time.sleep(.2)
    except KeyboardInterrupt:
        reciver.stop()
        sys.exit(1)

if __name__ == "__main__":
    configure_logging()
    main()
   
