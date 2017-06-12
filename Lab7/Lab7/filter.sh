#!/bin/sh

IPTABLES='/sbin/iptables -t filter'


$IPTABLES -P INPUT DROP
# Change the FOWARD chain's default policy to DROP
$IPTABLES -P FORWARD DROP
$IPTABLES -P OUTPUT ACCEPT

# Convenient logging chain
$IPTABLES -N logdrop
$IPTABLES -A logdrop -j LOG
$IPTABLES -A logdrop -j DROP

# Various custom forward chains
$IPTABLES -N trusted-outside
$IPTABLES -A trusted-outside -j ACCEPT

$IPTABLES -N outside-trusted
# Stronger ICMP rules to block the icmp echo-reply packets from smurf networks
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW1 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW2 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW3 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW4 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW5 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW6 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW7 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW8 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW9 -j DROP 
$IPTABLES -A outside-trusted -p icmp --icmp-type 0/0 -s $SMURF_NW10 -j DROP 
# Allow all other ICMP traffic
$IPTABLES -A outside-trusted -p icmp -j ACCEPT
# Allow TCP packets with the SYN flag set that are headed to destination ports: 21, 22, 23, 25, 80, 135, 137, 138, 139, 443, 445, and 3389
$IPTABLES -A outside-trusted -p tcp -m multiport --destination-port 21,22,23,25,80,135,137,138,139,443,445,3389 --tcp-flags SYN,FIN,ACK SYN -j ACCEPT
# Allow all packets which are members of ESTABLISHED connections 
$IPTABLES -A outside-trusted -m state --state ESTABLISHED -j ACCEPT 
# Send all other traffic to the logdrop chain
$IPTABLES -A outside-trusted -j logdrop 

# Traffic directed at this machine
$IPTABLES -A INPUT -i lo -j ACCEPT
$IPTABLES -A INPUT -j ACCEPT

# Add a rule to the end of the FORWARD chain which sends all traffic to the logdrop chain
$IPTABLES -A FORWARD -j logdrop
# Add a rule at the top of the FORWARD chain.
# This rule should send all packets coming from the TRUSTED network to the trusted-outside
#      chain for further evaluation.
$IPTABLES -I FORWARD 1 -i $TRUSTED_IF -s $TRUSTED -j trusted-outside
# ADD a rule as the second item in the FORWARD chain.
# This rule should send all packets coming from the Internet to the TRUSTED network
#      to the outside-trusted chain for further evaluation.
$IPTABLES -I FORWARD 2 -i $OUTSIDE_IF -d $TRUSTED -j outside-trusted
# $IPTABLES -I FORWARD 2 -i $OUTSIDE_IF -d $TRUSTED -s !$TRUSTED -j outside-trusted


# Generated from this machine to other networks
$IPTABLES -A OUTPUT -o lo -j ACCEPT
