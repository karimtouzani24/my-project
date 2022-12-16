## Project: 1.0

### Demands
- 2 VPCs in region Frankfurt 
    - VPC1: 10.10.10.0/24
        - 2 public subnets: mask /25
            - 1 subnet with the web server and the other subnet is extra.
    - VPC2: 10.20.20.0/24
        - 2 public subnets: mask /25
            - 1 subnet with the managment server and the other subnet is extra.
- VPCs are connected with a VPC peering connection.  
- The subnets are protected:
    - NACL  
- The instances are protected:  
    - Security Groups  
- Only the managment server can SSH into the webserver.  
- Only the admin (ip from home or office) can SSH/RDP into the managment server.  
- Everyone can acces the webserver with HTTP/HTTPS.  
- OS of the instances:  
    - web server: Linux.  
    - managment server: Windows.  
- There is userdata to instal the webserver.  
    - This userdata should be stored in a S3 bucket with no public acces.  
- The instances and s3 buckets are encrypted.  
- Daily backups of the webserver and stored for 7 days.
