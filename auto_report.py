#coding:utf-8
#!/usr/bin/env python

import records
# import codecs
import sys
import time
import ConfigParser
import os
import smtplib
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import email

stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr
reload(sys)  
sys.setdefaultencoding('utf-8')
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde

def query_data(file_name, db_url):
    print( '==' *30)
    db = records.Database(db_url)
    rows = db.query_file(os.path.dirname(os.path.realpath(__file__)) + '/sql/query.sql')
    with open(file_name, 'wb',) as f:
        f.write(rows.export('xls'))
    # print(rows.dataset)
    print("query data success!") 
    db.close()

'''
    check dir
'''
def check_dir(dst_path):
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

def send_mail(email_config, attachment_path):
    # print email_config.get('smtp')
    # print email_config.get('email_address')
    #print email_config.get('password')
    print("Init SMTP server successfully. server=%s, email_address=%d."%(email_config.get('smtp'), email_config.get('email_address')))

    msg = MIMEMultipart()  
    msg["Subject"] = email_config.get('title')
    msg["From"]    = email_config.get('email_address') 
    msg["To"]      = email_config.get('to')

    cc_addrs = []
    if email_config.has_key('cc'):
        msg["Cc"] = email_config.get('cc')
        cc_addrs = email_config.get('cc').split(',')
    to_addrs = email_config.get('to').split(',')
    
    to_addrs.extend(cc_addrs)

    to = email_config.get('to')

    # 邮件文本内容
    content=MIMEText(email_config.get('content'),'html')
    msg.attach(content)

    #xlsx类型附件  
    attach_part = MIMEApplication(open(attachment_path,'rb').read())

    attach_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path) )  
    msg.attach(attach_part) 

    sent = smtplib.SMTP(email_config.get('smtp'),timeout=30)
    sent.login(email_config.get('email_address'),email_config.get('password'))
    sent.sendmail(email_config.get('email_address'), to_addrs, msg.as_string())
    sent.quit()
    print('send finish at %s' %(time.strftime("%Y%m%d %H:%M:%S", time.localtime())))


def main():
    dest_path = os.getcwd()+"/report"
    check_dir(dest_path)
    file_name = ''.join((dest_path, '/',time.strftime("%Y%m%d%H%M%S", time.localtime()),'.xls'))
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.dirname(os.path.realpath(__file__)) + "/config/config.conf", "rb"))
    db_url = config.get('db','url')
    query_data(file_name, db_url)
    send_mail(dict(config.items('email')), file_name)
    # 

if __name__=='__main__':
    main()