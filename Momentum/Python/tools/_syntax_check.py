import ast
import sys

p = r"c:\Users\eoin0\Documents\Code\FinalProject\FinalProject\Momentum\Python\GUI\gui_race_visual.py"
try:
    s = open(p, "r", encoding="utf-8").read()
    ast.parse(s)
    print("OK")
except Exception as e:
    import traceback

    traceback.print_exc()
    print("ERR", e)
    sys.exit(1)
