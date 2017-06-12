#!/bin/sh

# Paths
IPTABLES='/sbin/iptables'
SCRIPT_DIR='/etc/iptables/ipv4'

# Networks
TRUSTED='10.0.100.0/255.255.255.0'

# This machine's outside IP
OUTSIDE_IP='192.168.254.15'

# Smurf networks
SMURF_NW1='212.1.130.0/24'
SMURF_NW2='204.158.83.0/24'
SMURF_NW3='209.241.162.0/24'
SMURF_NW4='159.14.24.0/24'  
SMURF_NW5='192.220.134.0/24'
SMURF_NW6='204.193.121.0/24'
SMURF_NW7='198.253.187.0/24'
SMURF_NW8='164.106.163.0/24'
SMURF_NW9='12.17.161.0/24'  
SMURF_NW10='199.98.24.0/24'  

# Disable forwarding temporarily
echo '0' > /proc/sys/net/ipv4/conf/all/forwarding

# Clear out everything, reset counters
$IPTABLES -t nat -F
$IPTABLES -t nat -X
$IPTABLES -t nat -Z
$IPTABLES -t mangle -F
$IPTABLES -t mangle -X
$IPTABLES -t mangle -Z
$IPTABLES -t filter -F
$IPTABLES -t filter -X
$IPTABLES -t filter -Z

. $SCRIPT_DIR/filter.sh
#. $SCRIPT_DIR/filter_test.sh
. $SCRIPT_DIR/mangle.sh
. $SCRIPT_DIR/nat.sh

# Re-enable forwarding
echo '1' > /proc/sys/net/ipv4/conf/all/forwarding
