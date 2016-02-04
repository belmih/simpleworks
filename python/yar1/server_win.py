#!C:/python27/python.exe

import socket
import logging
import asyncore
import smtpd
import threading
import time
import sys, os
import csv


class CustomSMTPServer(smtpd.SMTPServer,None,file):

    emails = []
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        print 'Receiving message from:', peer
        print 'Message addressed from:', mailfrom
        print 'Message addressed to  :', rcpttos
        print 'Message length        :', len(data)
        print 'Data:', str(data)
        self.emails.append(1)
        
        return
    

        

class MyReceiver:
    
    def __init__(self):
        self.run = False
        self.csvfile = CSVfile('test.csv')
    
    def start(self):
        """Start the listening service"""
        # here I create an instance of the SMTP server, derived from  asyncore.dispatcher
        self.smtp = CustomSMTPServer(('0.0.0.0', 1025), None,self.csvfile)
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

            
    # now it finally it is possible to use an instance of this class to check for emails or whatever in a non-blocking way
    def count(self):
        """Return the number of emails received"""
        return len(self.smtp.emails)  
      
      
    def get(self):
        """Return all emails received so far"""
        return self.smtp.emails    

class CSVfile:
    def __init__(self,filename):
        fieldnames = [ 'IP', 'DATE', 'FROM', 'TO', 'SUBJECT', 'BODY']
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # write csv file
    def write_csv(filename, fieldnames, data):
        with open('eggs.csv', 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
            
        # with open(filename, 'a') as csvfile:
            # writer = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldnames)
            # writer.writerow(data)
            # with open('eggs.csv', 'wb') as csvfile:
        # spamwriter = csv.writer(csvfile, delimiter=' ',
                                # quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
        # spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
        
if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    workdir = os.path.dirname(abspath)
    os.chdir(workdir)
    
    mr = MyReceiver()
    try:
        while True:
            command = str(raw_input('Input:'))
            if 'start' == command:
                mr.start()
            elif 'stop' == command:
                mr.stop()
            elif 'restart' == command:
                mr.stop()
                mr.start()
            elif 'status' == command:
                mr.status()
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
