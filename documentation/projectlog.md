# Log 13-12-22

## One Sentence summary of the day
Testing the deployment.  

## Challenges
To test if I can connect to the webserver and managment server. I was able to connect with RDP to the managment server, but I couldn't SSH into the webserver. 

## Solutions
I checked the NACL and Security groups and found out that I used the wrong IP address, to allow SSH into the webserver. I had to use my public IP address. (because only SSH from admins home is allowed.)  

# Log 14-12-22

## One Sentence summary of the day
Creating the webserver with the userdata stored in a S3 bucket.
## Challenges
After coding the creation of a bucket and the code to upload files in the bucket. A userdata file is added to the code of installing the instance. The instance has permision to read from S3. The code deployed without error, but the webserver was not working.
## Solutions  
The webserver was not working because the userdata was not executed. The userdata was added after the instance creation. So to solve this I had to write the code for the userdata above the code of instance creation.

# Log 15-12-22

## One Sentence summary of the day
Creating backup for the webserver.
## Challenges
Making a backup vault to store and organize the backups. Than making the backupplan to store in the backup vault. The webserver is selected for the backupplan and a rule is added to the backupplan to make daily backups and deleted after 7 days.
## Solutions
The code is easy to find in the official aws cdk documentation.

____

# Log [date-yesterday]

## One Sentence summary of the day

## Challenges

## Solutions