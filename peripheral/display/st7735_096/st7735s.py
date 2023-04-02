from periphery import GPIO
from periphery import SPI
import numbers
import time
import numpy as np

class Instructions:
    NOP = 0x00
    COLS = 132
    ROWS = 162
    NOP = 0x00
    SWRESET = 0x01
    RDDID = 0x04
    RDDST = 0x09
    SLPIN = 0x10
    SLPOUT = 0x11
    PTLON = 0x12
    NORON = 0x13
    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E
    PTLAR = 0x30
    MADCTL = 0x36
    COLMOD = 0x3A
    FRMCTR1 = 0xB1
    FRMCTR2 = 0xB2
    FRMCTR3 = 0xB3
    INVCTR = 0xB4
    DISSET5 = 0xB6
    PWCTR1 = 0xC0
    PWCTR2 = 0xC1
    PWCTR3 = 0xC2
    PWCTR4 = 0xC3
    PWCTR5 = 0xC4
    VMCTR1 = 0xC5
    RDID1 = 0xDA
    RDID2 = 0xDB
    RDID3 = 0xDC
    RDID4 = 0xDD
    GMCTRP1 = 0xE0
    GMCTRN1 = 0xE1
    PWCTR6 = 0xFC


# Constants for interacting with display registers.
TFTWIDTH = 64
TFTHEIGHT = 32


# Colours for convenience
BLACK = 0x0000  # 0b 00000 000000 00000
BLUE = 0x001F  # 0b 00000 000000 11111
GREEN = 0x07E0  # 0b 00000 111111 00000
RED = 0xF800  # 0b 11111 000000 00000
CYAN = 0x07FF  # 0b 00000 111111 11111
MAGENTA = 0xF81F  # 0b 11111 000000 11111
YELLOW = 0xFFE0  # 0b 11111 111111 00000
WHITE = 0xFFFF  # 0b 11111 111111 11111

