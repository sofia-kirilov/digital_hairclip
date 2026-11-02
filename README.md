# Digital Hair Clip

A wearable digital hair clip. It's an ESP32 with a 1.14" screen in a 3D-printed case. It plays pixel-art animations, and you change them from your phone over Wi-Fi. You don't need an app.

## Features

- Built-in animations: blinking face, sparkles, beating heart, scrolling text, and a clock
- Draw your own animation (up to 8 frames) on your phone and send it to the clip
- Color presets plus custom colors, brightness, speed, and rotation
- Settings and drawings are kept after power-off
- Wi-Fi turns itself off after 10 minutes of no activity. Deep sleep is one button hold away.
- The case is parametric, so you can change the dimensions in one Python file

## Hardware

| Part | Notes |
|---|---|
| LilyGO T-Display (ESP32, 1.14" ST7789) | The original version, with pins 36/37/38/39 on one side. **Not** the T-Display S3. |
| 602540 LiPo battery (3.7 V) | 6 × 25 × 40 mm, with a JST 1.25 mm plug that matches the board |
| Snap or alligator hair clip | Glued to the back lid |
| Super glue, beads (optional) | For decorating |

## Files

```
digital-hairclip/
├── README.md
├── cad/
│   ├── hairclip_case.py     # parametric source (CadQuery)
│   ├── hairclip_case.step   # both parts, for Onshape / Fusion
│   ├── case_shell.stl
│   └── back_lid.stl
└── firmware/
    └── HairClip/
        ├── HairClip.ino
        └── web_page.h       # the phone control page
```

## 1. Print the case

1. Measure your board and battery with calipers. If your numbers differ from the defaults, edit the top of `cad/hairclip_case.py` and run:
   ```
   pip install cadquery
   python hairclip_case.py
   ```
2. Print `case_shell.stl` front face down and `back_lid.stl` flat. PLA works fine. No supports needed.
3. To edit in Onshape, go to **Import** and choose `hairclip_case.step`. It comes in as two parts.

Default outer size: **55.4 × 29.0 × 11.7 mm**.

If the lid is too tight or too loose, change `LID_CLR` and reprint just the lid.

## 2. Flash the firmware

1. In the Arduino IDE, open Boards Manager and install **esp32 by Espressif Systems** (2.x or 3.x).
2. In Library Manager, install **LovyanGFX**. You don't need to edit any config files; the display pins are set in the sketch.
3. Open `firmware/HairClip/HairClip.ino` and select the board **ESP32 Dev Module**. Then upload.
   - If the upload won't start, hold the GPIO0 button while you plug in USB.

## 3. Assemble

1. Plug the battery into the JST socket on the back of the board.
2. Put the board into the shell from the back, screen first, with the USB-C end at the cutout.
3. Put the battery behind the board and snap on the lid.
4. Glue the hair clip into the oval on the lid, then add beads wherever you want.

## 4. Use it

1. On your phone, join the Wi-Fi network **HairClip-XXXX** with the password `sparkle123`. Your phone will say "No Internet." That's expected.
2. Open **http://192.168.4.1** (or http://hairclip.local).
3. Pick an animation, change the colors, type text (`<3` makes a heart), or draw your own animation.

Opening the page also sets the clip's clock to your phone's time.

### Buttons

| Button | Short press | Hold 1.5 s |
|---|---|---|
| GPIO0 | Next animation | Rotate screen |
| GPIO35 | Wi-Fi on/off | Deep sleep (press again to wake) |

## Battery tips

- Wi-Fi uses about 3× the power of the screen alone. Set your animation, then turn Wi-Fi off from the page or with GPIO35.
- Lowering the brightness extends battery life the most after that.
- Plug in USB-C to charge. The page shows the battery level.

## Customizing

These settings are at the top of `HairClip.ino`:

- `AP_PASSWORD`: Wi-Fi password (8 characters minimum)
- `MDNS_NAME`: the `.local` address
- `WIFI_IDLE_OFF_MS`: how long before Wi-Fi turns itself off
- `CELL`: the size of each "big pixel" on screen

To add an animation:

1. Write a function that clears the grid and calls `setPx(x, y, 1)`. Use `2` for the accent color.
2. Add it to the `Anim` enum and the `ANIM_NAMES` list.
3. Add a `case` for it in `loop()`.

The phone page picks up the new animation automatically.
