#!/bin/bash
# Permanent block of SSH brute-force bots (2026-09-08)
sudo cscli decisions add --ip 64.110.90.250 --duration 8760h --reason "KR Seoul / Oracle Cloud / SSH brute-force"
sudo cscli decisions add --ip 223.123.65.54 --duration 8760h --reason "PK Islamabad / CMPak / SSH brute-force (12 events)"
sudo cscli decisions add --ip 151.158.2.135 --duration 8760h --reason "IN Hyderabad / Arcr Tech / SSH brute-force (55 events)"
sudo cscli decisions add --ip 165.101.40.180 --duration 8760h --reason "VN Hanoi / Thanh Huyen / SSH brute-force"
echo "Blocked 4 IPs permanently. Verify with: sudo cscli decisions list"
