from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel, QCheckBox, QComboBox, QApplication, QTextEdit
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QCursor

class DraggableWidget(QWidget):
    def __init__(self, widget_type="button", parent=None, text="", properties=None):
        super().__init__(parent)
        self.widget_type = widget_type
        self.is_dragging = False
        self.is_resizing = False
        self.grid_size = 10
        self.properties = properties or {}
        self.custom_properties = self.properties.get("custom_properties", {})
        self.preview_mode = False

        # --- Attributes for global coordinate dragging ---
        self.drag_start_global_pos = None
        self.drag_start_widget_pos = None
        self.drag_start_size = None
        self.last_move_global_pos = None
        # --- End of New Attributes ---

        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.is_processing_move = False

        if widget_type == "button":
            self.widget = QPushButton(text or "Button", self)
        elif widget_type == "field":
            self.widget = QLineEdit(self)
            self.widget.setPlaceholderText("Text Field")
            if text:
                self.widget.setText(text)
        elif widget_type == "textedit":
            self.widget = QTextEdit(self)
            self.widget.setPlaceholderText("Multi-line text...")
            if text:
                self.widget.setText(text)
        elif widget_type == "label":
            self.widget = QLabel(text or "Label", self)
        elif widget_type == "checkbox":
            self.widget = QCheckBox(text or "CheckBox", self)
        elif widget_type == "combobox":
            self.widget = QComboBox(self)
            self.widget.addItems(["Option 1", "Option 2"] if not text else text.split(","))
        elif widget_type == "container":
            self.widget = QWidget(self)
            self.widget.setStyleSheet("border: 1px dashed gray;")

        color = self.properties.get("color", "")
        font_size = self.properties.get("font_size", 12)
        style = f"background-color: {color}; font-size: {font_size}px;" if color else f"font-size: {font_size}px;"
        self.widget.setStyleSheet(style)

        self.widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.widget.setGeometry(0, 0, self.width(), self.height())
        self.setMinimumSize(50, 30)
        self.setStyleSheet("")

        self.move_timer = QTimer(self)
        self.move_timer.setSingleShot(True)
        self.move_timer.setInterval(16)  # ~60 FPS
        self.move_timer.timeout.connect(self.process_move)

    def get_gui_editor_parent(self):
        parent = self.parentWidget()
        while parent and not hasattr(parent, 'handle_widget_selection'):
            parent = parent.parentWidget()
        return parent

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.preview_mode:
            self.drag_start_global_pos = event.globalPosition().toPoint()
            
            corner_size = 10
            in_resize_corner = (self.width() - event.pos().x() <= corner_size and
                                self.height() - event.pos().y() <= corner_size)

            if in_resize_corner:
                self.is_resizing = True
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                self.drag_start_size = self.size()
            else:
                self.is_dragging = True
                self.setCursor(Qt.CursorShape.SizeAllCursor)
                self.drag_start_widget_pos = self.pos()

            self.grabMouse()
            self.raise_()
            parent = self.get_gui_editor_parent()
            if parent:
                parent.handle_widget_selection(self, event)
            event.accept()

    def mouseMoveEvent(self, event):
        if (self.is_dragging or self.is_resizing) and not self.preview_mode:
            if not self.move_timer.isActive() and not self.is_processing_move:
                self.last_move_global_pos = event.globalPosition().toPoint()
                self.move_timer.start()
            event.accept()

    def process_move(self):
        try:
            self.is_processing_move = True
            if self.last_move_global_pos is None:
                return
            
            current_global_pos = self.last_move_global_pos
            parent = self.get_gui_editor_parent()
            if not parent or not self.isVisible():
                return

            if self.is_dragging and self.drag_start_widget_pos is not None:
                delta = current_global_pos - self.drag_start_global_pos
                new_pos = self.drag_start_widget_pos + delta
                
                snap_x, snap_y = new_pos.x(), new_pos.y()
                if parent.grid_enabled and self.grid_size > 1:
                    snap_x = round(snap_x / self.grid_size) * self.grid_size
                    snap_y = round(snap_y / self.grid_size) * self.grid_size

                guides = []
                try:
                    guides, snap_x, snap_y, _, _ = parent.calculate_alignment_guides(
                        self, snap_x, snap_y, self.width(), self.height()
                    )
                except Exception as e:
                    print(f"Error calculating alignment guides: {e}")
                
                parent.canvas.update_alignment_guides(guides)

                final_delta_x = snap_x - self.x()
                final_delta_y = snap_y - self.y()

                if self in parent.selected_widgets or "group_id" in self.properties:
                    moved_widgets = parent.selected_widgets
                    if "group_id" in self.properties:
                        group = next((g for g in parent.groups if g["id"] == self.properties["group_id"]), None)
                        if group: moved_widgets = group["widgets"]
                    
                    for widget in moved_widgets:
                        if "layout_id" not in widget.properties:
                            widget.move(int(widget.x() + final_delta_x), int(widget.y() + final_delta_y))
                else:
                    self.move(int(snap_x), int(snap_y))

            elif self.is_resizing and self.drag_start_size is not None:
                delta = current_global_pos - self.drag_start_global_pos
                new_width = self.drag_start_size.width() + delta.x()
                new_height = self.drag_start_size.height() + delta.y()

                new_width = max(self.minimumWidth(), new_width)
                new_height = max(self.minimumHeight(), new_height)

                if parent.grid_enabled and self.grid_size > 1:
                    new_width = round(new_width / self.grid_size) * self.grid_size
                    new_height = round(new_height / self.grid_size) * self.grid_size
                
                guides = []
                try:
                    guides, _, _, new_width, new_height = parent.calculate_alignment_guides(
                        self, self.x(), self.y(), new_width, new_height, is_resizing=True
                    )
                except Exception as e:
                    print(f"Error calculating alignment guides for resize: {e}")
                
                parent.canvas.update_alignment_guides(guides)

                self.resize(int(new_width), int(new_height))

        finally:
            self.is_processing_move = False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.preview_mode:
            self.is_dragging = False
            self.is_resizing = False
            self.unsetCursor()
            self.releaseMouse()
            
            parent = self.get_gui_editor_parent()
            if parent:
                parent.canvas.update_alignment_guides([])
                parent.update_properties()
                parent.add_to_history({"action": "modify", "widgets": [w.get_properties() for w in parent.selected_widgets]})
            event.accept()

    def show_context_menu(self, pos):
        if not self.preview_mode:
            parent = self.get_gui_editor_parent()
            if parent:
                parent.show_widget_context_menu(self, self.mapToGlobal(pos))

    def resizeEvent(self, event):
        self.widget.resize(self.size())
        super().resizeEvent(event)

    def get_properties(self):
        # Determine the correct way to get text based on widget type
        text_value = ""
        if self.widget_type in ["button", "field", "label", "checkbox"]:
            text_value = self.widget.text()
        elif self.widget_type == "textedit":
            text_value = self.widget.toPlainText()
        elif self.widget_type == "combobox":
            text_value = ",".join([self.widget.itemText(i) for i in range(self.widget.count())])

        props = {
            "type": self.widget_type,
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height(),
            "text": text_value,
            "color": self.properties.get("color", ""),
            "font_size": self.properties.get("font_size", 12),
            "custom_properties": self.custom_properties,
            "group_id": self.properties.get("group_id"),
            "layout_id": self.properties.get("layout_id")
        }
        props.update(self.properties)
        return {k: v for k, v in props.items() if v is not None}