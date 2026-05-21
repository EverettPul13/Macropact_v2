import math

import digitalio
from neopixel_write import neopixel_write

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel.git"

# Pixel color order constants
RGB = (0, 1, 2)
"""Red Green Blue"""
GRB = (1, 0, 2)
"""Green Red Blue"""
RGBW = (0, 1, 2, 3)
"""Red Green Blue White"""
GRBW = (1, 0, 2, 3)
"""Green Red Blue White"""

class NeoPixel:
    def __init__(self, pin, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.n = n
        if pixel_order is None:
            self.order = GRBW
            self.bpp = bpp
        else:
            self.order = pixel_order
            self.bpp = len(self.order)
        self.buf = bytearray(self.n * self.bpp)
        # Set auto_write to False temporarily so brightness setter does _not_
        # call show() while in __init__.
        self.auto_write = False
        self.brightness = brightness
        self.auto_write = auto_write

    def deinit(self):
        """Blank out the NeoPixels and release the pin."""
        for i in range(len(self.buf)):
            self.buf[i] = 0
        neopixel_write(self.pin, self.buf)
        self.pin.deinit()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.deinit()

    def __repr__(self):
        return "[" + ", ".join([str(x) for x in self]) + "]"

    def _set_item(self, index, value):
        if index < 0:
            index += len(self)
        if index >= self.n or index < 0:
            raise IndexError
        offset = index * self.bpp
        r = 0
        g = 0
        b = 0
        w = 0
        if isinstance(value, int):
            if value>>24:
                raise ValueError("only bits 0->23 valid for integer input")
            r = value >> 16
            g = (value >> 8) & 0xff
            b = value & 0xff
            w = 0
            # If all components are the same and we have a white pixel then use it
            # instead of the individual components.
            if self.bpp == 4 and r == g and g == b:
                w = r
                r = 0
                g = 0
                b = 0
        elif (len(value) == self.bpp) or ((len(value) == 3) and (self.bpp == 4)):
            r, g, b, w = value if len(value) == 4 else value+(0,)
        else:
            raise ValueError("Color tuple size does not match pixel_order.")

        self.buf[offset + self.order[0]] = r
        self.buf[offset + self.order[1]] = g
        self.buf[offset + self.order[2]] = b
        if self.bpp == 4:
            self.buf[offset + self.order[3]] = w

    def __setitem__(self, index, val):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self.buf) // self.bpp)
            length = stop - start
            if step != 0:
                length = math.ceil(length / step)
            if len(val) != length:
                raise ValueError("Slice and input sequence size do not match.")
            for val_i, in_i in enumerate(range(start, stop, step)):
                self._set_item(in_i, val[val_i])
        else:
            self._set_item(index, val)

        if self.auto_write:
            self.show()

    def __getitem__(self, index):
        if isinstance(index, slice):
            out = []
            for in_i in range(*index.indices(len(self.buf) // self.bpp)):
                out.append(tuple(self.buf[in_i * self.bpp + self.order[i]]
                                 for i in range(self.bpp)))
            return out
        if index < 0:
            index += len(self)
        if index >= self.n or index < 0:
            raise IndexError
        offset = index * self.bpp
        return tuple(self.buf[offset + self.order[i]]
                     for i in range(self.bpp))

    def __len__(self):
        return len(self.buf) // self.bpp

    @property
    def brightness(self):
        """Overall brightness of the pixel"""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        # pylint: disable=attribute-defined-outside-init
        self._brightness = min(max(brightness, 0.0), 1.0)
        if self.auto_write:
            self.show()

    def fill(self, color):
        """Colors all pixels the given ***color***."""
        auto_write = self.auto_write
        self.auto_write = False
        for i, _ in enumerate(self):
            self[i] = color
        if auto_write:
            self.show()
        self.auto_write = auto_write

    def write(self):
        """.. deprecated: 1.0.0

             Use ``show`` instead. It matches Micro:Bit and Arduino APIs."""
        self.show()

    def show(self):
        """Shows the new colors on the pixels themselves if they haven't already
        been autowritten.

        The colors may or may not be showing after this function returns because
        it may be done asynchronously."""
        if self.brightness > 0.99:
            neopixel_write(self.pin, self.buf)
        else:
            neopixel_write(self.pin, bytearray([int(i * self.brightness) for i in self.buf]))