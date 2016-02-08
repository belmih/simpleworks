#!/usr/bin/python

import argparse
import smtplib
import email.utils
from email.mime.text import MIMEText
import random, string
import time, sys, os
import threading
import logging

IP_ADDRESS = "127.0.0.1"
SMTP_PORT = 25
COUNT_THREADS = 8

abspath = os.path.abspath(__file__)
workdir = os.path.dirname(abspath)
os.chdir(workdir)

class EmailSender:
    
    def __init__(self,from_domain,to_domain):
        self.email_count = 0
        self.run = False
        self.threads = []
        self.lock = threading.Lock()

        self.from_domain = from_domain
        self.to_domain = to_domain

    class Email:
        def __init__(self,from_d,to_d):
            self.__from_addr = self.get_random_addr(from_d)
            self.__to_addr   = self.get_random_addr(to_d)
          
        def get_random_string(self, minlen=6, maxlen=12):
            random.seed()
            len = random.randint(minlen,maxlen)
            s1 = random.choice(string.ascii_letters)
            randomstring = s1 + ''.join([random.choice(string.ascii_letters + string.digits) for n in range(len-1)])
            return randomstring
            
        def get_random_addr(self, domain):
            tmpstr = self.get_random_string()
            randomaddr = tmpstr + '@' + domain
            return randomaddr.lower()
           
        def get_data(self):
            msg = MIMEText(self.get_random_string(6, 128))
            msg['To'] = email.utils.formataddr(('Recipient', self.__to_addr))
            msg['From'] = email.utils.formataddr(('Author', self.__from_addr))
            msg['Subject'] = self.get_random_string()
            return (self.__from_addr, self.__to_addr, msg.as_string())
    
    
    def start_thread(self):
        for i in range(COUNT_THREADS):
            t = threading.Thread(target=self.send_email)
            t.daemon = True
            t.start()
            self.threads.append(t)
    
    
    def send_email(self):
        logging.debug("in thread")
        while self.run:
            time.sleep(.1)
            try:
                logging.debug("send mail")
                server = smtplib.SMTP(IP_ADDRESS, SMTP_PORT)
                email = self.Email(self.from_domain,self.to_domain)
                from_addr, to_addr, msg = email.get_data()
                server.sendmail(from_addr, to_addr, msg)
                self.lock.acquire()
                self.email_count += 1
                self.lock.release()
                server.quit()
            except: 
                e = sys.exc_info()[0]
                logging.error("Error %s" % e)
                print "Error %s" % e
           

    def start(self):
        if self.run:
            print "client is already running"
        else:
            self.start_thread()
            self.run = True
            print "\nclient is running"
        
        
    def stop(self):
        self.run = False
        for t in self.threads:
            t.join()
        print "\nclient stopped"

            
    def get_statistic(self):
        print "\nemails sent: %s" % self.email_count


def configure_logging():
    logging.basicConfig(level = logging.DEBUG,
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        filename='smtpclient.log',
                        filemode='a')
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(levelname)s: %(message)s')
    # console.setFormatter(formatter)
    # logging.getLogger('').addHandler(console)

def get_args():
    parser = argparse.ArgumentParser(description='email sender')
    parser.add_argument('-f','--from-domain', help='from domain', required=True)
    parser.add_argument('-t','--to-domain', help='to domain', required=True)
    args = parser.parse_args()
    return (args.from_domain, args.to_domain)

def main():
    from_domain, to_domain = get_args()
    print "Hello! Use: start|stop|restart|statistic|exit"
    sender = EmailSender(from_domain, to_domain)
    sender.start()
    try:
        while True:
            command = str(raw_input('smtp client:'))
            if 'start' == command:
                sender.start()
            elif 'stop' == command:
                sender.stop()
                sender.get_statistic()
            elif 'restart' == command:
                sender.stop()
                time.sleep(.5)
                sender.start()
            elif 'statistic' == command:
                sender.get_statistic()
            elif 'exit' == command:
                sender.stop()
                sys.exit(0)
            else:
                print "Unknown command"
            time.sleep(.2)
    except KeyboardInterrupt:
        logging.error("Keyboard Interrupt")
        sender.stop()
        print "Bye!"
        sys.exit(1)


if __name__ == '__main__':
    configure_logging()
    main()
