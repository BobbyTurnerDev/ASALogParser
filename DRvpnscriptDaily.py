import os.path
import os
from datetime import date, datetime, timedelta
import shutil
import time
import csv
import smtplib
from email.message import EmailMessage


#copy the last 60 days of files over from MCDPLOG2
sourcepath = os.path.expanduser("\\\\MCDPLOG2\\fwlogs")
processpath = "D:/Projects/LogFiles/"
fwlogs = os.listdir(sourcepath)
for log in fwlogs:
    if os.path.isfile(os.path.join(sourcepath, log)):
        lastmodified = datetime.fromtimestamp(os.path.getmtime(sourcepath+'\\'+log))
        cutoffdate = datetime.now() - timedelta(days=60)
        if lastmodified > cutoffdate:
            shutil.copy2(sourcepath+'\\'+log,processpath+'\\'+log)

#vpn login string
pattern = "ASA-4-722051"
pattern2 = "ASA-7-746013"

newpath = os.path.expanduser("D:/Projects/DRVPNLogs")
timestr = time.strftime("%m-%d-%Y")
file_name = ('DRVPNLog-'+timestr+'Daily.csv')
header = ['Username', 'Date', 'Time', 'Login/Logoff']
csvfile = open(os.path.join(newpath, file_name), 'w', newline='')
csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(header)

#open up the local log path, grab all of the files (we'll filter them in the loop)
path = os.path.expanduser("D:/Projects/LogFiles/")
files = os.listdir(path)
for f in files:
    lastmodified = datetime.fromtimestamp(os.path.getmtime(path+'\\'+f))
    cutoffdate = datetime.now() - timedelta(days=1)
    if lastmodified > cutoffdate:
        openfile = open(os.path.join(path, f), 'r')
        data=openfile.readlines()
        for line in data:
            if pattern in line:
                line = line.split()
                user = str(line[8]) 
                user = user.strip('<')
                user = user.strip('>')
                user = user.lower()
                date = str(line[0])
                time = str(line[1])
                print(user,date,time)
                csvwriter.writerow([user,date,time,'Login'])
            elif pattern2 in line:
                line = line.split()
                user = str(line[11]) 
                user = user.strip('LOCAL\\')
                user = user.lower()
                date = str(line[0])
                time = str(line[1])
                print(user,date,time)
                csvwriter.writerow([user, date, time, 'Logoff'])
        openfile.close()

csvfile.close()

msg = EmailMessage()
msg['Subject'] = ('1-Day DR VPN Report for '+timestr)
msg['From'] = 'noreply@mcohio.org'
msg['To'] = 'shockleye@mcohio.org'
attach_path = os.path.join(newpath+'\\'+file_name)
with open(attach_path, 'rb') as attach_file:
    file_data = attach_file.read()
msg.add_attachment(file_data, maintype='application', subtype='csv', filename=file_name)
with smtplib.SMTP('mcdpsmtp.mcohio.org:25') as mail:
    mail.send_message(msg)
