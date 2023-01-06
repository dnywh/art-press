# Art Press

![Art Press Sequence.gif](https://res.cloudinary.com/dannywhite/image/upload/v1672986899/github/art-press-sequence.gif)

Art Press is a [Pi Frame](https://github.com/dnywh/pi-frame) app. It prints a random item from the Art Institute of Chicago’s collection to an e-ink display via Raspberry Pi. By default it selects only items classified as “woodcut” to suit the qualities (and limitations) of e-ink.

Art Press relies on the [Art Institute of Chicago’s API](http://api.artic.edu/docs/) to search for random art and its [IIIF Image API](http://api.artic.edu/docs/#iiif-image-api) to render a cropped image.

## Prerequisites

To run Art Press you need to first:

1. Join a Wi-Fi network on your Raspberry Pi
2. Enable SSH on your Raspberry Pi
3. Plug in a Waveshare e-Paper or similar display to your Raspberry Pi

Art Press works great with [Pi Frame](https://github.com/dnywh/pi-frame), which includes the Waveshare drivers amongst other things like a scheduling template. If you’d prefer not to use Pi Frame, you’ll need to upload the [Waveshare e-Paper display drivers](https://github.com/waveshare/e-Paper/tree/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd) (or similar) to your Raspberry Pi in a _lib_ directory that is a sibling of Art Press’. Here's an example:

```
.
└── art-press
└── lib
    └── waveshare_epd
        ├── __init__.py
        ├── epdconfig.py
        └── epd7in5_V2.py
```

Either way, Waveshare displays require some additional setup. See the [Hardware Connection](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual#Hardware_Connection) and [Python](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual#Python) sections of your model’s manual.

## Get started

If you haven’t already, copy all the contents of this Art Press repository over to the main directory of your Raspberry Pi.

### Set the display driver

Look for this line as the last import in _[app.py](https://github.com/dnywh/art-press/blob/main/app.py)_:

```python
from waveshare_epd import epd7in5_V2 as display
```

Swap out the `epd7in5_V2` for your Waveshare e-Paper display driver, which should be in the _lib_ directory. Non-Waveshare displays should be imported here too, although you’ll need to make display-specific adjustments in the handful of places `display` is called further on.

### Install required packages

See _[requirements.txt](https://github.com/dnywh/art-press/blob/main/requirements.txt)_ for a short list of required packages. Install each package on your Raspberry Pi using `sudo apt-get`. Here’s an example:

```bash
sudo apt-get update
sudo apt-get install python3-pil
sudo apt-get install python3-requests
```

### Run the app

Run Art Press just like you would any other Python file on a Raspberry Pi:

```bash
cd art-press
python3 app.py
```

Art Press is noisy by default. Look for the results in Terminal.

---

## Usage

### Run on a schedule

See [Pi Frame](https://github.com/dnywh/pi-frame) for a crontab template and usage instructions.

### Design options

Art Press contains several visual design parameters in _[app.py](https://github.com/dnywh/art-press/blob/main/app.py)_.

| Option         | Type    | Description                                                                                                                             |
| -------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `imageQuality` | String  | Corresponds to the [IIF quality parameter](https://iiif.io/api/image/2.0/#quality) with options `"default"`, `"gray"`, and `"bitonal"`. |
| `preferCrop`   | Boolean | Crops to the center of the original image if true. Uses `maskWidth` and `maskHeight`.                                                   |

### Save to folder

Art Press contains an `exportImages` boolean option in _[app.py](TODO)._ When `True` it saves both an image and text file to a timestamped directory within an _exports_ directory.
