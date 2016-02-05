#!/usr/bin/python

import socket
import asyncore
import smtpd
import threading
import time
from datetime import datetime
import sys, os
import csv
import re


class CustomSMTPServer(smtpd.SMTPServer):

    class CSVfile:
        def __init__(self,filename):
            self.filename = filename
            self.fieldnames = [ 'IP', 'DATE', 'FROM', 'TO', 'SUBJECT', 'BODY']
            with open(filename, 'w') as csvfile:
               writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
               writer.writeheader()

        # write csv file
        def write_row(self, row):
            with open(self.filename, 'a') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';')
                spamwriter.writerow(row)

    emails = []
    csvfile = CSVfile('test.csv')
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        ip_addr = peer[0]
        date = datetime.now()

        from_addr = ""
        m = re.search('^from:\s(.+)$', data, re.I|re.M)
        if m:
            from_addr = m.group(1)
        else:
            from_addr = mailfrom

        to_addr = ""
        m = re.search('^to:\s(.+)$', data, re.I|re.M)
        if m:
            to_addr = m.group(1)
        else:
            to_addr = rcpttos

        subject = "" 
        m = re.search('^subject:\s(.+)$', data, re.I|re.M)
        if m:
            subject = m.group(1)

        body = ""
        m = re.search('\n\n(.+)$', data, re.I|re.S)
        if m:
            body = m.group(1)

        self.csvfile.write_row([ip_addr, date, from_addr, to_addr, subject, body])
        self.emails.append(1)
        return
        

class MyReceiver(object):
    
    def __init__(self):
        self.run = False
    
    def start(self):
        """Start the listening service"""
        # here I create an instance of the SMTP server, derived from  asyncore.dispatcher
        self.smtp = CustomSMTPServer(('0.0.0.0', 1025), None)
        # and here I also start the asyncore loop, listening for SMTP connection, within a thread
        # timeout parameter is important, otherwise code will block 30 seconds after the smtp channel has been closed
        self.thread =  threading.Thread(target=asyncore.loop,kwargs = {'timeout':1} )
        # self.thread.daemon = True
        self.thread.start() 
        self.run = True

        
    def stop(self):
        if self.run:
            """Stop listening now to port 25"""
            # close the SMTPserver to ensure no channels connect to asyncore
            self.smtp.close()
            # now it is save to wait for the thread to finish, i.e. for asyncore.loop() to exit
            self.thread.join()
            self.run = False
    

    def get_statistic(self):
        pass
        
            
    # now it finally it is possible to use an instance of this class to check for emails or whatever in a non-blocking way
    def count(self):
        """Return the number of emails received"""
        return len(self.smtp.emails)  
     
    def get(self):
        """Return all emails received so far"""
        return self.smtp.emails    


        
if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    workdir = os.path.dirname(abspath)
    os.chdir(workdir)

    mr = MyReceiver()
    mr.start()
    try:
        while True:
            command = str(raw_input('smtp server:'))
            if 'start' == command:
                mr.start()
            elif 'stop' == command:
                mr.stop()
            elif 'restart' == command:
                mr.stop()
                mr.start()
            elif 'statistic' == command:
                mr.get_statistic()
            elif 'exit' == command:
                mr.stop()
                sys.exit(0)
            else:
                print "Unknown command"
            time.sleep(.2)
    except KeyboardInterrupt:
        mr.stop()
        print "bye"
        sys.exit(2)

