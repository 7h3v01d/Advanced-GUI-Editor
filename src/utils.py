import json
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QFileDialog

def save_json(widgets, groups, layouts, parent):
    file_name, _ = QFileDialog.getSaveFileName(parent, "Save JSON", "", "JSON Files (*.json)")
    if file_name:
        data = {
            "widgets": [widget.get_properties() for widget in widgets],
            "groups": groups,
            "layouts": layouts
        }
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved JSON to {file_name}")
        parent.status_bar.showMessage(f"Saved JSON to {file_name}")

def load_json(parent):
    file_name, _ = QFileDialog.getOpenFileName(parent, "Load JSON", "", "JSON Files (*.json)")
    if file_name:
        with open(file_name, 'r') as f:
            data = json.load(f)
        print(f"Loaded JSON from {file_name}")
        parent.status_bar.showMessage(f"Loaded JSON from {file_name}")
        return data
    return None

def load_ui(parent):
    file_name, _ = QFileDialog.getOpenFileName(parent, "Load UI File", "", "UI Files (*.ui)")
    if file_name:
        tree = ET.parse(file_name)
        root = tree.getroot()
        ui_data = []
        for widget in root.findall(".//widget"):
            widget_type = widget.get("class").lower().replace("q", "")
            properties = {
                "name": widget.get("name", ""),
                "x": int(widget.find("geometry/x").text) if widget.find("geometry/x") is not None else 100,
                "y": int(widget.find("geometry/y").text) if widget.find("geometry/y") is not None else 100,
                "width": int(widget.find("geometry/width").text) if widget.find("geometry/width") is not None else 100,
                "height": int(widget.find("geometry/height").text) if widget.find("geometry/height") is not None else 40,
                "text": widget.find("property/text").text if widget.find("property/text") is not None else "",
                "color": widget.find("property/stylesheet").text.split("background-color: ")[1].split(";")[0] if widget.find("property/stylesheet") is not None and "background-color" in widget.find("property/stylesheet").text else "white",
                "font_size": int(widget.find("property/font/size").text) if widget.find("property/font/size") is not None else 12,
                "custom_properties": {}
            }
            ui_data.append((widget_type, properties))
        print(f"Loaded UI from {file_name}")
        parent.status_bar.showMessage(f"Loaded UI from {file_name}")
        return ui_data
    return None

def generate_code(widgets, layouts, parent):
    file_name, _ = QFileDialog.getSaveFileName(parent, "Save Generated Code", "", "Python Files (*.py)")
    if file_name:
        code = [
            "from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox",
            "from PyQt6.QtCore import Qt",
            "",
            "class GeneratedUI(QMainWindow):",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.setWindowTitle('Generated UI')",
            "        self.setGeometry(100, 100, 800, 600)",
            "        central_widget = QWidget()",
            "        self.setCentralWidget(central_widget)",
            "        layout = QVBoxLayout(central_widget)",
            ""
        ]
        # Handle layouts first
        for layout in layouts:
            layout_id = layout["id"]
            layout_type = layout["type"].capitalize()
            code.append(f"        layout_{layout_id} = Q{layout_type}Layout()")
            for widget in layout["widgets"]:
                props = widget.get_properties()
                name = props.get("name", f"{props['type']}_{id(widget)}")
                if props["type"] == "button":
                    code.append(f"        {name} = QPushButton('{props['text']}', central_widget)")
                elif props["type"] == "field":
                    code.append(f"        {name} = QLineEdit(central_widget)")
                    if props["text"]:
                        code.append(f"        {name}.setText('{props['text']}')")
                elif props["type"] == "label":
                    code.append(f"        {name} = QLabel('{props['text']}', central_widget)")
                elif props["type"] == "checkbox":
                    code.append(f"        {name} = QCheckBox('{props['text']}', central_widget)")
                elif props["type"] == "combobox":
                    code.append(f"        {name} = QComboBox(central_widget)")
                    if props["text"]:
                        items = props["text"].split(",")
                        for item in items:
                            code.append(f"        {name}.addItem('{item}')")
                color = props.get("color", "white")
                font_size = props.get("font_size", 12)
                code.append(f"        {name}.setStyleSheet('background-color: {color}; font-size: {font_size}px;')")
                # Add custom properties as comments
                for key, value in props.get("custom_properties", {}).items():
                    code.append(f"        # Custom property: {key} = {value}")
                code.append(f"        layout_{layout_id}.addWidget({name})")
            code.append(f"        container_{layout_id} = QWidget(central_widget)")
            code.append(f"        container_{layout_id}.setLayout(layout_{layout_id})")
            code.append(f"        layout.addWidget(container_{layout_id})")
        # Handle non-layout widgets
        for widget in widgets:
            if "layout_id" not in widget.get_properties():
                props = widget.get_properties()
                name = props.get("name", f"{props['type']}_{id(widget)}")
                x, y, width, height = props["x"], props["y"], props["width"], props["height"]
                text = props["text"]
                color = props.get("color", "white")
                font_size = props.get("font_size", 12)
                if props["type"] == "button":
                    code.append(f"        {name} = QPushButton('{text}', central_widget)")
                elif props["type"] == "field":
                    code.append(f"        {name} = QLineEdit(central_widget)")
                    if text:
                        code.append(f"        {name}.setText('{text}')")
                elif props["type"] == "label":
                    code.append(f"        {name} = QLabel('{text}', central_widget)")
                elif props["type"] == "checkbox":
                    code.append(f"        {name} = QCheckBox('{text}', central_widget)")
                elif props["type"] == "combobox":
                    code.append(f"        {name} = QComboBox(central_widget)")
                    if text:
                        items = text.split(",")
                        for item in items:
                            code.append(f"        {name}.addItem('{item}')")
                code.append(f"        {name}.setGeometry({x}, {y}, {width}, {height})")
                code.append(f"        {name}.setStyleSheet('background-color: {color}; font-size: {font_size}px;')")
                for key, value in props.get("custom_properties", {}).items():
                    code.append(f"        # Custom property: {key} = {value}")
        code.append("")
        code.append("if __name__ == '__main__':")
        code.append("    app = QApplication([])")
        code.append("    window = GeneratedUI()")
        code.append("    window.show()")
        code.append("    app.exec()")
        with open(file_name, 'w') as f:
            f.write("\n".join(code))
        print(f"Generated code saved to {file_name}")
        parent.status_bar.showMessage(f"Generated code saved to {file_name}")