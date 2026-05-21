# Import the GPIO pin definitions for the Raspberry Pi Pico
import board

from kmk.extensions.rgb import RGB

# Import the main keyboard firmware class specifically for the MacroPact board
from kmk.kmk_keyboard import KMKKeyboard

# KC = keyboard keycodes
# make_key = lets us create custom "virtual" keys with special behavior
from kmk.keys import KC, make_key

# Import the rotary encoder class
from kmk.rotary_encoder import Encoder

# Import IPS display support
from kmk.ips import IPS, ips_config


# Create the main keyboard object
# This represents the entire macropad
keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP0, board.GP1, board.GP2, board.GP3, board.GP4)
keyboard.row_pins = (board.GP5, board.GP6, board.GP7, board.GP8)

keyboard.diode_orientation = "COL2ROW"

rgb = RGB(
    pixel_pin=board.GP28,
    num_pixels=27,
 )


# Optional debugging
# Uncommenting this line prints debug info to serial
keyboard.debug_enabled = True



# =========================================================
# ROTARY ENCODER FUNCTIONS
# =========================================================

# This function runs whenever Encoder A is rotated
# "direction" is:
#   > 0  = clockwise
#   < 0  = counterclockwise
def onRotateA(direction):

    # If turned clockwise
    if(direction > 0):

        # Tap Shift + ]
        # KC.RBRC = right bracket key ]
        # KC.LSFT() wraps the key in Shift
        keyboard._state.tap_key(KC.LSFT(KC.RBRC))

    # If turned counterclockwise
    elif(direction < 0):

        # Tap Shift + [
        keyboard._state.tap_key(KC.LSFT(KC.LBRC))



# Encoder A behavior while RGB VALUE mode is active
# VALUE = brightness
def rgbv_onRotateA(direction):

    # Increase brightness
    if(direction > 0):
        rgb.increase_val()

    # Decrease brightness
    elif(direction < 0):
        rgb.decrease_val()



# Encoder A behavior while RGB HUE mode is active
def rgbh_onRotateA(direction):

    # Rotate through colors
    if(direction > 0):
        rgb.increase_hue()

    # Rotate opposite direction through colors
    elif(direction < 0):
        rgb.decrease_hue()



# Encoder A behavior while RGB SATURATION mode is active
# SATURATION = intensity/vividness of the color
def rgbs_onRotateA(direction):

    # Increase saturation
    if(direction > 0):
        rgb.increase_sat()

    # Decrease saturation
    elif(direction < 0):
        rgb.decrease_sat()

# Rainbow effect
def set_rainbow(*args, **kwargs):
    rgb.animation_mode = "rainbow"


# Swirl effect
def set_swirl(*args, **kwargs):
    rgb.animation_mode = "swirl"


# Breathing effect
def set_breathing(*args, **kwargs):
    rgb.animation_mode = "breathing"


# Static red
def set_red(*args, **kwargs):
    rgb.animation_mode = "static"
    rgb.set_hsv_fill(0, 255, 255)


# Static blue
def set_blue(*args, **kwargs):
    rgb.animation_mode = "static"
    rgb.set_hsv_fill(170, 255, 255)


# Gamer purple
def set_purple(*args, **kwargs):
    rgb.animation_mode = "static"
    rgb.set_hsv_fill(200, 255, 255)



# Encoder B rotation behavior
def onRotateB(direction):

    # Clockwise
    if(direction > 0):

        # Press ]
        keyboard._state.tap_key(KC.RBRC)

    # Counterclockwise
    elif(direction < 0):

        # Press [
        keyboard._state.tap_key(KC.LBRC)


# =========================================================
# FUNCTIONS THAT CHANGE WHAT ENCODER A DOES
# =========================================================

# Return Encoder A to default mode
def set_default_handler(*args, **kwargs):

    # Change Encoder A's rotation function
    keyboard.encoders[0].onRotate = onRotateA



# Set Encoder A to RGB brightness mode
def set_handler_rgbv(*args, **kwargs):

    # Redirect Encoder A rotation
    keyboard.encoders[0].onRotate = rgbv_onRotateA



# Set Encoder A to RGB hue/color mode
def set_handler_rgbh(*args, **kwargs):

    keyboard.encoders[0].onRotate = rgbh_onRotateA



# Set Encoder A to RGB saturation mode
def set_handler_rgbs(*args, **kwargs):

    keyboard.encoders[0].onRotate = rgbs_onRotateA



# =========================================================
# ENCODER SETUP
# =========================================================

# Create both rotary encoders
#
# Encoder A:
#   GP0 = encoder signal A
#   GP1 = encoder signal B
#
# Encoder B:
#   GP2 = encoder signal A
#   GP3 = encoder signal B
keyboard.encoders = [
    Encoder(board.GP0, board.GP1, onRotateA),
    Encoder(board.GP2, board.GP3, onRotateB)
]



# =========================================================
# IPS DISPLAY SETUP
# =========================================================

# Create the display object
keyboard.ips = IPS()

keyboard.extensions.append(rgb)


# =========================================================
# LAYER KEYS
# =========================================================

# "Momentarily activate layer while held"
#
# Layer 1 key
LAYER1 = KC.MO(1)

# When pressed:
# load the layer 1 bitmap/image onto the display
LAYER1.after_press_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L1.bmp")
)

# When released:
# return to layer 0 image
LAYER1.after_release_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L0.bmp")
)



# Same thing for Layer 2
LAYER2 = KC.MO(2)

