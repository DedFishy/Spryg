# Spryg
![Spryg Logo](logo.png)

A library for the [Sprig](https://sprig.hackclub.com/) game console by HackClub to write games using MicroPython.

## Installation
It's not too difficult to get set up. Being that I'm not particularly great at writing instructions, it may be good to have experience with Picos and MicroPython first.
### Setting up MicroPython
- [Download Latest MicroPython](https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2)
- Hold down BOOTSEL on your Pico (the big white button) and plug it in to your computer
- Move the downloaded MicroPython file into the Pico when it's mounted as a flash device
### Setting up Spryg
- Go to the latest release on GitHub and download `ST7735.py` (the library for the screen by GuyCarver), and `main.py` (the actual library itself)
- Open your Pico in a program where you can access the MicroPython filesystem. I recommend [Thonny](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/2) as it gets the job done.
- Move `main.py` and `ST7735.py` to the Pico

You now have Spryg installed on your Pico. When you turn on your Sprig, it will tell you there is no game loaded. You must install one. The way to do this is to put a file called `game.py` on your Pico. The library will call the function `run` in your game, and it must accept one argument which is the Spryg library class.
You can copy a game from the examples folder if you wish, and move it over to the Pico. Make sure its name is `game.py`, otherwise Spryg won't find it.

## Troubleshooting

#### The speaker starts screaming

This will happen when the speaker is not properly uninitialized. It can be caused by an unrecoverable crash or other bug. Simply restart your console.

#### Another issue

If you have an issue that was *somehow* not listed in this one-problem troubleshooting document, feel free to go to the Issues tab in Github and report a bug.

## It doesn't have `INSERT FEATURE`

Ask for it to be added in the Issues tab on Github, or do it yourself with a pull request. I'm likely too lazy to do it myself.
