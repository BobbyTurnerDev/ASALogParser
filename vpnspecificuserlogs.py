import os


# Username of the person we want to track
pattern = "heckmh".lower()

# Set the environment variables
path = os.path.expanduser("C:\Projects\LogFiles")
newpath = os.path.expanduser("C:\Projects\Output")
filename = 'matchesuserheckma.csv'
newf = open(os.path.join(newpath, filename), "w+")
files = os.listdir(path)

# Parse through the VPN logs for any login attempts, write them to the csv
for f in files:
    openfile = open(os.path.join(path, f), 'r')
    data=openfile.readlines()
    for line in data:
        if pattern in line.lower():
            newf.write(line)
    openfile.close()
newf.close()