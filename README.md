# hori-tac14
OS-independent key remapper and other useful tools for the HORI Tactical Assault Commander F14 Black (Hori Tac14) game keypad.

## Introduction

HORI has released a remapper for the HORI Tactical Assault Commander F14 Black (... or just hori-tac14) [through](https://hori.co.uk/hpc-047u/) entirely [too](https://stores.horiusa.com/HPC-047U/app) many [links](https://store-kmne79kvbv.mybigcommerce.com/content/FF14%20Keypad%20Install%201.17.zip).

It requires the user to install the *CORRECT* Visual C++ redistributables
themselves (2010 edition, x86 only, not x64), asks them to run a firmware update
(which seems unnecessary on recently shipped models), and then use a program
that doesn't even remember basic language settings between launches.

Safe to say I have a few issues with the program, and that's before mentioning
that it is entirely useless on Linux. If run through Wine, it will fail entirely
to detect and work with a plugged in device. In a VM, you may need to pass along
the entire USB bus or the application won't recognize it either. All this, just
to rebind the keys!

Anyway...

The goal of this project is to build a platform-independent variant of the key
remapper (although most importantly for Linux and Mac users), useable from a
single executable/package, with largely the same features of the official tool.

**Note** that this program aims be the Hori version of
[OpenRazer](https://openrazer.github.io) rather than compete against
[input-remapper](https://github.com/sezanzeb/input-remapper) at any level. For
basic remapping of the Hori, `input-remapper` will work *just fine*!

However, if you are interested in any of the following features, you might want
to try out this program.

- Manage thumbstick deadzones
- Change thumbstick behaviour in A+K mode (left stick, right stick, dpad)
- Toggle LED backlight on profiles
- Store mappings on the device instead of in a remapper config.
- Change mappings of any part of the configuration without having to switch over
  to it first.
- Move (or disable!) the `Fn` key.

## Repository structure

`wireshark/plugins` contain Lua plugins used during analysis of the packets sent
between the device and computer. They are very barbones, mostly used to help
visualize basic structures of the data going back and forth. These are not
full-fledged dissectors, and they are **very** slow on large captures.

`udev/40-hori-tac14.rules` contains a udev rules file that grants users access
to the device automatically when it is plugged in. If you're comfortable
managing your Linux system, it should be sufficient to place the file in
`/etc/udev/rules.d/` (make sure it has the same permissions as the other rule
files) and reload your udev rules (`udevadm control --reload` - or just reboot
your computer). Next time the HORI is plugged in, you should have user access.
*I'm not sure if this is strictly necessary on most systems. Need to test out
the program without this to be sure.*

`remapper` contains the program itself, written in Python. Note that the
structure within the program will be *heavily* in flux until v1.0 is released.
It's expected that there will be a CLI, GUI, and library version available.

## Loose checklist

- [ ] Analyze USB traffic
  - [x] Protocol command structure (7 bytes) (I use "_" for the unused half of an octet/byte for a given point)
      - `0x01` (always)
      - `0xa5` (always)
      - `0x1_` for READ `0x_` for WRITE
      - `0x_0` for START, `0x_1` for any operation before END, `0x_2` and then another with `0x_3` for WRITE END, and just `0x_2` for READ END
      - The complement for bytes 1 and 2. `0xa5` -> `0x5a`, and e.g. `0x12` -> `0xed`
      - `0x1_` for A+K, `0x0_` for keyboard only.
      - `0x_0` to `0x_7`, profile
      - `0x00` to `0x1f` for virtual page (0-7 during READ; 0-31 during WRITE)
  - [ ] Reading (*observe* known values coming back over the wire)
    - [x] Basic (one-off)
    - [x] Differentiation
      - [x] Page
      - [x] Profile
      - [x] A+K or K mode
      - [x] Alternate key functions (Fn+)
    - [x] Stick deadzones
    - [ ] Stick type in A+K mode
      - [ ] Left
      - [ ] Right
      - [ ] dpad
      - [x] Keyboard (same as for Keyboard only)
  - [ ] Writing (*observe* that values are written over the wire)
    - [x] Keyboard inputs (including composite)
    - [x] LED backlight
    - [ ] Gamepad inputs
  - [ ] Value types
    - [x] Single key
    - [x] Composite (modifier + key)
    - [x] Gamepad input
    - [ ] LED backlight
    - [ ] ... others?
- [ ] Python library
  - [x] Init
  - [ ] Read configuration
    - [x] Keys (escape, 1-22)
    - [x] Thumbstick (in keyboard mode)
    - [ ] LED backlight
    - [ ] Deadzones
  - [ ] Write configuration
  - [ ] (Optional) backup/restore configuration (JSON/YAML) (*I think trying to support the official tools' own profile format might be too much work right now*)
- [ ] GUI application