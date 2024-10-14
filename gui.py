# gui.py

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from main import organize_media

class WorkerThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, input_dir, output_dir, trash_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.trash_dir = trash_dir

    def run(self):
        def log_callback(message):
            self.log_signal.emit(message)

        organize_media(self.input_dir, self.output_dir, self.trash_dir, log_callback)

class PhotoOrganizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo and Video Organizer")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input Directory
        input_layout = QHBoxLayout()
        input_label = QLabel("Input Directory:")
        self.input_line_edit = QLineEdit()
        input_browse_button = QPushButton("Browse")
        input_browse_button.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(input_browse_button)
        layout.addLayout(input_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Directory:")
        self.output_line_edit = QLineEdit()
        output_browse_button = QPushButton("Browse")
        output_browse_button.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(output_browse_button)
        layout.addLayout(output_layout)

        # Trash Directory
        trash_layout = QHBoxLayout()
        trash_label = QLabel("Trash Directory:")
        self.trash_line_edit = QLineEdit()
        trash_browse_button = QPushButton("Browse")
        trash_browse_button.clicked.connect(self.browse_trash_directory)
        trash_layout.addWidget(trash_label)
        trash_layout.addWidget(self.trash_line_edit)
        trash_layout.addWidget(trash_browse_button)
        layout.addLayout(trash_layout)

        # Organize Button
        self.organize_button = QPushButton("Organize")
        self.organize_button.clicked.connect(self.start_organization)
        layout.addWidget(self.organize_button)

        # Log Display
        log_label = QLabel("Logs:")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(log_label)
        layout.addWidget(self.log_text_edit)

        self.setLayout(layout)

    def browse_input_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.input_line_edit.setText(directory)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_line_edit.setText(directory)

    def browse_trash_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Trash Directory")
        if directory:
            self.trash_line_edit.setText(directory)

    def start_organization(self):
        input_dir = self.input_line_edit.text()
        output_dir = self.output_line_edit.text()
        trash_dir = self.trash_line_edit.text()

        if not input_dir or not output_dir or not trash_dir:
            QMessageBox.warning(self, "Input Error", "Please select all directories.")
            return

        # Disable the organize button to prevent multiple clicks
        self.organize_button.setEnabled(False)
        self.log_text_edit.append("Starting organization...")

        # Start the worker thread
        self.thread = WorkerThread(input_dir, output_dir, trash_dir)
        self.thread.log_signal.connect(self.update_log)
        self.thread.finished.connect(self.organization_finished)
        self.thread.start()

    def update_log(self, message):
        self.log_text_edit.append(message)

    def organization_finished(self):
        self.organize_button.setEnabled(True)
        QMessageBox.information(self, "Completed", "Media organization completed.")

def main():
    app = QApplication(sys.argv)
    gui = PhotoOrganizerGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
