---
trigger: always_on
---

# Live KiCad Progress & Visual Update Rule

Whenever working on KiCad schematic or PCB tasks:
1. **Live Step-by-Step Reporting:** Proactively report each operation being executed (e.g. parsing netlist, setting coordinates, creating copper zones, executing DRC).
2. **Automated Visual Feedback:** After making layout modifications or routing changes to `internship.kicad_pcb`, automatically render the updated PCB using `kicad-cli.exe pcb render` and display the resulting image in the response so the user can visually see the live progress in KiCad.
3. **KiCad Editor Synchronization:** Remind the user that if they have the board open in the KiCad PCB Editor GUI, they can press `Ctrl + R` (or `File -> Revert to Saved`) to instantly see the live updates on their screen.
