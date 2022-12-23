#!/bin/bash

sudo yum update -y
sudo yum install -y httpd 
sudo systemctl start httpd
sudo systemctl enable httpd

sudo touch /var/www/html/index.html
sudo chmod 755 -R /var/html/index.html
echo "<h1> Hello world, this is the website to test if it's working</h1>" | sudo tee index.html