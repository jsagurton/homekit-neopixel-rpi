# homekit-neopixel-rpi
homekit-neopixel-rpi 

[Demo Video](https://youtu.be/IMnxmEtBPBE)

<img src="image.jpg" width="100%">

## You need

Hardware:

  Raspberry Pi
  Neopixel strip

Software

  homebridge on Raspberry Pi
  python3
  nodejs


### Install 
Follow the directions in the HomeBridge documents to install HomeBridge and get it running as a daemon. You'll probably want to clone this repo to /var/lib/ so that the end location of `server.py` ends up being `/var/lib/homekit-neopixel-rpi/server.py`.

### Daemonize the server
For my own simplicity I've gone ahead and included the sudo that you'll almost certainly need in here.
```bash
# Install gunicorn
sudo apt-get install gunicorn3

# Copy neopixel.service to /etc/systemd/system
sudo cp neopixel.service /etc/systemd/system/neopixel.service

# Start and initialize the service.
sudo systemctl enable neopixel
sudo systemctl start neopixel
```

After this you should be able to see the status of the daemon using systemd, it should start on boot, etc. To see the status use `sudo systemctl status neopixel`.

### setting
```
# .homebridge/config
# add 
{
    "accessory": "HttpPushRgb",
    "name": "Neo Lamp2",
    "service": "Light",
    "switch": {
        "status": "http://localhost:5000/status",
        "powerOn": "http://localhost:5000/on",
        "powerOff": "http://localhost:5000/off"
    },
    "brightness": {
        "status": "http://localhost:5000/bright",
        "url": "http://localhost:5000/setbright/%s"
    },
    "color": {
        "status": "http://localhost:5000/color",
        "url": "http://localhost:5000/set/%s",
        "brightness": false
    }
},
{
    "accessory": "HttpPushRgb",
    "name": "Neo Rainbow2",
    "service": "Light",
    "switch": {
        "status": "http://localhost:5000/status",
        "powerOn": "http://localhost:5000/rainbow",
        "powerOff": "http://localhost:5000/off"
    },
    "brightness": {
        "status": "http://localhost:5000/bright",
        "url": "http://localhost:5000/setbright/%s"
    }
}
```


### Planned Changes/TODO

* [x] Split brightness functionality out so it's not tethered to color codes. This will allow changing the brightness of patterns - *DONE*, not very elegantly. It currently requires brightness computation to be done in *each* pattern's color "fetch" method, IE, the wheel method for rainbows.
* [ ] Configure device notifications so that when a pattern "device" is activated, other devices turn off and notify HomeBridge of this change.
* [x] Figure out what's up with the threads. Currently if you turn on the rainbow device, then tinker with the standard device, two different threads simultaneously communicate with the LED strip. It looks like there are some checks to handle this already, but it seems to take too long. I might have to kill the thread? - Some progress made here. I used a loop structure instead of constantly pushing more function calls on the stack recursively.
* [ ] Add more patterns
* [x] Ensure migration to [HomeBridge HTTP RGB Push](https://github.com/QuickSander/homebridge-http-rgb-push) is working as expected.
* [x] Daemonize the webserver.

[homebridge neopixel](https://www.studiopieters.nl/homebridge-neopixel-light/)
[RPi neipixel](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring)
