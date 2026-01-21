from PyQt6.QtWidgets import QApplication
import sys
from gui_editor import GUIEditor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = GUIEditor()
    editor.show()
    sys.exit(app.exec())