#!/usr/bin/env python3

from st7735s import ST7735S
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
import signal

def handler(signum, fram):
    exit(0)

def main():
    print("ST7735")
    signal.signal(signal.SIGINT, handler)
    disp = ST7735S(port = "/dev/spidev5.0", dc = 127, blk = 123, res = 82)
    
    WIDTH = 64
    HEIGHT = 32

    disp.fill([255, 255, 255])

    del disp

if __name__ == "__main__":
    main()