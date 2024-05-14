*Throughout these files I'll be referring to profile and page numbers. Unless
otherwise specified, these are zero-indexed in the source data.*

The following is the basic structure of the configuration's data model, as seen
through the USB traffic:

Mode (A+K or K) -> Profile -> Page

These are all set using the last four bytes of the "command string" (the first
14 bytes of the SET_REPORT data fragment).

`MP GG`, where:

- `M` is `0` for keyboard-only and `1` for A+K
- `P` is the profile number, starting with `0` and ending at `7`
- `GG` is the page, starting from `00` and running up to `07` on reads (over
`0x1e` = 30 on writes??)