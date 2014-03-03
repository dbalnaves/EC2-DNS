#!/bin/bash

MAC=$(ip l l eth0 | grep ether | awk '{ print $2 }')
VPC=$(curl -s http://169.254.169.254/latest/meta-data/network/interfaces/macs/$MAC/vpc-id)

sed -e 's/options {/options {\n        empty-zones-enable yes;/' -i /etc/named.conf
echo 'include "/etc/named/ec2-dns/named.ddns.conf";' >> /etc/named.conf

mkdir /etc/named/ec2-dns
wget -P /etc/named/ec2-dns https://github.com/dbalnaves/EC2-DNS/raw/master/named.ddns.conf
wget -P /usr/local/bin https://github.com/dbalnaves/EC2-DNS/raw/master/parse_instance.py
chmod 755 /usr/local/bin/parse_instance.py

cp /var/named/named.empty /var/named/named.ec2-dns
chown root:named /var/named/named.ec2-dns.jnl /var/named/named.ec2-dns
chmod 664 /var/named/named.ec2-dns.jnl /var/named/named.ec2-dns
chmod 775 /var/named

echo "AWS_DEFAULT_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone|sed -e s/.$//)" > /etc/cron.d/ec2-dns
echo "*/2 * * * * root (/usr/local/bin/parse_instance.py $VPC $1 | nsupdate" >> /etc/cron.d/ec2-dns)

/etc/init.d/named start
