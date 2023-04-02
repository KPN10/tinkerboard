"""
sudo pip3 install python-periphery
"""

#!/usr/bin/env python3

from periphery import SPI

def main():
    spi = SPI("/dev/spidev5.0", 0, 1000000)
    data_out = [0xaa, 0xbb, 0xcc, 0xdd]
    data_in = spi.transfer(data_out)

    print("shifted out [0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}]".format(*data_out))
    print("shifted in  [0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}]". format(*data_in))

    spi.close()

if __name__ == "__main__":
    main()