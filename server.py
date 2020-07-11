import time
import board
import neopixel
import threading

from flask import Flask

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D21

# The number of NeoPixels
num_pixels = 350

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False,
                           pixel_order=ORDER)
app = Flask(__name__)

rgb=(255,255,255)
status = 0
enableRainbow = False
# I'm not entirely sure what to do with the ratio yet. Repeated brightness adjustments cause problems. Maybe max this until >=1 of the component values is 255?
rgbRatio=(255, 255, 255)
brightness = 1

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    global brightness
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    r, g, b = int(brightness * r), int(brightness * g), int(brightness * b)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rainbow_cycle():
  global enableRainbow
  while enableRainbow:
      for j in range(255):
	# This is necessary because with longer strands this nested loop just takes foreverrrrrr, so breaking will force a re-eval. It's hacky, and could
        # be done more cleanly probably. Consider refactoring in the future to move the thread object to be global, making it stoppable and then implementing
        # more consistent checks instead of having random globals flying all over the place. Blame the wine.
        if not enableRainbow:
          break
        for i in range(num_pixels):
          pixel_index = (i * 256 // num_pixels) + j
          pixels[i] = wheel(pixel_index & 255)
        pixels.show()
  off()
  return

@app.route("/status")
def status():
  global status
  return str(status)


@app.route("/bright")
def bright():
  global rgb
  print(str(int(brightness*100)))
  return str(int(brightness*100))

@app.route("/color")
def color():
  global rgb
  value = rgb_to_hex(rgb)
  return str(value)


@app.route("/rainbow")
def rainbow():
  global enableRainbow
  global status
  status = 1
  global rgb
  pixels.fill(rgb)
  pixels.show()
  if(enableRainbow==False):
    enableRainbow=True
    t = threading.Thread(target = rainbow_cycle)
    t.start()
  return "on"

# TODO: Test this actually works. Can this be condensed in to the other /bright route? Is it easier to just have one with no args and one with args?
# TODO: Handle case where brightness is 0.
# More Info on setBrightness() call: https://forums.adafruit.com/viewtopic.php?t=41143
@app.route("/setbright/<value>")
def setbright(value):
  global rgb
  global brightness
  # pixels.fill(rgb)
  brightness = int(value) / 100
  rgb = tuple(int(brightness * v) for v in rgbRatio)
  print("rgb inside setbright", rgb)
  # print("brightness, inside setbright", brightness)
  # pixels.show()
  return str(int(brightness*100))

@app.route("/on")
def on():
  global status
  status = 1
  global rgb
  pixels.fill(rgb)
  pixels.show()
  return "on"

@app.route("/off")
def off():
  global status
  status = 0
  global enableRainbow
  enableRainbow=False
  pixels.fill((0,0,0))
  pixels.show()
  return "off"

@app.route("/set/<values>")
def set(values):
  global enableRainbow
  enableRainbow=False
  h = values
  #h = values.replace("NA","0").replace("N","1")
  global rgb
  global rgbRatio
  #rgb=hex_to_rgb(h)
  rgb=tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
  # Figure out which of these is the highest value, and how far it needs to scale to get to 255
  rgbRatio = tuple(int(v*255/max(rgb)) for v in rgb)
  print("rgb, inside set call", rgb)
  print("rgbRatio, inside set call", rgbRatio)
  pixels.fill(rgb)
  pixels.show()
  return "ok"
