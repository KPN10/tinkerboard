"""
sudo pip3 install python-periphery
"""

#!/usr/bin/env python3

from periphery import GPIO
import time

pin_cpu = 127
pin = GPIO(pin_cpu, "out")

def main():
    while True:
        try:
            pin.write(True)
            print("led on")
            time.sleep(0.5)
            pin.write(False)
            print("led off")
            time.sleep(0.5)

        except KeyboardInterrupt:
            pin.write(False)
            pin.close()
            break

        except IOError:
            print("Error")
    
if __name__ == "__main__":
    main()
