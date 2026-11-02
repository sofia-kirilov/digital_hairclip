"""
Digital hair clip enclosure for the LilyGO T-Display (original ESP32, 1.14" screen)
+ 602540 LiPo battery. Parametric CadQuery script.

Run:  python hairclip_case.py
Out:  hairclip_case.step (both parts, import into Onshape)
      case_shell.stl, back_lid.stl (for Bambu Studio)

Measure YOUR board + battery with calipers and edit the numbers below.
All units mm.
"""
import cadquery as cq

# ---------- measure these ----------
BOARD_L   = 51.6   # T-Display PCB length (not counting USB-C overhang)
BOARD_W   = 25.2   # PCB width
PCB_T     = 1.6    # PCB thickness
UNDER_GAP = 1.4    # space for parts on the back of the PCB (chip, JST plug)
BATTERY_T = 6.0    # 602540 = 6.0 thick x 25 wide x 40 long

# ---------- fit / style ----------
CLR       = 0.30   # clearance around the board, per side
WALL      = 1.6    # side wall thickness
FRONT_T   = 1.2    # front plate thickness (lip that holds the board)
LIP       = 1.5    # how far the front lip overlaps the PCB edge
BTN_ZONE  = 15.0   # open area at the USB end for the 2 front buttons
LID_T     = 1.2    # back lid thickness
RABBET    = 0.8    # ledge the lid sits on
LID_CLR   = 0.12   # lid clearance per side (raise if the lid is too tight)
CORNER_R  = 2.4    # outer corner rounding
EDGE_R    = 0.8    # front edge rounding

USB_W     = 12.5   # USB-C cable plug opening width
SW_FROM_USB_END = 12.0  # side reset switch centre, measured from the USB end
SW_LEN    = 8.0
SW_BOTH_SIDES = True    # cut the side-switch notch on both long sides

CLIP_RECESS = True      # shallow outline on the lid for gluing the clip
CLIP_L, CLIP_W, CLIP_D = 46.0, 13.0, 0.4

# ---------- derived ----------
PL = BOARD_L + 2 * CLR          # pocket length
PW = BOARD_W + 2 * CLR          # pocket width
OL = PL + 2 * WALL              # outer length
OW = PW + 2 * WALL              # outer width
INNER_D = PCB_T + UNDER_GAP + BATTERY_T + 0.3   # below the lip to the lid
H = FRONT_T + INNER_D + LID_T                   # total shell height
Z_PCB_TOP = H - FRONT_T                         # PCB top sits against the lip

# Coordinates: X along length (+X = USB end), Y across, Z=0 back, Z=H front.


def rounded_box(l, w, h, r, z0=0.0):
    return (cq.Workplane("XY").workplane(offset=z0)
            .rect(l, w).extrude(h).edges("|Z").fillet(r))


def make_shell():
    body = rounded_box(OL, OW, H, CORNER_R)
    body = body.faces(">Z").edges().fillet(EDGE_R)

    # main pocket for board + battery
    body = body.cut(rounded_box(PL, PW, Z_PCB_TOP, 0.6))

    # rabbet (ledge) for the back lid
    body = body.cut(rounded_box(PL + 2 * RABBET, PW + 2 * RABBET, LID_T, 1.0))

    # display window (lip on 3 sides)
    win_l = PL - LIP - BTN_ZONE
    win = (cq.Workplane("XY").workplane(offset=Z_PCB_TOP - 0.1)
           .center(-PL / 2 + LIP + (win_l + 3) / 2, 0)
           .rect(win_l + 3, PW - 2 * LIP).extrude(FRONT_T + 1)  # +3 runs into button zone
           .edges("|Z").fillet(1.0))
    body = body.cut(win)

    # button zone at the USB end: fully open front
    bz = (cq.Workplane("XY").workplane(offset=Z_PCB_TOP - 0.1)
          .center(PL / 2 - BTN_ZONE / 2 - 0.05, 0)
          .rect(BTN_ZONE + 0.1, PW).extrude(FRONT_T + 1))
    body = body.cut(bz)

    # USB-C notch in the end wall (open to the front)
    usb_bottom = Z_PCB_TOP - 1.9
    usb = (cq.Workplane("XY").workplane(offset=usb_bottom)
           .center(PL / 2 + WALL / 2, 0)
           .rect(WALL * 3, USB_W).extrude(H))
    body = body.cut(usb)

    # side reset-switch notch(es), open to the front
    sw_x = PL / 2 - CLR - SW_FROM_USB_END
    sides = [1, -1] if SW_BOTH_SIDES else [1]
    for s in sides:
        n = (cq.Workplane("XY").workplane(offset=Z_PCB_TOP - 0.6)
             .center(sw_x, s * (PW / 2 + WALL / 2))
             .rect(SW_LEN, WALL * 3).extrude(H))
        body = body.cut(n)

    # snap grooves in the rabbet wall (match the lid ribs)
    for x in (-15.0, 15.0):
        for s in (1, -1):
            d = (cq.Workplane("YZ").circle(0.6).extrude(7)
                 .translate((x - 3.5, s * (PW / 2 + RABBET), LID_T / 2)))
            body = body.cut(d)

    # pry notch at the pin end so the lid pops off with a fingernail
    pry = (cq.Workplane("XY").center(-(PL / 2 + RABBET), 0)
           .rect(1.6, 6).extrude(0.8))
    body = body.cut(pry)
    return body


def make_lid():
    ll = PL + 2 * RABBET - 2 * LID_CLR
    lw = PW + 2 * RABBET - 2 * LID_CLR
    lid = rounded_box(ll, lw, LID_T, 1.0 - LID_CLR)
    # snap ribs
    for x in (-15.0, 15.0):
        for s in (1, -1):
            nub = (cq.Workplane("YZ").circle(0.5).extrude(6)
                   .translate((x - 3.0, s * (lw / 2 - 0.3), LID_T / 2)))
            lid = lid.union(nub)
    # clip outline on the outside (Z=0 face is the outside)
    if CLIP_RECESS:
        rec = (cq.Workplane("XY").slot2D(CLIP_L, CLIP_W).extrude(CLIP_D))
        lid = lid.cut(rec)
    return lid


if __name__ == "__main__":
    shell = make_shell()
    lid = make_lid()

    asm = cq.Assembly()
    asm.add(shell, name="case_shell", color=cq.Color(0.55, 0.36, 0.45))
    asm.add(lid, name="back_lid", loc=cq.Location((0, 0, -6)),
            color=cq.Color(0.85, 0.65, 0.75))
    asm.save("hairclip_case.step")

    cq.exporters.export(shell, "case_shell.stl", tolerance=0.02, angularTolerance=0.1)
    # lid printed flat, outside face down
    cq.exporters.export(lid, "back_lid.stl", tolerance=0.02, angularTolerance=0.1)
    print(f"Outer size: {OL:.1f} x {OW:.1f} x {H:.1f} mm")
