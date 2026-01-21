# Advanced GUI Editor

⚠️ **LICENSE & USAGE NOTICE — READ FIRST**

This repository is **source-available for private technical evaluation and testing only**.

- ❌ No commercial use  
- ❌ No production use  
- ❌ No academic, institutional, or government use  
- ❌ No research, benchmarking, or publication  
- ❌ No redistribution, sublicensing, or derivative works  
- ❌ No independent development based on this code  

All rights remain exclusively with the author.  
Use of this software constitutes acceptance of the terms defined in **LICENSE.txt**.

---

### Key Features

- Interactive Design Canvas: Create UIs by dragging and dropping widgets onto a canvas with a customizable grid.
- Dynamic Widget Management: Add, resize, and move various widgets including Buttons, Fields, Labels, CheckBoxes, ComboBoxes, and TextEdits.

- Alignment & Snapping: Precise positioning with real-time alignment guides and grid snapping (1px to 50px).

- Layout & Grouping: Group multiple widgets together or apply Vertical/Horizontal layouts to containers.

- Code Generation: Export your visual design directly to a standalone Python script using PyQt6.

- File Interoperability:
  
  - Save and load layouts in a custom JSON format.
  - Import existing layouts from Qt .ui files.

- Advanced Editing Tools:

  - Full Undo/Redo history for all actions.
  - Preview Mode to test the UI's look and feel without editing.
  - Context Menu for quick access to Cut, Paste, and Z-order (Bring to Front/Send to Back).
  - Theme Support: Switch between Dark and Light themes for the generated widgets.

---

## Installation

**Prerequisites**
- Python 3.x
- PyQt6

Setup
Clone this repository:

```Bash
git clone https://github.com/yourusername/advanced-gui-editor.git
cd advanced-gui-editor
```
Install dependencies:

```Bash
pip install PyQt6
```

---

### Usage

To start the editor, run the main.py file:
```Bash
python main.py
```
**Quick Start**
1. Add Widgets: Use the toolbar at the top to add new elements to the canvas.
2. Edit Properties: Select a widget to modify its position, size, text, color, and font size in the Properties Dock on the right.
3. Align: Drag widgets near each other to see red alignment guides.
4. Export: Once satisfied, click Generate Code to save your UI as a Python file.

---

### Project Structure

- main.py: The entry point of the application.
- gui_editor.py: Contains the GUIEditor class, managing the main window, toolbars, and editor logic.
- draggable_widget.py: Implements the DraggableWidget class, handling the mouse events and properties of individual UI elements.
- canvas_widget.py: Handles the drawing of the grid and alignment guides.
- utils.py: Contains utility functions for JSON serialization, UI file parsing, and Python code generation.

---

### Contribution Policy

Feedback, bug reports, and suggestions are welcome.

You may submit:

- Issues
- Design feedback
- Pull requests for review

However:

- Contributions do not grant any license or ownership rights
- The author retains full discretion over acceptance and future use
- Contributors receive no rights to reuse, redistribute, or derive from this code

---

### License
This project is not open-source.

It is licensed under a private evaluation-only license.
See LICENSE.txt for full terms.
