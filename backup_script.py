#!/usr/bin/python

import gzip
import subprocess
import os
import datetime

# Directories to Backup
dir_to_backup = '/var/www/'

# DBs to backup
db_to_backup = ['Mondial','Mondial1']

# DB storage server
db_host = 'a.b.c.d' # IP
db_user = 'backup' # Username
db_dir = '/root/backup/db/' # Directory for backup

#  Files storage server
file_host = 'a.b.c.d' # IP
file_user = 'backup' # Username
file_dir = '/root/backup/files/' # Directory for backup

# MySQL Credentials
mysql_user = 'root'
mysql_pass = 'root'
mysql_hostname  = 'localhost'
mysql_port      = 3306

# Log and alert variables
email_alert = 'john@doe.com'
log_path = "/home/script/backup.log";
file_path = "/home/script/temp"

#Date use for timestamp the DBs and files backups
date_string = datetime.datetime.now().strftime("%Y-%m-%d")

# Files to upload
db_to_up = []
files_to_up = []



def db_backup(db_name, mysql_user, mysql_pass, mysql_hostname, date_string, file_path):
    """Create a backup (gz) file of the database in parameter"""
    
    #Write in log file
    log.write("Create backup files for db: %s\n" % (db_name))
    
    #Use of mysqldump function to back up the database
    cmd = "mysqldump -u %s -p%s -h %s -e --single-transaction -c %s" % (mysql_user, mysql_pass, mysql_hostname, db_name)

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    error = process.stderr.read()
    dump_process = process.communicate()[0]
    
    #Filename: [db_name]_Y-m-d.sql.gz
    file_name = "%s_%s.sql.gz" % (db_name, date_string) # Create Filename

    if error != "":
        log.write("Error: %s\n" % error)
    else:
        log.write("File %s successfully created\n" % file_name)
    
    #Create the .gz file with the .SQL extracted    
    gzip_file = gzip.open(file_path + "/" + file_name, "wb")
    gzip_file.write(dump_process)
    gzip_file.close()

    return file_name
    

def files_backup(dir_backup, date_string, file_path):
    """Create backup of Files describe in parameter"""
    
    #Write in Log
    log.write("Create backup files for directory: %s\n" % (dir_backup))
    
    #Create the file tar.gz
    file_name = "files_%s.tar.gz" % date_string
    os.chdir(dir_backup)
    cmd = "tar -czpPf %s/%s ." % (file_path, file_name)
    os.system(cmd)
    log.write("File files_%s.tar.gz successfully created\n" % date_string)
    
    return file_name
    
def file_upload(file_name, user, host, directory, file_path):
    """Upload File to the server by SCP"""
    
    #Write in Log
    log.write("Uploading %s\n" % file_name)
    
    #Move to the files directory
    os.chdir(file_path)
    
    #Call SCP command / Could be improved by using pure python method/Lib paramiko
    cmd = "scp -Bq %s %s@%s:%s/%s" % (file_name, user, host, directory, file_name) #Use of RSA authentification necessary
    os.system(cmd)
    
    log.write("File %s successfully uploaded\n" % file_name)


# Script Start
#Create Log File

log = open(log_path,'a')
log.write(
"Starting script at %s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)

# Loop db_to_backup to create backups of DBs
for index, item in enumerate(db_to_backup):
    db_to_up.append(db_backup(item, mysql_user, mysql_pass, mysql_hostname, date_string, file_path))

# Create backup of files
files_to_up.append(files_backup(dir_to_backup, date_string, file_path))

print

# Upload the backups to the servers
#DBs first
for index, item in enumerate(db_to_up):
    file_upload(item, db_user, db_host, db_dir, file_path)

#Files
for index, item in enumerate(files_to_up):
    file_upload(item, file_user, file_host, file_dir, file_path)

#Close Logs
log.write("Ending script at %s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
log.close()