def color565(r, g, b):
    """Convert red, green, blue components to a 16-bit 565 RGB value. Components
    should be values 0 to 255.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def image_to_data(image, rotation=0):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    # NumPy is much faster at doing this. NumPy code provided by:
    # Keith (https://www.blogger.com/profile/02555547344016007163)
    pb = np.rot90(np.array(image.convert('RGB')), rotation // 90).astype('uint16')
    color = ((pb[:, :, 0] & 0xF8) << 8) | ((pb[:, :, 1] & 0xFC) << 3) | (pb[:, :, 2] >> 3)
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class ST7735S(object):
    def __init__(self, port, dc, blk, res, width=TFTWIDTH,
                 height=TFTHEIGHT):
        print("ST7735S created.")

        self.spi = SPI(port, 0, 1000000)
        self.dc = GPIO(dc, "out")
        self.blk = GPIO(blk, "out")
        self.blk.write(True)
        self.res = GPIO(res, "out")

        # Default left offset to center display
        rotation = 90
        # width = ST7735_TFTWIDTH
        # height = ST7735_TFTHEIGHT
        self._width = width
        self._height = height
        self._rotation = rotation

        offset_left = None
        offset_top = None

        if offset_left is None:
            offset_left = (Instructions.COLS - width) // 2

        self._offset_left = offset_left

        # Default top offset to center display
        if offset_top is None:
            offset_top = (Instructions.ROWS - height) // 2

        self._offset_top = offset_top

        self.hard_reset()
        self.init()

    def __del__(self):
        print("Destructor called, ST7735S deleted.")
        self.spi.close()

    def send(self, data, is_data=True):
        if is_data:
            # print("DC low")
            self.dc.write(False)
        else:
            # print("DC high")
            self.dc.write(True)

        if isinstance(data, numbers.Number):
            data = [data & 0xff]
        self.spi.transfer(data)

    def send_command(self, data):
        self.send(data, False)

    def send_data(self, data):
        self.send(data, True)

    def hard_reset(self):
        print("hard_reset")
        self.res.write(True)
        time.sleep(0.5)
        self.res.write(False)
        time.sleep(0.5)
        self.res.write(True)

    def soft_reset(self):
        self.send_command(Instructions.SWRESET)
        time.sleep(0.3)
        self.send_command(Instructions.DISPOFF)
        time.sleep(0.3)
        self.send_command(Instructions.DISPON)

    def init(self):
        print("Init display")

        self.send_command(Instructions.SWRESET)    # Software reset
        time.sleep(0.150)               # delay 150 ms

        self.send_command(Instructions.SLPOUT)     # Out of sleep mode
        time.sleep(0.500)               # delay 500 ms

        self.send_command(Instructions.FRMCTR1)    # Frame rate ctrl - normal mode
        self.send_data(0x01)                 # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.send_data(0x2C)
        self.send_data(0x2D)

        self.send_command(Instructions.FRMCTR2)    # Frame rate ctrl - idle mode
        self.send_data(0x01)                 # Rate = fosc/(1x2+40) * (LINE+2C+2D)
        self.send_data(0x2C)
        self.send_data(0x2D)

        self.send_command(Instructions.FRMCTR3)    # Frame rate ctrl - partial mode
        self.send_data(0x01)                 # Dot inversion mode
        self.send_data(0x2C)
        self.send_data(0x2D)
        self.send_data(0x01)                 # Line inversion mode
        self.send_data(0x2C)
        self.send_data(0x2D)

        self.send_command(Instructions.INVCTR)     # Display inversion ctrl
        self.send_data(0x07)                 # No inversion

        self.send_command(Instructions.PWCTR1)     # Power control
        self.send_data(0xA2)
        self.send_data(0x02)                 # -4.6V
        self.send_data(0x84)                 # auto mode

        self.send_command(Instructions.PWCTR2)     # Power control
        self.send_data(0x0A)                 # Opamp current small
        self.send_data(0x00)                 # Boost frequency

        self.send_command(Instructions.PWCTR4)     # Power control
        self.send_data(0x8A)                 # BCLK/2, Opamp current small & Medium low
        self.send_data(0x2A)

        self.send_command(Instructions.PWCTR5)     # Power control
        self.send_data(0x8A)
        self.send_data(0xEE)

        self.send_command(Instructions.VMCTR1)     # Power control
        self.send_data(0x0E)

        # if self._invert:
            # self.command(ST7735_INVON)   # Invert display
        # else:
            # self.command(ST7735_INVOFF)  # Don't invert display
        self.send_command(Instructions.INVOFF)

        self.send_command(Instructions.MADCTL)     # Memory access control (directions)
        self.send_data(0xC8)                 # row addr/col addr, bottom to top refresh

        self.send_command(Instructions.COLMOD)     # set color mode
        self.send_data(0x05)                 # 16-bit color

        self.send_command(Instructions.CASET)      # Column addr set
        self.send_data(0x00)                 # XSTART = 0
        self.send_data(self._offset_left)
        self.send_data(0x00)                 # XEND = ROWS - height
        self.send_data(self._width + self._offset_left - 1)

        self.send_command(Instructions.RASET)      # Row addr set
        self.send_data(0x00)                 # XSTART = 0
        self.send_data(self._offset_top)
        self.send_data(0x00)                 # XEND = COLS - width
        self.send_data(self._height + self._offset_top - 1)

        self.send_command(Instructions.GMCTRP1)    # Set Gamma
        self.send_data(0x02)
        self.send_data(0x1c)
        self.send_data(0x07)
        self.send_data(0x12)
        self.send_data(0x37)
        self.send_data(0x32)
        self.send_data(0x29)
        self.send_data(0x2d)
        self.send_data(0x29)
        self.send_data(0x25)
        self.send_data(0x2B)
        self.send_data(0x39)
        self.send_data(0x00)
        self.send_data(0x01)
        self.send_data(0x03)
        self.send_data(0x10)

        self.send_command(Instructions.GMCTRN1)    # Set Gamma
        self.send_data(0x03)
        self.send_data(0x1d)
        self.send_data(0x07)
        self.send_data(0x06)
        self.send_data(0x2E)
        self.send_data(0x2C)
        self.send_data(0x29)
        self.send_data(0x2D)
        self.send_data(0x2E)
        self.send_data(0x2E)
        self.send_data(0x37)
        self.send_data(0x3F)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x02)
        self.send_data(0x10)

        self.send_command(Instructions.NORON)      # Normal display on
        time.sleep(0.10)                # 10 ms

        self.send_command(Instructions.DISPON)     # Display on
        time.sleep(0.100)               # 100 ms

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.send_command(Instructions.CASET)       # Column addr set
        self.send_data(x0 >> 8)
        self.send_data(x0)                    # XSTART
        self.send_data(x1 >> 8)
        self.send_data(x1)                    # XEND
        self.send_command(Instructions.RASET)       # Row addr set
        self.send_data(y0 >> 8)
        self.send_data(y0)                    # YSTART
        self.send_data(y1 >> 8)
        self.send_data(y1)                    # YEND
        self.send_command(Instructions.RAMWR)       # write to RAM

    def display(self, image):
        self.set_window()
        pixel_bytes = list(image_to_data(image, self._rotation))
        print(len(pixel_bytes))
        self.send_data(pixel_bytes)

    def fill(self, color):
        self.set_window()
        self.send_command(Instructions.RAMWR)
        data = color * (1261)
        for y in range(13):
            self.send_data(data)


