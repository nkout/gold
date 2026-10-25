Chance PI main board (DIP version, layout by DesAlex) - Gerber package
Source: Chance_layout_from_DesAlex.lay (Sprint-Layout 5), the "PCB for DIP version" download.
Schematic: Andy_F, fandy.vov.ru (sheme.gif). Firmware: v0.8.4 (MCP3201 or ADS7816).

Order as: 2 layers, 1.6 mm FR4, HASL. Board 90.46 x 65.06 mm.
Upload only the 7 fab files (*.gbl *.gtl *.gbs *.gts *.gto *.gm1 *.drl).

Changes from the .lay file
- B_Cu: bottom copper exactly as drawn (single-sided original).
- F_Cu: pads only, plus ONE 0.6 mm track joining (16.51,-22.86) and (16.51,-30.48) in the original
  coordinates, under the ATmega8. It joins VCC (ATmega pin 7, 78L05 output) to AVCC (pin 20) and
  MCP3201 VDD, which are separate copper nets in the original (wire link, no silkscreen).
- Holes: the original drills are hand-drilling guides (0.4-0.6 mm). 82 stacked duplicate pads
  (0.05-0.18 mm apart) merged into single holes. Finished plated sizes:
  1.0 mm ATmega8 (28) and general parts; 0.8 mm DIP-8 sockets and C5; 0.9 mm small pads;
  1.1 mm TO-220 (IRF9640) and other large pads; 1.2 mm wire terminals; 3.0 mm mounting (plated).
- ATmega8 footprint is on a 2.5 mm pitch (not 2.54): 0.52 mm over 14 pins. Pads left in place,
  holes enlarged to 1.0 mm. The end pins need a slight bend; a turned-pin socket may not fit.
- Edge_Cuts: rectangle 0.8 mm outside the copper. The original has no outline layer.
- F_SilkS: original component outlines (no designators or values exist in the original), plus
  labels ATmega8, MCP3201, OP37, 7660 inside the IC outlines.
- Soldermask: pad + 0.1 mm on both sides.

Not on the board: ISP header X2 (MOSI is unconnected). Program the ATmega8 off-board.
Minimum copper gap 0.196 mm (near the left crystal capacitors), from the original layout.
