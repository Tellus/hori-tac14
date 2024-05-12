# HORI Tac14 USB protocol

This file is an effort to document the communication protocol used by the HORI
Tactical Assault F14 Black edition.

Everything has been discovered by sniffing traffic between the FFXIV keymapping
tool and the USB device, using Wireshark.

I am not a USB expert, so expect me to conflate the workings of the HORI with
mechanisms that are normal for any USB device.

## Normal operation

The HORI (idVendor `0x0f0d`) presents itself as multiple devices:

- A USB hub to encompass its constituents
- A USB HID, the keypad - idProduct `0x013a`
- A joystick (game controller?) - idProduct `0x013b`

The joystick is only active/present/available when the HORI i in Analog+Keyboard
mode (as opposed to pure Keyboard mode).

The keypad portion is a USB HID class. When the user presses a butotn, the HORI
sends an interrupt containing the USB scan code of the pressed button. On
release, another interrupt is sent.

From what I can tell, the *base* functionality of the HORI works on Linux and
Steam out of the box, as long as the user has access rights to the device.
There should be a udev rule file in this repository that can be dumped in
`/etc/udev/rules.d/`. I expect this should work for most modern "user-friendly"
distros. If you're not using udev or systemd, or for some reason might have
other spicy features in your system, I expect you're enough of an expert to know
how to get access to the USB devices on your own :D

## Remapping

The device's keys can be remapped to any valid keyboard input (as well as some
gamepad inputs) using the remapper tool.

The remapper seems to rely entirely on SET_REPORT and GET_REPORT to perform all
editing actions on the device.

Basically, it's operations boil down to either reading current configurations or
writing new key configurations. It doesn't seem like the tool can forcefully
change the active key profile (1-8) but it CAN access the configurations from
all 8 profiles for both modes (A+K and K) at any time.

When communicating with the HORI, the remapper only sends or expects data
segments of 64 bytes. I have no idea if this is USB restriction/convention or
just how the tool is implemented. Because of this, a full configuration cannot
be sent or received with a single message, and the remapper sends several
messages covering several *pages*.

For all SET_REPORT operations, the data fragment has the form `0x01a5105aef10000000000000000000000000000000000000000000000000000000` (lots of padding). For brevity (and legibility), I'll omit bytes that seem to be unused.

### Reading

Reading key configurations goes through three phases:

#### Start with a "start read" command

SET_REPORT with the following parameters:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5105aef1000`

#### "Turn" to a configuration page and read it back

First a SET_REPORT "turning the page" to the requested page of keys:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5115aee1000`

The last two bytes of the data fragment is the `page`, and the third last byte
seems to be the `profile`. Thus, the first page of the first profile is `0x1000`
while the second page of the fifth profile is `0x1401`. **The page count when
reading does NOT match the page count when writing. When reading, each page
contains 16 keys. When WRITING, each page only contains 4 keys.**

Then, a GET_REPORT that returns 16 keys matching the input parameters.

- bmRequestType: `0xa1`
- bRequest: `0x01` (GET_REPORT)
- wValue: `0x0101`
- wIndex: `0x01`
- wLength: 65 <- I don't know if this is necessary to state explicitly

This returns 64 bytes of key configurations, 8 bytes per key. "Pure" keys (like
just the letter "G") are in the first 2 bytes. Compounded keys (say,
Ctrl+Shift+G) notes each modifier key's USB scan code before the final key.

- G: `0b 00 00 00`
- Ctrl+Shift+G: `e0 e1 0b 00`
- The function key is the (special?) value `26 00 00 ff`. `0x26` is "9" (I think - check notes), I don't know if this MUST be the "primary" key when defining the
function key.

#### End with a "stop reading" command

SET_REPORT with the following parameters:

- bmRequestType: `0x21`
- bRequest: `0x09` (SET_REPORT)
- wValue: `0x0201`
- wIndex: `0x01`
- data: `0x01a5125aed1000`

### Writing

WIP

## Notes

Every single operation seems prefixed with `0x01a5` but I can't tell if this has
any particular meaning.

It *seems* to be the case that four bits differ between reading and writing
operations. Two pairs of two adjacent bits are flipped. So far I haven't been
able to discern the pattern.

I don't know if it makes more sense to view the communication as hex-based
commands or look at the specific bits that are set for each message. I feel
confident in the last three bytes that point to profile and page. They seem
solid.

When reading back page 0 of any profile, the very first key is the physical
"Esc" key, "bound" to the escape USB scan code. This seems to suggest that the
key can actually be rebound, even if the tool won't allow it. Hm.

It *seems* like the LED backlight is set on page 12 (`0x0c`), 3rd parameter,
i.e. the ninth byte, i.e. index 8 (when zero-indexing).

I haven't mapped out how the data fragment / command line differs when
requesting different profiles across thw two modes, or when writing to them.
This should be a fairly simple sniff-trek with Wireshark, though.

It might be really useful to know what board the HORI is actually based on.

The board has a maintenance mode that can be activated by holding 1 and 2 while
plugging it in. This is used when updating firmware.