# ReqIF Scraper GUI

import sys
import os
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFormLayout, QRadioButton, QPushButton, QLineEdit, QFileDialog, QLabel, QComboBox, QTextEdit, QHBoxLayout)
from PyQt6.QtGui import QIcon
from PermanentHeader import permanent_header
from NextButton import NextButton
from Functions import find_reqif_attribute_values
import io

# Custom stream class to redirect stdout to a QTextEdit widget
class QTextEditLogger(io.StringIO):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def write(self, s):
        self.text_edit.append(s)
        QApplication.processEvents()  # Ensure GUI remains responsive

class ReqIFScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Import Formatter")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_width = 800
        window_height = 350
        x = (screen_geometry.width() - window_width) // 2
        y = (screen_geometry.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'jama_logo_icon.png')
        self.setWindowIcon(QIcon(icon_path))

        self.main_app_layout = QVBoxLayout()
        self.setLayout(self.main_app_layout)

        header_layout, separator = permanent_header("Import Formatter", 'jama_logo.png')
        self.main_app_layout.addLayout(header_layout)
        self.main_app_layout.addWidget(separator)

        self.dynamic_content_layout = QVBoxLayout()
        self.main_app_layout.addLayout(self.dynamic_content_layout)
        self.main_app_layout.addStretch()

        self.DetailsPage()

    def DetailsPage(self):
        self.clearLayout(self.dynamic_content_layout)
        layout = QVBoxLayout()

        # Add text input for user to input word to parse with
        keyword_layout = QFormLayout()
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("i.e. image.png")
        keyword_layout.addRow("Enter Keyword:", self.word_input)
        layout.addLayout(keyword_layout)

        # Add file select widgets
        self.select_file_button = QPushButton("Select File")
        self.select_file_button.clicked.connect(self.select_file)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_file_button)
        self.select_file_button.setStyleSheet("background-color: #0052CC; color: white;")
        self.file_path_label = QLabel("No file selected")
        button_layout.addWidget(self.file_path_label)
        layout.addLayout(button_layout) 

        # Add a QTextEdit widget for the output readout
        self.output_readout = QTextEdit()
        self.output_readout.setReadOnly(True)
        self.output_readout.setPlaceholderText("Output will be displayed here...")

        self.submit_button = NextButton("Run", True)

        self.dynamic_content_layout.addLayout(layout)
        self.dynamic_content_layout.addWidget(self.submit_button)
        self.dynamic_content_layout.addWidget(self.output_readout)
        self.dynamic_content_layout.addStretch()

        self.submit_button.clicked.connect(self.run)
        
        # Store the original stdout
        self.original_stdout = sys.stdout
        # Create an instance of the custom stream and redirect stdout
        sys.stdout = QTextEditLogger(self.output_readout)

    def run(self):
        # Clear previous output
        self.output_readout.clear()
        
        keyword = self.word_input.text()
        if hasattr(self, 'file_path') and self.file_path:
            # Use the stored self.file_path variable
            print(f"Starting process with file: '{self.file_path}' and keyword: '{keyword}'...")
            find_reqif_attribute_values(self.file_path, keyword)
            print("Process completed.")
        else:
            print("Warning: Please select a file first.")
    
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select File", "", "Files (*.reqif)")
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(f"Selected: {os.path.basename(self.file_path)}")
            self.select_file_button.setStyleSheet("background-color: #53575A; color: white;")

    def closeEvent(self, event):
        # Restore the original stdout when the application closes
        sys.stdout = self.original_stdout
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReqIFScraperGUI()
    window.show()
    sys.exit(app.exec())