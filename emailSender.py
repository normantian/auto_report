#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
''''' 
Copyright (C)  2015 By Thomas Hu.  All rights reserved. 
@author : Thomas Hu 
@version: 1.0 
@created: 2015-05-17 
'''  
import sys
import records
import base64  
import httplib  
import re  
import os  
import smtplib
import time
import ConfigParser 
from xml.etree import ElementTree  
from email.utils import formatdate  
from email.MIMEText import MIMEText  
from email.MIMEBase import MIMEBase  
from email.MIMEMultipart import MIMEMultipart  
from email import Encoders  


stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr
reload(sys)  
sys.setdefaultencoding('utf-8')
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde

  
class EmailSender(object):  
    def __init__(self, smtp_server, smtp_port=25, verbose=False, debug_level=1, encoding="utf-8"):  
        ''''' Initiate the EmailSender. 
        @param smtp_server: the Email SMTP server. 
        @param smtp_port:   the Email SMTP server port, if use the default port(25), you can set it to 0 or 25. 
        @param verbose:     show the processing information if set to 'True', default is 'False'. 
        @param debug_level: set the smtplib debug level, if it's '0', will enable debug information. 
        @param encoding:    the encoding or charset for email body text or attachment file name, default is "utf-8". 
        '''  
        self.server = smtp_server  
        self.port = int(smtp_port)  
        self.verbose = verbose  
        self.debug_level = int(debug_level)  
        self.encoding = encoding  
        self.attachments = []  
  
        #Create smtp instance  
        self.smtp = smtplib.SMTP(self.server, self.port)  
        self.smtp.set_debuglevel(self.debug_level)  
        self.print_verbose("Init SMTP server successfully. server=%s, port=%d."%(self.server, self.port))  
  
    def print_verbose(self, message):  
        '''''Print the verbose information. 
        @param message: the message to be print if the verbose is "True". 
        '''  
        if self.verbose:  
            print(message)  
              
    def login(self, user, password):  
        '''''Login to SMTP server. 
        @param user:     the user name of the email sender. 
        @param password: the passord of the user for login to SMTP server. 
        '''  
        self.from_addr = user #user + "@" + ".".join(self.server.split(".")[1:])  
        try:  
            self.print_verbose("Start to login into SMTP server.server=%s, port=%d."%(self.server, self.port))  
            self.smtp.login(user, password)  
            self.print_verbose("Login into SMTP server successfully.")  
        except Exception as ex:  
            print("Login into SMTP server failed! Error info: %s"%(str(ex)))  
  
    def __add_attachment_file(self, filename, encoding, Filter):  
        '''''Add attachment file to the attachment list. 
        @param filename:  the file name of attachment, should not be a path. 
        @param encoding:  the encode of the attachment file name. 
        @param Filter:    the file filter object, must implement 'accept(filename)' interface, and return True or False. 
        '''  
        # Check if the file is acceptable by the Filter  
        if Filter is not None:  
            try:  
                accept = Filter.accept(filename)  
            except:  
                accept = False  
            if accept == False:  
                return  
        # Add the attachment to the attachment list  
        try:  
            basename = os.path.basename(filename)  
            attach = MIMEBase("application", "octet-stream")  
            attach.set_payload(open(filename, "rb").read())  
            #attach.add_header("Content-Disposition", "attachment;filename=%s"%(basename))  
            #attach.add_header("Content-Disposition", "attachment", filename=(encoding, "", basename))
            attach.add_header("Content-Disposition", "attachment", filename=basename)  
            Encoders.encode_base64(attach)  
            self.attachments.append(attach)  
            self.print_verbose("Add attachment \"%s\" successfully."%(filename))  
        except Exception as ex:  
            print("Add attachment file \"%s\" failed. Error info: %s."%(filename, str(ex)))  
                  
    def add_attachment(self, path, encoding=None, Filter=None):  
        '''''Add attachment file to the attachment list. 
        @param path:      the path of files to be added as attachment files. If is a directory, all of the files in it will be added. 
        @param encoding:  the encode of the attachment file name. 
        @param Filter:    the file filter object, must implement 'accept(filename)' interface, and return True or False. 
        '''  
        if not os.path.exists(path):  
            self.print_verbose("Warning: attachment path \"%s\" is not exists."%(path))  
            return  
        charset = encoding if (encoding is not None) else self.encoding  
        if os.path.isfile(path):  
            return self.__add_attachment_file(path, charset, Filter)  
        for root, dirs, files in os.walk(path):  
            for f in files:  
                fname = os.path.join(root, f)  
                self.__add_attachment_file(fname, charset, Filter)  
                  
    def send_email(self, subject, to_addrs, cc_addrs, content, subtype="plain", charset=None):  
        '''''Send the email to the receivers. 
        @param subject:    the email's subject(title). 
        @param to_addrs:   the receivers' addresses, it's a list looks like ["user1@some_server.com", "user2@another_server.com"]. 
        @param cc_addrs:   the copy to receivers' addresses, has the same format as to_addrs. 
        @param content:    the email message body, it can be plain text or HTML text, which depends on the parameter 'content_type'. 
        @param subtype:    the content type, it can be "html" or "plain", default is "plain". 
        @param charset:    the charset of message content, default is "None", use the same encoding as the initial function, which default is "utf-8". 
        @return: if send successfully, return 'True', otherwise, return 'False'. 
        '''  
        charset = charset if charset is not None else self.encoding  
          
        #Set the root information  
        msg_root = MIMEMultipart("related")  
        msg_root["Subject"] = subject  
        msg_root["From"] = self.from_addr  # You can change it to any string  
        msg_root["To"] = ",".join(to_addrs)  
        msg_root["CC"] = ",".join(cc_addrs)  
        msg_root["Date"] = formatdate(localtime=True)  
        msg_root.preamble = "This is a multi-part message in MIME format."  
  
        #Encapsulate the plain and HTML of the message body into an 'alternative' part,  
        #so message agents can decide which they want to display.  
        msg_alt = MIMEMultipart("alternative")  
  
        #Set the message content  
        msg_txt = MIMEText(content, subtype.lower(), charset)  
        msg_alt.attach(msg_txt)  
  
        #Add the alternative part to root part.  
        msg_root.attach(msg_alt)  
  
        #Add the attachment files  
        for attach in self.attachments:  
            msg_root.attach(attach)  
  
        #Extend the copy to addresses to to_addrs  
        to_addrs.extend(cc_addrs)  
  
        #Send the email  
        try:  
            self.smtp.sendmail(self.from_addr, to_addrs, msg_root.as_string())  
            self.print_verbose("Send email successfully.")  
        except Exception as ex:  
            print("Send email failed. Error info:%s"%(str(ex)))  
            return False  
        return True  
  
    def close(self):  
        '''''Quit from the SMTP. 
        '''  
        self.smtp.quit()  
        self.print_verbose("Logout SMTP server successfully.")  

