from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QDockWidget, QFormLayout, QSpinBox, 
    QLabel, QToolBar, QFileDialog, QInputDialog, QStatusBar, QMenu, 
    QLineEdit, QCheckBox, QPushButton, QComboBox, QColorDialog
)
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtCore import Qt
from canvas_widget import CanvasWidget
from draggable_widget import DraggableWidget
from utils import save_json, load_json, load_ui, generate_code

class GUIEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced GUI Editor")
        self.setGeometry(100, 100, 800, 600)
        self.history = []
        self.history_index = -1
        self.grid_enabled = True
        self.grid_size = 10
        self.property_widgets = {}
        self.clipboard = None
        self.selected_widgets = []
        self.groups = []  # List of {"id": int, "widgets": [DraggableWidget]}
        self.layouts = []  # List of {"id": int, "type": str, "widgets": [DraggableWidget]}
        self.preview_mode = False
        self.themes = {
            "Dark": {"background-color": "#333", "color": "#fff", "font-size": "14px"},
            "Light": {"background-color": "#fff", "color": "#000", "font-size": "12px"}
        }

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Grid Enabled")

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        # Canvas
        self.canvas = CanvasWidget(self.central_widget)
        self.central_layout.addWidget(self.canvas)

        # Toolbar
        self.toolbar = QToolBar("Tools")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.add_button_action = QAction("Add Button", self)
        self.add_field_action = QAction("Add Field", self)
        self.add_label_action = QAction("Add Label", self)
        self.add_checkbox_action = QAction("Add CheckBox", self)
        self.add_combobox_action = QAction("Add ComboBox", self)
        self.add_textedit_action = QAction("Add TextEdit", self) # This line is new
        self.delete_action = QAction("Delete Selected", self)
        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        self.grid_toggle_action = QAction("Toggle Grid", self)
        self.save_json_action = QAction("Save JSON", self)
        self.load_json_action = QAction("Load JSON", self)
        self.load_ui_action = QAction("Load UI File", self)
        self.generate_code_action = QAction("Generate Code", self)
        self.group_action = QAction("Group Selected", self)
        self.ungroup_action = QAction("Ungroup Selected", self)
        self.apply_v_layout_action = QAction("Apply Vertical Layout", self)
        self.apply_h_layout_action = QAction("Apply Horizontal Layout", self)
        self.preview_action = QAction("Toggle Preview", self)
        self.apply_theme_action = QAction("Apply Theme", self)
        
        self.toolbar.addAction(self.add_button_action)
        self.toolbar.addAction(self.add_field_action)
        self.toolbar.addAction(self.add_label_action)
        self.toolbar.addAction(self.add_checkbox_action)
        self.toolbar.addAction(self.add_combobox_action)
        self.toolbar.addAction(self.add_textedit_action) # This line is new
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.delete_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.grid_toggle_action)
        self.toolbar.addAction(self.group_action)
        self.toolbar.addAction(self.ungroup_action)
        self.toolbar.addAction(self.apply_v_layout_action)
        self.toolbar.addAction(self.apply_h_layout_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.preview_action)
        self.toolbar.addAction(self.apply_theme_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_json_action)
        self.toolbar.addAction(self.load_json_action)
        self.toolbar.addAction(self.load_ui_action)
        self.toolbar.addAction(self.generate_code_action)

        # Connect toolbar actions
        self.add_button_action.triggered.connect(lambda: self.add_widget("button"))
        self.add_field_action.triggered.connect(lambda: self.add_widget("field"))
        self.add_label_action.triggered.connect(lambda: self.add_widget("label"))
        self.add_checkbox_action.triggered.connect(lambda: self.add_widget("checkbox"))
        self.add_combobox_action.triggered.connect(lambda: self.add_widget("combobox"))
        self.add_textedit_action.triggered.connect(lambda: self.add_widget("textedit")) # This line is new
        self.delete_action.triggered.connect(self.delete_widget)
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.grid_toggle_action.triggered.connect(self.toggle_grid)
        self.group_action.triggered.connect(self.group_widgets)
        self.ungroup_action.triggered.connect(self.ungroup_widgets)
        self.apply_v_layout_action.triggered.connect(self.apply_vertical_layout)
        self.apply_h_layout_action.triggered.connect(self.apply_horizontal_layout)
        self.preview_action.triggered.connect(self.toggle_preview)
        self.save_json_action.triggered.connect(self.save_json)
        self.load_json_action.triggered.connect(self.load_json)
        self.load_ui_action.triggered.connect(self.load_ui)
        self.generate_code_action.triggered.connect(self.generate_code)
        self.apply_theme_action.triggered.connect(self.apply_theme)

        # Widgets list
        self.widgets = []
        self.add_initial_widgets()

        # Properties dock
        self.properties_dock = QDockWidget("Properties", self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        self.properties_widget = QWidget()
        self.properties_layout = QFormLayout(self.properties_widget)
        self.properties_dock.setWidget(self.properties_widget)

        self.update_properties()

    def add_initial_widgets(self):
        self.add_widget_to_canvas("button", {"x": 50, "y": 50, "width": 100, "height": 40, "text": "Sample Button", "color": "lightblue", "font_size": 12})
        self.add_widget_to_canvas("field", {"x": 50, "y": 100, "width": 150, "height": 30, "text": "Sample Text", "color": "lightgreen", "font_size": 12})
        self.add_widget_to_canvas("label", {"x": 50, "y": 150, "width": 100, "height": 30, "text": "Sample Label", "color": "lightyellow", "font_size": 12})
        self.add_widget_to_canvas("checkbox", {"x": 50, "y": 200, "width": 100, "height": 30, "text": "Sample CheckBox", "color": "lightcoral", "font_size": 12})
        self.add_widget_to_canvas("combobox", {"x": 50, "y": 250, "width": 150, "height": 30, "text": "Option 1,Option 2", "color": "lightgray", "font_size": 12})

    def add_widget(self, widget_type):
        text, ok1 = QInputDialog.getText(self, f"New {widget_type.capitalize()}", "Enter text:")
        color = QColorDialog.getColor(title=f"Select Color for {widget_type.capitalize()}")
        color_hex = color.name() if color.isValid() else "white"
        font_size, ok2 = QInputDialog.getInt(self, f"Font Size for {widget_type.capitalize()}", "Enter font size:", 12, 8, 72)
        if ok1 or ok2 or color.isValid():
            properties = {
                "x": 100,
                "y": 100,
                # This block is updated
                "width": 150 if widget_type in ["field", "textedit"] else 100,
                "height": 80 if widget_type == "textedit" else 40,
                "text": text if ok1 else "",
                "color": color_hex,
                "font_size": font_size if ok2 else 12,
                "custom_properties": {}
            }
            widget = self.add_widget_to_canvas(widget_type, properties)
            self.select_widget(widget, clear_others=True)
            self.add_to_history({"action": "add", "widgets": [widget.get_properties()]})
            print(f"Added {widget_type} with color {color_hex}, font size {font_size}")

    def add_widget_to_canvas(self, widget_type, properties):
        widget = DraggableWidget(widget_type, self.canvas, properties.get("text", ""), properties)
        widget.grid_size = self.grid_size if self.grid_enabled else 1
        widget.preview_mode = self.preview_mode
        widget.move(properties.get("x", 100), properties.get("y", 100))
        widget.resize(properties.get("width", 100), properties.get("height", 40))
        widget.show()
        self.widgets.append(widget)
        return widget

    def delete_widget(self, widget=None):
        targets = [widget] if widget else self.selected_widgets.copy()
        if targets:
            action = {"action": "delete", "widgets": [w.get_properties() for w in targets]}
            for target in targets:
                self.widgets.remove(target)
                for group in self.groups:
                    if target in group["widgets"]:
                        group["widgets"].remove(target)
                for layout in self.layouts:
                    if target in layout["widgets"]:
                        layout["widgets"].remove(target)
                target.deleteLater()
                if target in self.selected_widgets:
                    self.selected_widgets.remove(target)
            self.groups = [g for g in self.groups if g["widgets"]]  # Remove empty groups
            self.layouts = [l for l in self.layouts if l["widgets"]]  # Remove empty layouts
            self.update_properties()
            self.add_to_history(action)
            print(f"Deleted {len(targets)} widget(s)")
            self.status_bar.showMessage(f"Deleted {len(targets)} widget(s)")

    def cut_widget(self, widget):
        if widget:
            self.clipboard = widget.get_properties()
            self.delete_widget(widget)
            print(f"Cut {widget.widget_type}")
            self.status_bar.showMessage(f"Cut {widget.widget_type}")

    def paste_widget(self):
        if self.clipboard:
            properties = self.clipboard.copy()
            properties["x"] = properties.get("x", 100) + 20
            properties["y"] = properties.get("y", 100) + 20
            widget = self.add_widget_to_canvas(properties["type"], properties)
            self.select_widget(widget, clear_others=True)
            self.add_to_history({"action": "add", "widgets": [widget.get_properties()]})
            print(f"Pasted {widget.widget_type}")
            self.status_bar.showMessage(f"Pasted {widget.widget_type}")

    def group_widgets(self):
        if len(self.selected_widgets) > 1:
            group_id = len(self.groups) + 1
            group = {"id": group_id, "widgets": self.selected_widgets.copy()}
            self.groups.append(group)
            for widget in self.selected_widgets:
                widget.properties["group_id"] = group_id
            self.add_to_history({"action": "group", "group": group})
            self.status_bar.showMessage(f"Grouped {len(self.selected_widgets)} widgets")
            print(f"Grouped {len(self.selected_widgets)} widgets")

    def ungroup_widgets(self):
        if self.selected_widgets:
            group_ids = set(widget.properties.get("group_id") for widget in self.selected_widgets if "group_id" in widget.properties)
            for group_id in group_ids:
                group = next((g for g in self.groups if g["id"] == group_id), None)
                if group:
                    self.groups.remove(group)
                    for widget in group["widgets"]:
                        widget.properties.pop("group_id", None)
                    self.add_to_history({"action": "ungroup", "group_id": group_id})
            self.status_bar.showMessage(f"Ungrouped widgets")
            print(f"Ungrouped widgets")

    def apply_vertical_layout(self):
        if len(self.selected_widgets) > 1:
            layout_id = len(self.layouts) + 1
            container = DraggableWidget("container", self.canvas, properties={"layout": "vertical", "layout_id": layout_id})
            container.resize(200, 50 * len(self.selected_widgets))
            self.widgets.append(container)
            for widget in self.selected_widgets:
                widget.properties["layout_id"] = layout_id
                widget.setParent(container)
            self.layouts.append({"id": layout_id, "type": "vertical", "widgets": self.selected_widgets.copy()})
            self.add_to_history({"action": "layout", "layout": self.layouts[-1]})
            self.status_bar.showMessage("Applied vertical layout")
            print("Applied vertical layout")

    def apply_horizontal_layout(self):
        if len(self.selected_widgets) > 1:
            layout_id = len(self.layouts) + 1
            container = DraggableWidget("container", self.canvas, properties={"layout": "horizontal", "layout_id": layout_id})
            container.resize(50 * len(self.selected_widgets), 200)
            self.widgets.append(container)
            for widget in self.selected_widgets:
                widget.properties["layout_id"] = layout_id
                widget.setParent(container)
            self.layouts.append({"id": layout_id, "type": "horizontal", "widgets": self.selected_widgets.copy()})
            self.add_to_history({"action": "layout", "layout": self.layouts[-1]})
            self.status_bar.showMessage("Applied horizontal layout")
            print("Applied horizontal layout")

    def toggle_preview(self):
        self.preview_mode = not self.preview_mode
        for widget in self.widgets:
            widget.preview_mode = self.preview_mode
            widget.widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not self.preview_mode)
            widget.widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus if self.preview_mode else Qt.FocusPolicy.NoFocus)
            widget.setMouseTracking(not self.preview_mode)
        self.toolbar.setEnabled(not self.preview_mode)
        self.properties_dock.setEnabled(not self.preview_mode)
        self.status_bar.showMessage("Preview Mode" if self.preview_mode else "Edit Mode")
        print(f"Toggled to {'Preview' if self.preview_mode else 'Edit'} Mode")

    def apply_theme(self):
        theme, ok = QInputDialog.getItem(self, "Select Theme", "Choose a theme:", self.themes.keys(), 0, False)
        if ok:
            for widget in self.selected_widgets or self.widgets:
                widget.properties.update(self.themes[theme])
                self.update_widget_stylesheet(widget, widget in self.selected_widgets)
            self.add_to_history({"action": "modify", "widgets": [w.get_properties() for w in self.selected_widgets or self.widgets]})
            self.status_bar.showMessage(f"Applied {theme} theme")
            print(f"Applied {theme} theme")

    def update_widget_stylesheet(self, widget, is_selected):
        color = widget.properties.get("color", "")
        font_size = widget.properties.get("font_size", 12)
        style = f"background-color: {color}; font-size: {font_size}px;" if color else f"font-size: {font_size}px;"
        if is_selected:
            style += " border: 2px solid blue;"
        widget.widget.setStyleSheet(style)
        widget.setStyleSheet("")
        print(f"Updated stylesheet for {widget.widget_type}, selected: {is_selected}, style: {style}")

    def edit_widget(self, widget):
        if widget:
            text, ok1 = QInputDialog.getText(self, f"Edit {widget.widget_type.capitalize()}", "Enter text:", text=widget.widget.text() if widget.widget_type != "combobox" else ",".join([widget.widget.itemText(i) for i in range(widget.widget.count())]))
            name, ok2 = QInputDialog.getText(self, f"Edit {widget.widget_type.capitalize()}", "Enter name:", text=widget.properties.get("name", ""))
            color = QColorDialog.getColor(title=f"Select Color for {widget.widget_type.capitalize()}")
            color_hex = color.name() if color.isValid() else widget.properties.get("color", "")
            font_size, ok3 = QInputDialog.getInt(self, f"Edit Font Size for {widget.widget_type.capitalize()}", "Enter font size:", widget.properties.get("font_size", 12), 8, 72)
            if ok1 or ok2 or ok3 or color.isValid():
                if ok1:
                    self.update_widget_property(widget, "text", text)
                if ok2:
                    self.update_widget_property(widget, "name", name)
                if ok3:
                    self.update_widget_property(widget, "font_size", font_size)
                if color.isValid():
                    self.update_widget_property(widget, "color", color_hex)
                self.update_widget_stylesheet(widget, widget in self.selected_widgets)
                print(f"Edited {widget.widget_type}, selected: {widget in self.selected_widgets}")
                self.status_bar.showMessage(f"Edited {widget.widget_type}")

    def edit_custom_properties(self, widget):
        key, ok1 = QInputDialog.getText(self, "Custom Property", "Enter property name:")
        value, ok2 = QInputDialog.getText(self, "Custom Property", "Enter property value:")
        if ok1 and ok2:
            widget.custom_properties[key] = value
            self.add_to_history({"action": "modify", "widgets": [widget.get_properties()]})
            self.status_bar.showMessage(f"Added custom property {key}: {value}")
            print(f"Added custom property {key}: {value}")

    def show_widget_context_menu(self, widget, global_pos):
        menu = QMenu(self)
        cut_action = QAction("Cut", self)
        paste_action = QAction("Paste", self)
        delete_action = QAction("Delete", self)
        edit_action = QAction("Edit", self)
        bring_to_front_action = QAction("Bring to Front", self)
        send_to_back_action = QAction("Send to Back", self)
        custom_props_action = QAction("Edit Custom Properties", self)

        cut_action.triggered.connect(lambda: self.cut_widget(widget))
        paste_action.triggered.connect(self.paste_widget)
        delete_action.triggered.connect(lambda: self.delete_widget(widget))
        edit_action.triggered.connect(lambda: self.edit_widget(widget))
        bring_to_front_action.triggered.connect(lambda: self.bring_to_front(widget))
        send_to_back_action.triggered.connect(lambda: self.send_to_back(widget))
        custom_props_action.triggered.connect(lambda: self.edit_custom_properties(widget))

        menu.addAction(cut_action)
        menu.addAction(paste_action)
        menu.addAction(delete_action)
        menu.addAction(edit_action)
        menu.addAction(custom_props_action)
        menu.addAction(bring_to_front_action)
        menu.addAction(send_to_back_action)
        menu.exec(global_pos)

    def save_json(self):
        save_json(self.widgets, self.groups, self.layouts, self)

    def load_json(self):
        data = load_json(self)
        if data:
            self.clear_canvas()
            for item in data["widgets"]:
                self.add_widget_to_canvas(item["type"], item)
            self.groups = data.get("groups", [])
            self.layouts = data.get("layouts", [])
            self.add_to_history({"action": "load_json", "data": data})
            self.status_bar.showMessage("Loaded JSON layout")
            print("Loaded JSON layout")

    def load_ui(self):
        ui_data = load_ui(self)
        if ui_data:
            self.clear_canvas()
            for widget_type, properties in ui_data:
                self.add_widget_to_canvas(widget_type, properties)
            self.add_to_history({"action": "load_ui", "layout": ui_data})

    def generate_code(self):
        generate_code(self.widgets, self.layouts, self)

    def clear_canvas(self):
        for widget in self.widgets[:]:
            self.delete_widget(widget)
        self.groups.clear()
        self.layouts.clear()

    def select_widget(self, widget, event=None, clear_others=True):
        if self.preview_mode:
            return
        if clear_others:
            for w in self.selected_widgets:
                self.update_widget_stylesheet(w, False)
            self.selected_widgets.clear()
        if widget and widget not in self.selected_widgets:
            self.selected_widgets.append(widget)
            self.update_widget_stylesheet(widget, True)
        self.update_properties()
        print(f"Selected {len(self.selected_widgets)} widget(s)")

    def handle_widget_selection(self, widget, event):
        if self.preview_mode:
            return
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:  # Fixed attribute
            if widget in self.selected_widgets:
                self.selected_widgets.remove(widget)
                self.update_widget_stylesheet(widget, False)
            else:
                self.selected_widgets.append(widget)
                self.update_widget_stylesheet(widget, True)
        else:
            self.select_widget(widget)
        print(f"Handled selection, {len(self.selected_widgets)} widgets selected")

    def calculate_alignment_guides(self, widget, x, y, width, height, is_resizing=False):
        guides = []
        snap_x, snap_y = x, y
        snap_width, snap_height = width, height
        threshold = 5
        for other in self.widgets:
            if other != widget and "layout_id" not in other.properties:
                # Horizontal alignment
                if abs(other.y() - y) < threshold:
                    guides.append((0, other.y(), self.canvas.width(), other.y()))
                    snap_y = other.y()
                if abs(other.y() + other.height() - y) < threshold:
                    guides.append((0, other.y() + other.height(), self.canvas.width(), other.y() + other.height()))
                    snap_y = other.y() + other.height()
                # Vertical alignment
                if abs(other.x() - x) < threshold:
                    guides.append((other.x(), 0, other.x(), self.canvas.height()))
                    snap_x = other.x()
                if abs(other.x() + other.width() - x) < threshold:
                    guides.append((other.x() + other.width(), 0, other.x() + other.width(), self.canvas.height()))
                    snap_x = other.x() + other.width()
                # Center alignment
                if abs(other.x() + other.width() / 2 - x - width / 2) < threshold:
                    center_x = other.x() + other.width() / 2
                    guides.append((center_x, 0, center_x, self.canvas.height()))
                    snap_x = center_x - width / 2
                if abs(other.y() + other.height() / 2 - y - height / 2) < threshold:
                    center_y = other.y() + other.height() / 2
                    guides.append((0, center_y, self.canvas.width(), center_y))
                    snap_y = center_y - height / 2
                if is_resizing:
                    if abs(other.x() + other.width() - x - width) < threshold:
                        guides.append((other.x() + other.width(), 0, other.x() + other.width(), self.canvas.height()))
                        snap_width = other.x() + other.width() - x
                    if abs(other.y() + other.height() - y - height) < threshold:
                        guides.append((0, other.y() + other.height(), self.canvas.width(), other.y() + other.height()))
                        snap_height = other.y() + other.height() - y
        return guides, snap_x, snap_y, snap_width, snap_height

    def bring_to_front(self, widget):
        widget.raise_()
        self.add_to_history({"action": "modify", "widgets": [widget.get_properties()]})
        print(f"Brought {widget.widget_type} to front")
        self.status_bar.showMessage(f"Brought {widget.widget_type} to front")

    def send_to_back(self, widget):
        widget.lower()
        self.add_to_history({"action": "modify", "widgets": [widget.get_properties()]})
        print(f"Sent {widget.widget_type} to back")
        self.status_bar.showMessage(f"Sent {widget.widget_type} to back")

    def add_to_history(self, action):
        self.history = self.history[:self.history_index + 1]
        self.history.append(action)
        self.history_index += 1
        print(f"History updated: {action['action']}")

    def undo(self):
        if self.history_index >= 0:
            action = self.history[self.history_index]
            self.history_index -= 1
            if action["action"] == "add":
                for props in action["widgets"]:
                    for widget in self.widgets[:]:
                        if widget.get_properties() == props:
                            self.delete_widget(widget)
            elif action["action"] == "delete":
                for props in action["widgets"]:
                    self.add_widget_to_canvas(props["type"], props)
            elif action["action"] == "modify":
                for widget in self.widgets:
                    for props in action["widgets"]:
                        if widget.get_properties()["name"] == props["name"]:
                            self.restore_widget_properties(widget, props)
            elif action["action"] == "group":
                group_id = action["group"]["id"]
                self.groups = [g for g in self.groups if g["id"] != group_id]
                for widget in action["group"]["widgets"]:
                    widget.properties.pop("group_id", None)
            elif action["action"] == "ungroup":
                self.groups.append({"id": action["group_id"], "widgets": [w for w in self.widgets if w.properties.get("group_id") == action["group_id"]]})
                for widget in self.widgets:
                    if widget.properties.get("group_id") == action["group_id"]:
                        widget.properties["group_id"] = action["group_id"]
            elif action["action"] == "layout":
                layout_id = action["layout"]["id"]
                self.layouts = [l for l in self.layouts if l["id"] != layout_id]
                for widget in self.widgets:
                    if widget.properties.get("layout_id") == layout_id:
                        widget.setParent(self.canvas)
                        widget.properties.pop("layout_id", None)
            elif action["action"] == "load_json":
                self.clear_canvas()
                for item in action["data"].get("widgets", []):
                    self.add_widget_to_canvas(item["type"], item)
                self.groups = action["data"].get("groups", [])
                self.layouts = action["data"].get("layouts", [])
            self.update_properties()
            self.status_bar.showMessage(f"Undo {action['action']}")
            print(f"Undo {action['action']}")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            action = self.history[self.history_index]
            if action["action"] == "add":
                for props in action["widgets"]:
                    self.add_widget_to_canvas(props["type"], props)
            elif action["action"] == "delete":
                for props in action["widgets"]:
                    for widget in self.widgets[:]:
                        if widget.get_properties() == props:
                            self.delete_widget(widget)
            elif action["action"] == "modify":
                for widget in self.widgets:
                    for props in action["widgets"]:
                        if widget.get_properties()["name"] == props["name"]:
                            self.restore_widget_properties(widget, props)
            elif action["action"] == "group":
                self.groups.append(action["group"])
                for widget in action["group"]["widgets"]:
                    widget.properties["group_id"] = action["group"]["id"]
            elif action["action"] == "ungroup":
                group_id = action["group_id"]
                self.groups = [g for g in self.groups if g["id"] != group_id]
                for widget in self.widgets:
                    if widget.properties.get("group_id") == group_id:
                        widget.properties.pop("group_id", None)
            elif action["action"] == "layout":
                self.apply_layout(action["layout"])
            self.update_properties()
            self.status_bar.showMessage(f"Redo {action['action']}")
            print(f"Redo {action['action']}")

    def restore_widget_properties(self, widget, props):
        widget.move(props["x"], props["y"])
        widget.resize(props["width"], props["height"])
        widget.properties.update({"color": props["color"], "font_size": props["font_size"], "name": props["name"], "custom_properties": props.get("custom_properties", {})})
        self.update_widget_property(widget, "text", props["text"])
        self.update_widget_stylesheet(widget, widget in self.selected_widgets)

    def apply_layout(self, layout):
        container = DraggableWidget("container", self.canvas, properties={"layout": layout["type"], "layout_id": layout["id"]})
        container.resize(200 if layout["type"] == "vertical" else 50 * len(layout["widgets"]), 50 * len(layout["widgets"]) if layout["type"] == "vertical" else 200)
        self.widgets.append(container)
        for widget in layout["widgets"]:
            widget.properties["layout_id"] = layout["id"]
            widget.setParent(container)
        self.layouts.append(layout)

    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.canvas.update_grid(self.grid_enabled, self.grid_size)
        for widget in self.widgets:
            widget.grid_size = self.grid_size if self.grid_enabled else 1
        self.update_properties()
        self.status_bar.showMessage(f"Grid {'Enabled' if self.grid_enabled else 'Disabled'}")
        print(f"Grid {'enabled' if self.grid_enabled else 'disabled'}")

    def update_grid_size(self, size):
        self.grid_size = size
        self.canvas.update_grid(self.grid_enabled, self.grid_size)
        for widget in self.widgets:
            widget.grid_size = self.grid_size if self.grid_enabled else 1
        self.status_bar.showMessage(f"Grid size set to {size}")
        print(f"Grid size set to {size}")

    def update_properties(self):
        for i in reversed(range(self.properties_layout.count())):
            self.properties_layout.itemAt(i).widget().deleteLater()
        self.property_widgets.clear()
        if self.preview_mode:
            self.properties_layout.addRow(QLabel("Properties disabled in Preview Mode"))
            return
        if len(self.selected_widgets) == 1:
            widget = self.selected_widgets[0]
            x_spin = QSpinBox()
            x_spin.setRange(-1000, 1000)
            x_spin.setValue(widget.x())
            x_spin.valueChanged.connect(lambda value: self.update_widget_property(widget, "x", value))
            self.properties_layout.addRow("X Position:", x_spin)
            self.property_widgets["x_spin"] = x_spin

            y_spin = QSpinBox()
            y_spin.setRange(-1000, 1000)
            y_spin.setValue(widget.y())
            y_spin.valueChanged.connect(lambda value: self.update_widget_property(widget, "y", value))
            self.properties_layout.addRow("Y Position:", y_spin)
            self.property_widgets["y_spin"] = y_spin

            width_spin = QSpinBox()
            width_spin.setRange(50, 1000)
            width_spin.setValue(widget.width())
            width_spin.valueChanged.connect(lambda value: self.update_widget_property(widget, "width", value))
            self.properties_layout.addRow("Width:", width_spin)
            self.property_widgets["width_spin"] = width_spin

            height_spin = QSpinBox()
            height_spin.setRange(30, 1000)
            height_spin.setValue(widget.height())
            height_spin.valueChanged.connect(lambda value: self.update_widget_property(widget, "height", value))
            self.properties_layout.addRow("Height:", height_spin)
            self.property_widgets["height_spin"] = height_spin

            type_label = QLabel(widget.widget_type.capitalize())
            self.properties_layout.addRow("Type:", type_label)
            self.property_widgets["type_label"] = type_label

            text_input = QLineEdit(widget.widget.text() if widget.widget_type != "combobox" else ",".join([widget.widget.itemText(i) for i in range(widget.widget.count())]))
            text_input.textChanged.connect(lambda text: self.update_widget_property(widget, "text", text))
            self.properties_layout.addRow("Text:", text_input)
            self.property_widgets["text_input"] = text_input

            name_input = QLineEdit(widget.properties.get("name", ""))
            name_input.textChanged.connect(lambda text: self.update_widget_property(widget, "name", text))
            self.properties_layout.addRow("Name:", name_input)
            self.property_widgets["name_input"] = name_input

            font_size_spin = QSpinBox()
            font_size_spin.setRange(8, 72)
            font_size_spin.setValue(widget.properties.get("font_size", 12))
            font_size_spin.valueChanged.connect(lambda value: self.update_widget_property(widget, "font_size", value))
            self.properties_layout.addRow("Font Size:", font_size_spin)
            self.property_widgets["font_size_spin"] = font_size_spin

            color_button = QPushButton("Select Color")
            color_button.clicked.connect(lambda: self.select_color_for_widget(widget))
            self.properties_layout.addRow("Background Color:", color_button)
            self.property_widgets["color_button"] = color_button

            custom_props_button = QPushButton("Edit Custom Properties")
            custom_props_button.clicked.connect(lambda: self.edit_custom_properties(widget))
            self.properties_layout.addRow("Custom Properties:", custom_props_button)
            self.property_widgets["custom_props_button"] = custom_props_button
        elif self.selected_widgets:
            common_x = self.selected_widgets[0].x() if all(w.x() == self.selected_widgets[0].x() for w in self.selected_widgets) else None
            x_spin = QSpinBox()
            x_spin.setRange(-1000, 1000)
            if common_x is not None:
                x_spin.setValue(common_x)
            else:
                x_spin.setEnabled(False)
                x_spin.setPlaceholderText("Multiple values")
            x_spin.valueChanged.connect(lambda value: self.update_multiple_widgets_property("x", value))
            self.properties_layout.addRow("X Position:", x_spin)
            self.property_widgets["x_spin"] = x_spin

            common_y = self.selected_widgets[0].y() if all(w.y() == self.selected_widgets[0].y() for w in self.selected_widgets) else None
            y_spin = QSpinBox()
            y_spin.setRange(-1000, 1000)
            if common_y is not None:
                y_spin.setValue(common_y)
            else:
                y_spin.setEnabled(False)
                y_spin.setPlaceholderText("Multiple values")
            y_spin.valueChanged.connect(lambda value: self.update_multiple_widgets_property("y", value))
            self.properties_layout.addRow("Y Position:", y_spin)
            self.property_widgets["y_spin"] = y_spin

            common_width = self.selected_widgets[0].width() if all(w.width() == self.selected_widgets[0].width() for w in self.selected_widgets) else None
            width_spin = QSpinBox()
            width_spin.setRange(50, 1000)
            if common_width is not None:
                width_spin.setValue(common_width)
            else:
                width_spin.setEnabled(False)
                width_spin.setPlaceholderText("Multiple values")
            width_spin.valueChanged.connect(lambda value: self.update_multiple_widgets_property("width", value))
            self.properties_layout.addRow("Width:", width_spin)
            self.property_widgets["width_spin"] = width_spin

            common_height = self.selected_widgets[0].height() if all(w.height() == self.selected_widgets[0].height() for w in self.selected_widgets) else None
            height_spin = QSpinBox()
            height_spin.setRange(30, 1000)
            if common_height is not None:
                height_spin.setValue(common_height)
            else:
                height_spin.setEnabled(False)
                height_spin.setPlaceholderText("Multiple values")
            height_spin.valueChanged.connect(lambda value: self.update_multiple_widgets_property("height", value))
            self.properties_layout.addRow("Height:", height_spin)
            self.property_widgets["height_spin"] = height_spin

            common_font_size = self.selected_widgets[0].properties.get("font_size", 12) if all(w.properties.get("font_size", 12) == self.selected_widgets[0].properties.get("font_size", 12) for w in self.selected_widgets) else None
            font_size_spin = QSpinBox()
            font_size_spin.setRange(8, 72)
            if common_font_size is not None:
                font_size_spin.setValue(common_font_size)
            else:
                font_size_spin.setEnabled(False)
                font_size_spin.setPlaceholderText("Multiple values")
            font_size_spin.valueChanged.connect(lambda value: self.update_multiple_widgets_property("font_size", value))
            self.properties_layout.addRow("Font Size:", font_size_spin)
            self.property_widgets["font_size_spin"] = font_size_spin

            common_color = self.selected_widgets[0].properties.get("color", "") if all(w.properties.get("color", "") == self.selected_widgets[0].properties.get("color", "") for w in self.selected_widgets) else None
            color_button = QPushButton("Select Color")
            if common_color is None:
                color_button.setEnabled(False)
                color_button.setText("Multiple colors")
            color_button.clicked.connect(self.select_color_for_multiple_widgets)
            self.properties_layout.addRow("Background Color:", color_button)
            self.property_widgets["color_button"] = color_button
        else:
            grid_size_spin = QSpinBox()
            grid_size_spin.setRange(1, 50)
            grid_size_spin.setValue(self.grid_size)
            grid_size_spin.valueChanged.connect(self.update_grid_size)
            self.properties_layout.addRow("Grid Size:", grid_size_spin)
            self.property_widgets["grid_size_spin"] = grid_size_spin

            grid_enabled_check = QCheckBox("Grid Enabled")
            grid_enabled_check.setChecked(self.grid_enabled)
            grid_enabled_check.stateChanged.connect(self.toggle_grid)
            self.properties_layout.addRow(grid_enabled_check)
            self.property_widgets["grid_enabled_check"] = grid_enabled_check

    def select_color_for_widget(self, widget):
        color = QColorDialog.getColor(title=f"Select Color for {widget.widget_type.capitalize()}")
        if color.isValid():
            self.update_widget_property(widget, "color", color.name())
            print(f"Color selected for {widget.widget_type}: {color.name()}")

    def select_color_for_multiple_widgets(self):
        color = QColorDialog.getColor(title="Select Color for Selected Widgets")
        if color.isValid():
            self.update_multiple_widgets_property("color", color.name())
            print(f"Color selected for {len(self.selected_widgets)} widgets: {color.name()}")

    def update_widget_property(self, widget, property_name, value):
        if widget and widget in self.widgets:
            print(f"Updating {widget.widget_type} {property_name} to {value}, selected: {widget in self.selected_widgets}")
            if property_name == "x":
                widget.move(value, widget.y())
                print(f"Updated {widget.widget_type} x to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} X position to {value}")
            elif property_name == "y":
                widget.move(widget.x(), value)
                print(f"Updated {widget.widget_type} y to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} Y position to {value}")
            elif property_name == "width":
                widget.resize(value, widget.height())
                widget.widget.resize(value, widget.height())
                print(f"Updated {widget.widget_type} width to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} width to {value}")
            elif property_name == "height":
                widget.resize(widget.width(), value)
                widget.widget.resize(widget.width(), value)
                print(f"Updated {widget.widget_type} height to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} height to {value}")
            elif property_name == "text":
                if widget.widget_type != "combobox":
                    widget.widget.setText(value)
                else:
                    widget.widget.clear()
                    widget.widget.addItems(value.split(",") if value else ["Option 1"])
                print(f"Updated {widget.widget_type} text to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} text")
            elif property_name == "name":
                widget.properties["name"] = value
                print(f"Updated {widget.widget_type} name to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} name to {value}")
            elif property_name == "color":
                widget.properties["color"] = value
                self.update_widget_stylesheet(widget, widget in self.selected_widgets)
                print(f"Updated {widget.widget_type} color to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} color to {value}")
            elif property_name == "font_size":
                widget.properties["font_size"] = value
                self.update_widget_stylesheet(widget, widget in self.selected_widgets)
                print(f"Updated {widget.widget_type} font size to {value}")
                self.status_bar.showMessage(f"Updated {widget.widget_type} font size to {value}")
            self.add_to_history({"action": "modify", "widgets": [widget.get_properties()]})

    def update_multiple_widgets_property(self, property_name, value):
        for widget in self.selected_widgets:
            self.update_widget_property(widget, property_name, value)
        self.update_properties()