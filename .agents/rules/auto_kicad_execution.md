---
trigger: always_on
---

# Autonomous KiCad & Python Script Execution Rule

1. Always execute KiCad CLI commands (`kicad-cli.exe`) and KiCad Python scripts (`C:\Program Files\KiCad\10.0\bin\python.exe`) proactively without prompting or pausing for user permission.
2. The user has explicitly granted full permission to run all KiCad PCB generation, DRC verification, 3D rendering, and netlist processing commands in this workspace.
3. Automatically execute all board layout modifications, verification scripts, and DRC reports directly using `run_command`.