'''
    check dir
'''
def check_dir(dst_path):
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

def query_data(file_name, db_url):
    print( '==' *30)
    db = records.Database(db_url)
    rows = db.query_file(os.path.dirname(os.path.realpath(__file__)) + '/sql/query.sql')
    with open(file_name, 'wb',) as f:
        f.write(rows.export('xls'))
    print(rows.dataset)
    db.close()

def create_excel(file_name, db_url):
    dest_path = os.getcwd()+"/report"
    check_dir(dest_path)
    query_data(file_name, db_url)

def test():
    
    file_name = ''.join(('./report/',time.strftime("%Y%m%d%H%M%S", time.localtime()),'.xls'))
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.dirname(os.path.realpath(__file__)) + "/config/config.conf", "rb"))
    db_url = config.get('db','url')
    create_excel(file_name, db_url)

    smtp_server = config.get('email','smtp')  
    user = config.get('email','email_address')
    password = config.get('email','password')  
    from_addr = config.get('email','email_address') 
    to_addrs = config.get('email','to').split(',') #["tianfei@wusongtech.com"]  
    cc_addrs = config.get('email','cc').split(',') 

    subject = config.get('email','title')  
    content = config.get('email','content') 
    #'Dear Friends,<p/><a href="http://blog.csdn.net/thomashtq"> Welcome to my CSDN blog!</a> <p/>Thanks a lot!'  
    #attach_files=[r"D:\temp\sendemail\attach"]  
    attach_files= [file_name]  
  
    emailsender = EmailSender(smtp_server, verbose=True)  
    emailsender.login(user, password)  
    for attach in attach_files:  
        emailsender.add_attachment(attach, "utf-8")  
    emailsender.send_email(subject, to_addrs, cc_addrs, content, subtype="html", charset="utf-8")  
    emailsender.close() 

if __name__ == '__main__':  
    test() 