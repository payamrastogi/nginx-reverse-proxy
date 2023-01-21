#!/bin/bash
yum update -y
sudo su

amazon-linux-extras install -y nginx1
systemctl start nginx
systemctl enable nginx