LAYER2.after_press_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L2.bmp")
)

LAYER2.after_release_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L0.bmp")
)

# =========================================================
# LAYER 3
# =========================================================

LAYER3 = KC.MO(3)

LAYER3.after_press_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L3.bmp")
)

LAYER3.after_release_handler(
    lambda *args, **kwargs: keyboard.ips.load_bitmap("L0.bmp")
)


# =========================================================
# CUSTOM RGB MODE KEYS
# =========================================================

# make_key() creates a custom virtual key
#
# on_press = function that runs when pressed
# on_release = function that runs when released

# RGB brightness control mode
RGBV = make_key(
    on_press=set_handler_rgbv,
    on_release=set_default_handler
)

# RGB hue/color control mode
RGBH = make_key(
    on_press=set_handler_rgbh,
    on_release=set_default_handler
)

# RGB saturation control mode
RGBS = make_key(
    on_press=set_handler_rgbs,
    on_release=set_default_handler
)

RAINBOW = make_key(on_press=set_rainbow)

SWIRL = make_key(on_press=set_swirl)

BREATHING = make_key(on_press=set_breathing)

BLUERGB = make_key(on_press=set_blue)

REDRGB = make_key(on_press=set_red)

PURPLERGB = make_key(on_press=set_purple)



# =========================================================
# LAYER SWITCH KEYS
# =========================================================

current_layer = 0


def update_layer():

    keyboard.active_layers = [current_layer]

    keyboard.ips.load_bitmap(f"L{current_layer}.bmp")

    print("Layer:", current_layer)


def next_layer(*args, **kwargs):

    global current_layer

    if current_layer < 3:
        current_layer += 1

    update_layer()


def previous_layer(*args, **kwargs):

    global current_layer

    if current_layer > 0:
        current_layer -= 1

    update_layer()


NEXTLAYER = make_key(on_press=next_layer)

PREVLAYER = make_key(on_press=previous_layer)



# =========================================================
# KEYMAP
# =========================================================

# keyboard.keymap is a list of layers
#
# Layer 0 = default layer
# Layer 1 = secondary layer
# Layer 2 = RGB control layer
# Layer 3 = Cyrus + Rohan Layer (FRC programming macros)

keyboard.keymap = [

    # =====================================================
    # LAYER 0
    # =====================================================
    [
        KC.MPLY, KC.MNXT, KC.MPRV, KC.MUTE, KC.NO,
        
        KC.VOLU, KC.LCTL(KC.C), KC.LCTL(KC.V), KC.CAPS, NEXTLAYER,

        KC.VOLD, KC.LCTL(KC.Z), KC.LCTL(KC.Y), KC.PGUP, PREVLAYER,
        
        KC.LCTL(KC.S), KC.NO, KC.NO, KC.PGDN, KC.NO,
    ],



    # =====================================================
    # LAYER 1
    # =====================================================
    [
        KC.WWW_BACK, KC.WWW_FORWARD, KC.WWW_REFRESH, KC.WWW_STOP, KC.NO,
        
        KC.SYSTEM_SLEEP,  KC.SYSTEM_WAKE, KC.SYSTEM_POWER, KC.LALT(KC.F4), NEXTLAYER,

        KC.LCMD, KC.UP, KC.LCMD(KC.T), KC.LCTL(KC.LALT(KC.DEL)), PREVLAYER,
        
        KC.LEFT, KC.DOWN, KC.RIGHT, KC.NO, KC.NO,
    ],



    # =====================================================
    # LAYER 2 (RGB CONTROL)
    # =====================================================
    [
        RAINBOW, SWIRL, BREATHING, REDRGB, KC.NO,

        BLUERGB, PURPLERGB, KC.NO, KC.NO, NEXTLAYER,

        KC.NO, KC.NO, KC.NO, KC.NO, PREVLAYER,

        KC.NO, KC.NO, KC.NO, KC.NO, KC.NO,
    ],


    # =====================================================
    # LAYER 3 (rohan + cyrus layer// FRC programming + driver macros)
    # =====================================================
    [
        KC.send_string("10.51.99.12:5801"), KC.LCTL(KC.LALT(KC.B)), KC.LCTL(KC.LALT(KC.D)), KC.LCTL(KC.LALT(KC.G)), KC.NO,

        KC.send_string("10.51.99.11:5801"), KC.send_string("10.51.99.13:5801"), KC.F7, KC.F8, NEXTLAYER,

        KC.LCTL(KC.LALT(KC.E)), KC.LCTL(KC.LALT(KC.T)), KC.LCTL(KC.LALT(KC.A)), KC.LCTL(KC.LALT(KC.S)), PREVLAYER,

        KC.LCTL(KC.LALT(KC.D)), KC.LCTL(KC.LALT(KC.Q)), KC.LCTL(KC.LALT(KC.P)), KC.LCTL(KC.LALT(KC.M)), KC.TRNS,
    ],
]


# =========================================================
# MAIN PROGRAM START
# =========================================================

# This only runs when the file is directly executed
if __name__ == '__main__':

    # Load the default layer image and rgb setting on startup
    keyboard.ips.load_bitmap("L0.bmp")
    rgb.animation_mode = "rainbow"

    # Start the keyboard firmware
    #
    # This enters the main keyboard loop forever:
    #   - scans keys
    #   - scans encoders
    #   - updates RGB
    #   - handles USB HID
    # prints a message to ensure the code actually works and runs
    print("STARTED")
    keyboard.go()
