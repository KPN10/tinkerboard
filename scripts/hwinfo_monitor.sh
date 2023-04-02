#!/bin/bash

# watch -t -p -n 1 ./hwinfo_monitor.sh

soc_temp=$(sudo cat /sys/class/thermal/thermal_zone0/temp | awk '{printf "%.2f", $0 / 1000}')
cpu_freq=$(sudo cat /sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq | awk '{printf "%.2f", $0 / 1000}')

echo "SoC Temp=> $soc_temp degree C"
echo "CPU Freq=> $cpu_freq MHz"
