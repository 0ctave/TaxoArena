"""ref_remint.py - the name the ARM-B-VINTAGE registration gives its instrument (docs/judge_v2_program.md, "Script:
tools/analysis/ref_remint.py"). The code lives in arm_b_vintage.py (the orchestrator's name); this alias runs it with the
same arguments so both names are one instrument. Nothing here posts."""
import os, runpy, sys
_target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arm_b_vintage.py")
sys.argv[0] = _target
runpy.run_path(_target, run_name="__main__")
