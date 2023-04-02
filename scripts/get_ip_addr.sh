#!/bin/bash

ip=$(ip -f inet addr show dev eth0 | sed -n 's/^ *inet* *\([.0-9]*\).*/\1/p')

echo $ip
