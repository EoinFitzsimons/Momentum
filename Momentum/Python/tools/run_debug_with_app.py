from PyQt6.QtWidgets import QApplication
import runpy

app = QApplication([])
# execute the debug script in __main__ context
runpy.run_path(
    r"c:\Users\eoin0\Documents\Code\Momentum\Momentum\Python\tools\debug_infield_assets.py",
    run_name="__main__",
)
