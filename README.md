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
to detect and work with a plugged in device. In a VM, you need to pass along the
entire USB bus or the application won't recognize it either. All this, just to
rebind the keys!

Anyway...

The goal of this project is to build a platform-independent variant of the key
remapper (although most importantly for Linux and Mac users), useable from a
single executable/package, with largely the same features of the official tool.

## Repository structure

`wireshark/plugins` contain Lua plugins used during analysis of the packets sent
between the device and computer. They are very barbones, mostly used to help
visualize basic structures of the data going back and forth. These are not
full-fledged dissectors, and they are **very** slow on large captures.

`udev/40-hori-tac14.rules` contains a udev rules file that grants users access
to the device automatically when it is plugged in. If you're comfortable
managing your Linux system, it should be sufficient to place the file in
`/etc/udev/rules.d/` (make sure it has the same permissions as the other rule files) and reload your udev rules (`udevadm control --reload` - or
just reboot your computer). Next time the HORI is plugged in, you should have user access.

## Loose checklist

- [ ] Analyze USB traffic
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
  - [ ] Init
  - [ ] Read configuration (mode, profile, and page)
  - [ ] Write configuration
  - [ ] (Optional) backup/restore configuration (JSON/YAML) (*I think trying to support the official tools' own profile format might be too much work right now*)
- [ ] GUI application