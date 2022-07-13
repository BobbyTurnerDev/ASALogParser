import os.path
import os
import psycopg2
from datetime import date, datetime, timedelta
import shutil
import keyring

# Use Keyring to get the password for the DB (https://pypi.org/project/keyring/)
dbpw = keyring.get_password("vpnreport","postgres")

# start the connection to postgreSQL
con = psycopg2.connect(
    host="localhost", database="vpnusers", user="postgres", password=dbpw
)

# create the cursor
cur = con.cursor()

# Executing an MYSQL function using the execute() method
cur.execute("select version()")

# Fetch a single row using fetchone() method. Print to the console so we know we got connected.
data = cur.fetchone()
print("Connection established to: ", data)

# Let's get the latest version of the VPN Master List so we know when the user last placed a service request for access
cur.execute(
    """CREATE TEMP TABLE tmp_x (REQNUMBER int, REQDATE date, STATUS text, CONTACTS text, LOGGED text, ATTACHMENTS text, DEPARTMENT text, FULLNAME text, LAST text, TOTAL int, USERNAME text, primary key(REQNUMBER, USERNAME));

COPY tmp_x FROM 'C:/Temp/VPNMasterList.csv' WITH (FORMAT CSV, HEADER, NULL '');

insert into vpnforms (REQNUMBER, REQDATE, USERNAME) select REQNUMBER, REQDATE, USERNAME from tmp_x
	ON CONFLICT (USERNAME,REQNUMBER) DO UPDATE SET
		REQNUMBER = (EXCLUDED.REQNUMBER),
		REQDATE = (EXCLUDED.REQDATE);

drop table tmp_x; """
)

# Copy the last 60 days of files over from the server containing the logs
source_path = os.path.expanduser("\\\\MCDPLOG2\\fwlogs")
process_path = "C:/Projects/LogFiles/"
fw_logs = os.listdir(source_path)
for log in fw_logs:
    if os.path.isfile(os.path.join(source_path, log)):
        last_modified = datetime.fromtimestamp(os.path.getmtime(source_path + "\\" + log))
        cutoff_date = datetime.now() - timedelta(days=60)
        if last_modified > cutoff_date:
            shutil.copy2(source_path + "\\" + log, process_path + "\\" + log)

# vpn login string
pattern = "ASA-6-722051"

# Open up the local log path, grab all of the files (we'll filter them in the loop)
path = os.path.expanduser("C:/Projects/LogFiles/")
files = os.listdir(path)
for f in files:
    last_modified = datetime.fromtimestamp(os.path.getmtime(path + "\\" + f))
    cutoff_date = datetime.now() - timedelta(days=30)
    if last_modified > cutoff_date:
        open_file = open(os.path.join(path, f), "r")
        data = open_file.readlines()
        for line in data:
            if pattern in line:
                line = line.split()
                user = str(line[8])
                user = user.strip("<")
                user = user.strip(">")
                user = user.lower()
                date = str(line[0])
                print(user)
                sqlinsert = """ INSERT INTO vpnlogins (username, lastvpnlogin) 
                    VALUES (%s, %s) 
                    ON CONFLICT (username) DO UPDATE SET
                        lastvpnlogin = (EXCLUDED.lastvpnlogin);"""
                cur.execute(sqlinsert, (user, date))
        open_file.close()

# commit the changes
con.commit()

sql = """COPY (with latestdate as (
SELECT 
    f.username,
    (SELECT Max(v)
     FROM (VALUES (f.reqdate), (l.lastvpnlogin)) AS value(v)) as lastactivitydate
FROM vpnlogins l
RIGHT JOIN vpnforms f ON LOWER(l.username) = LOWER(f.username)
)

select LOWER(username),lastactivitydate
from latestdate
where lastactivitydate <= current_date - interval '30 days') TO STDOUT WITH CSV DELIMITER ',' """

with open("C:/Temp/vpnremovals.csv", "a") as file:
    cur.copy_expert(sql, file)

cur.close()
# close the cursor and connection
con.close()
