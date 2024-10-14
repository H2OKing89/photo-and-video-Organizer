# gui.py

import sys
import os
import threading
import psutil
import logging  # Ensure logging is imported
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox,
    QProgressBar, QDialog, QFormLayout, QCheckBox, QSpinBox, QComboBox,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QStandardPaths, QSettings
from PyQt6.QtGui import QTextCursor

from main import organize_media
from modules.logger import setup_logging  # Import the setup_logging function

# WorkerThread class to handle the organization process in a separate thread
class WorkerThread(QThread):
    """
    WorkerThread handles the media organization process in a separate thread to keep the GUI responsive.
    It emits signals to update the GUI with progress, status messages, and log entries.
    """
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, input_dir, output_dir, trash_dir, settings):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.trash_dir = trash_dir
        self.settings = settings
        self.cancel_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.clear()  # Not paused initially

    def run(self):
        """
        Executes the media organization process by calling the `organize_media` function.
        Emits log, progress, and status signals based on callbacks.
        """
        def log_callback(message):
            self.log_signal.emit(message)
            logging.info(message)  # Optionally log to file as well

        def progress_callback(value):
            self.progress_signal.emit(value)

        def status_callback(message):
            self.status_signal.emit(message)
            logging.info(message)  # Optionally log to file as well

        # Pass threading events for pause and cancel
        organize_media(
            self.input_dir,
            self.output_dir,
            self.trash_dir,
            log_callback=log_callback,
            settings=self.settings,
            progress_callback=progress_callback,
            status_callback=status_callback,
            pause_event=self.pause_event,
            cancel_event=self.cancel_event
        )

    def stop(self):
        """
        Signals the thread to stop the organization process.
        """
        self.cancel_event.set()
        self.resume()  # Ensure that if paused, it can exit

    def pause(self):
        """
        Pauses the organization process.
        """
        self.pause_event.set()
        self.log_signal.emit("Organization process paused.")
        logging.info("Organization process paused.")

    def resume(self):
        """
        Resumes the organization process if it was paused.
        """
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.log_signal.emit("Organization process resumed.")
            logging.info("Organization process resumed.")

    def is_paused(self):
        """
        Returns whether the thread is currently paused.
        """
        return self.pause_event.is_set()

# SettingsDialog class for user preferences
class SettingsDialog(QDialog):
    """
    SettingsDialog allows users to configure preferences such as duplicate detection methods,
    included file types, and naming conventions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings/Preferences")
        self.settings = self.parent().settings  # Access main settings

        layout = QFormLayout()

        # Duplicate Detection Method
        self.duplicate_method_combo = QComboBox()
        self.duplicate_method_combo.addItems(["MD5 Hash", "Perceptual Hash"])
        self.duplicate_method_combo.setCurrentText(self.settings.value('duplicate_method', 'MD5 Hash'))
        layout.addRow("Duplicate Detection Method:", self.duplicate_method_combo)

        # Include File Types
        self.include_jpg = QCheckBox("Include JPG/JPEG")
        self.include_jpg.setChecked(self.settings.value('include_jpg', True, type=bool))
        self.include_png = QCheckBox("Include PNG")
        self.include_png.setChecked(self.settings.value('include_png', True, type=bool))
        self.include_mp4 = QCheckBox("Include MP4")
        self.include_mp4.setChecked(self.settings.value('include_mp4', True, type=bool))
        self.include_mov = QCheckBox("Include MOV")
        self.include_mov.setChecked(self.settings.value('include_mov', True, type=bool))
        # Add more file types as needed
        file_types_layout = QVBoxLayout()
        file_types_layout.addWidget(self.include_jpg)
        file_types_layout.addWidget(self.include_png)
        file_types_layout.addWidget(self.include_mp4)
        file_types_layout.addWidget(self.include_mov)
        layout.addRow("Include File Types:", file_types_layout)

        # Naming Convention
        self.naming_convention_combo = QComboBox()
        self.naming_convention_combo.addItems(["Date_Location", "Date", "Location"])
        self.naming_convention_combo.setCurrentText(self.settings.value('naming_convention', 'Date_Location'))
        layout.addRow("Naming Convention:", self.naming_convention_combo)

        # Save and Cancel Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def save_settings(self):
        """
        Saves the current settings to QSettings.
        """
        self.settings.setValue('duplicate_method', self.duplicate_method_combo.currentText())
        self.settings.setValue('include_jpg', self.include_jpg.isChecked())
        self.settings.setValue('include_png', self.include_png.isChecked())
        self.settings.setValue('include_mp4', self.include_mp4.isChecked())
        self.settings.setValue('include_mov', self.include_mov.isChecked())
        self.settings.setValue('naming_convention', self.naming_convention_combo.currentText())
        self.accept()

# FeedbackDialog class for user feedback
class FeedbackDialog(QDialog):
    """
    FeedbackDialog allows users to submit feedback or report issues.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Feedback")
        layout = QVBoxLayout()
        feedback_label = QLabel("Please provide your feedback below:")
        self.feedback_text_edit = QTextEdit()
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_feedback)
        layout.addWidget(feedback_label)
        layout.addWidget(self.feedback_text_edit)
        layout.addWidget(submit_button)
        self.setLayout(layout)

    def submit_feedback(self):
        """
        Handles feedback submission.
        """
        feedback = self.feedback_text_edit.toPlainText().strip()
        if not feedback:
            QMessageBox.warning(self, "Empty Feedback", "Please enter some feedback before submitting.")
            return

        # Implement feedback handling logic here (e.g., send to email or save to file)
        # For demonstration, we'll just log it and show a message box
        logging.info(f"User Feedback: {feedback}")
        QMessageBox.information(self, "Feedback Submitted", "Thank you for your feedback!")
        self.accept()

# HelpDialog class for user assistance
class HelpDialog(QDialog):
    """
    HelpDialog provides help documentation to the user.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        help_text = """
        <h2>Photo and Video Organizer Help</h2>
        <p>Welcome to the Photo and Video Organizer! Follow the steps below to organize your media files:</p>
        <ol>
            <li><b>Select Input Directory:</b> Choose the folder containing your photos and videos.</li>
            <li><b>Select Output Directory:</b> Choose where you want the organized files to be stored.</li>
            <li><b>Select Trash Directory:</b> Choose where duplicate files will be moved.</li>
            <li><b>Settings:</b> Customize your preferences such as duplicate detection methods and file types.</li>
            <li><b>Organize:</b> Click the "Organize" button to start the process.</li>
            <li><b>Monitor Progress:</b> Watch the progress bar and status messages to track the organization.</li>
            <li><b>Logs:</b> View detailed logs in the logs section.</li>
            <li><b>Feedback:</b> Submit feedback or report issues using the "Feedback" button.</li>
        </ol>
        <p>If you encounter any issues or have suggestions, feel free to submit feedback!</p>
        """
        layout = QVBoxLayout()
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        self.setLayout(layout)

# PhotoOrganizerGUI class for the main application window
class PhotoOrganizerGUI(QWidget):
    """
    PhotoOrganizerGUI is the main GUI class for the Photo and Video Organizer program.
    It provides interfaces for selecting directories, initiating the organization process,
    viewing logs, managing settings, and submitting feedback.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo and Video Organizer")
        self.setGeometry(100, 100, 800, 600)
        self.settings = QSettings("YourCompany", "PhotoOrganizer")  # Initialize QSettings

        # Initialize logging
        log_file_path = os.path.join('logs', 'photo_organizer.log')
        setup_logging(log_file_path)

        self.init_ui()
        self.thread = None  # Initialize the worker thread

    def init_ui(self):
        """
        Initializes the GUI layout and widgets.
        """
        layout = QVBoxLayout()

        # Input Directory Selection
        input_layout = QHBoxLayout()
        input_label = QLabel("Input Directory:")
        self.input_line_edit = QLineEdit()
        input_browse_button = QPushButton("Browse")
        input_browse_button.setToolTip("Select the directory containing your photos and videos.")
        input_browse_button.clicked.connect(self.browse_input_directory)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(input_browse_button)
        layout.addLayout(input_layout)

        # Output Directory Selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output Directory:")
        self.output_line_edit = QLineEdit()
        output_browse_button = QPushButton("Browse")
        output_browse_button.setToolTip("Select the directory where organized media will be stored.")
        output_browse_button.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_line_edit)
        output_layout.addWidget(output_browse_button)
        layout.addLayout(output_layout)

        # Trash Directory Selection
        trash_layout = QHBoxLayout()
        trash_label = QLabel("Trash Directory:")
        self.trash_line_edit = QLineEdit()
        trash_browse_button = QPushButton("Browse")
        trash_browse_button.setToolTip("Select the directory where duplicate files will be moved.")
        trash_browse_button.clicked.connect(self.browse_trash_directory)
        trash_layout.addWidget(trash_label)
        trash_layout.addWidget(self.trash_line_edit)
        trash_layout.addWidget(trash_browse_button)
        layout.addLayout(trash_layout)

        # Initialize Log Display Before Loading Directories
        log_label = QLabel("Logs:")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(log_label)
        layout.addWidget(self.log_text_edit)

        # Now, Load Directories
        self.load_directories()

        # Organize Button
        self.organize_button = QPushButton("Organize")
        self.organize_button.setToolTip("Start organizing your photos and videos.")
        self.organize_button.clicked.connect(self.start_organization)
        layout.addWidget(self.organize_button)

        # Cancel Button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel the ongoing organization process.")
        self.cancel_button.clicked.connect(self.cancel_organization)
        self.cancel_button.setEnabled(False)  # Disabled initially
        layout.addWidget(self.cancel_button)

        # Pause and Resume Buttons
        pause_resume_layout = QHBoxLayout()
        self.pause_button = QPushButton("Pause")
        self.pause_button.setToolTip("Pause the ongoing organization process.")
        self.pause_button.clicked.connect(self.pause_organization)
        self.pause_button.setEnabled(False)  # Disabled initially
        self.resume_button = QPushButton("Resume")
        self.resume_button.setToolTip("Resume the paused organization process.")
        self.resume_button.clicked.connect(self.resume_organization)
        self.resume_button.setEnabled(False)  # Disabled initially
        pause_resume_layout.addWidget(self.pause_button)
        pause_resume_layout.addWidget(self.resume_button)
        layout.addLayout(pause_resume_layout)

        # Progress Bar
        progress_layout = QHBoxLayout()
        progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        # Status Label
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        self.status_display = QLabel("Idle")
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_display)
        layout.addLayout(status_layout)

        # CPU Usage Indicator
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU Usage:")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        layout.addLayout(cpu_layout)

        # Memory Usage Indicator
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Memory Usage:")
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_progress)
        layout.addLayout(memory_layout)

        # Settings, Feedback, and Help Buttons
        settings_feedback_layout = QHBoxLayout()
        self.settings_button = QPushButton("Settings")
        self.settings_button.setToolTip("Open settings/preferences.")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.feedback_button = QPushButton("Feedback")
        self.feedback_button.setToolTip("Submit feedback or report issues.")
        self.feedback_button.clicked.connect(self.open_feedback_dialog)
        self.help_button = QPushButton("Help")
        self.help_button.setToolTip("Open help documentation.")
        self.help_button.clicked.connect(self.open_help_dialog)
        settings_feedback_layout.addWidget(self.settings_button)
        settings_feedback_layout.addWidget(self.feedback_button)
        settings_feedback_layout.addWidget(self.help_button)
        layout.addLayout(settings_feedback_layout)

        self.setLayout(layout)

        # Timer for updating resource usage
        self.resource_timer = QTimer()
        self.resource_timer.setInterval(1000)  # Update every second
        self.resource_timer.timeout.connect(self.update_resource_usage)
        self.resource_timer.start()

    def load_directories(self):
        """
        Loads the input, output, and trash directories from QSettings.
        If not set, initializes them with default directories.
        """
        input_dir = self.settings.value("input_directory")
        output_dir = self.settings.value("output_directory")
        trash_dir = self.settings.value("trash_directory")

        # If directories are not set, use default directories
        if not input_dir:
            input_dir = get_default_pictures_folder()
            self.settings.setValue("input_directory", input_dir)
            self.log_text_edit.append(f"Default Input Directory set to: {input_dir}")
            logging.info(f"Default Input Directory set to: {input_dir}")

        if not output_dir:
            output_dir = get_default_output_folder()
            self.settings.setValue("output_directory", output_dir)
            os.makedirs(output_dir, exist_ok=True)
            self.log_text_edit.append(f"Default Output Directory created at: {output_dir}")
            logging.info(f"Default Output Directory created at: {output_dir}")

        if not trash_dir:
            trash_dir = get_default_trash_folder()
            self.settings.setValue("trash_directory", trash_dir)
            os.makedirs(trash_dir, exist_ok=True)
            self.log_text_edit.append(f"Default Trash Directory created at: {trash_dir}")
            logging.info(f"Default Trash Directory created at: {trash_dir}")

        # Set the line edits to the loaded or default directories
        self.input_line_edit.setText(input_dir)
        self.output_line_edit.setText(output_dir)
        self.trash_line_edit.setText(trash_dir)

    def browse_input_directory(self):
        """
        Opens a directory selection dialog for the input directory.
        """
        default_dir = self.input_line_edit.text() or get_default_pictures_folder()
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory", default_dir, QFileDialog.Option.ShowDirsOnly)
        if directory:
            self.input_line_edit.setText(directory)
            self.settings.setValue("input_directory", directory)
            logging.info(f"Input Directory set to: {directory}")
            self.log_text_edit.append(f"Input Directory set to: {directory}")

    def browse_output_directory(self):
        """
        Opens a directory selection dialog for the output directory.
        """
        default_dir = self.output_line_edit.text() or get_default_output_folder()
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", default_dir, QFileDialog.Option.ShowDirsOnly)
        if directory:
            self.output_line_edit.setText(directory)
            self.settings.setValue("output_directory", directory)
            logging.info(f"Output Directory set to: {directory}")
            self.log_text_edit.append(f"Output Directory set to: {directory}")

    def browse_trash_directory(self):
        """
        Opens a directory selection dialog for the trash directory.
        """
        default_dir = self.trash_line_edit.text() or get_default_trash_folder()
        directory = QFileDialog.getExistingDirectory(self, "Select Trash Directory", default_dir, QFileDialog.Option.ShowDirsOnly)
        if directory:
            self.trash_line_edit.setText(directory)
            self.settings.setValue("trash_directory", directory)
            logging.info(f"Trash Directory set to: {directory}")
            self.log_text_edit.append(f"Trash Directory set to: {directory}")

    def start_organization(self):
        """
        Initiates the media organization process by starting the WorkerThread.
        """
        input_dir = self.input_line_edit.text()
        output_dir = self.output_line_edit.text()
        trash_dir = self.trash_line_edit.text()

        # Validate directory selections
        if not input_dir or not output_dir or not trash_dir:
            QMessageBox.warning(self, "Input Error", "Please select all directories.")
            return

        # Disable the organize button and enable cancel and pause buttons
        self.organize_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)

        # Initialize settings (can be loaded from a config file)
        self.settings_dict = self.load_settings()

        # Start the worker thread
        self.thread = WorkerThread(input_dir, output_dir, trash_dir, self.settings_dict)
        self.thread.log_signal.connect(self.update_log)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.status_signal.connect(self.update_status)
        self.thread.finished.connect(self.organization_finished)
        self.thread.start()

    def cancel_organization(self):
        """
        Cancels the ongoing media organization process.
        """
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.log_text_edit.append("Cancellation requested...")
            self.status_display.setText("Cancelling...")
            logging.info("Cancellation requested by user.")

    def pause_organization(self):
        """
        Pauses the ongoing media organization process.
        """
        if self.thread and self.thread.isRunning():
            self.thread.pause()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
            logging.info("Organization process paused by user.")

    def resume_organization(self):
        """
        Resumes the paused media organization process.
        """
        if self.thread and self.thread.isRunning():
            self.thread.resume()
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            logging.info("Organization process resumed by user.")

    def organization_finished(self):
        """
        Handles the completion of the media organization process.
        """
        self.organize_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        QMessageBox.information(self, "Completed", "Media organization completed.")
        self.status_display.setText("Completed.")
        logging.info("Organization process completed.")

    def update_log(self, message):
        """
        Updates the log display with new log messages.
        """
        # Determine log level based on message content
        if "error" in message.lower():
            color = "red"
        elif "warning" in message.lower():
            color = "orange"
        elif "completed" in message.lower() or "started" in message.lower() or "processing" in message.lower():
            color = "green"
        else:
            color = "black"

        # Append colored text to the log display
        self.log_text_edit.append(f"<span style='color:{color};'>{message}</span>")
        self.log_text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def update_progress(self, value):
        """
        Updates the progress bar with the given value.
        """
        self.progress_bar.setValue(value)

    def update_status(self, message):
        """
        Updates the status label with the given message.
        """
        self.status_display.setText(message)
        logging.info(f"Status Update: {message}")

    def update_resource_usage(self):
        """
        Updates the CPU and memory usage indicators.
        """
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        self.cpu_progress.setValue(int(cpu))
        self.memory_progress.setValue(int(memory))

    def open_settings_dialog(self):
        """
        Opens the settings/preferences dialog.
        """
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Load updated settings
            self.settings_dict = self.load_settings()
            self.log_text_edit.append("Settings updated. Please restart the organization process to apply changes.")
            logging.info("Settings updated by user.")

    def open_feedback_dialog(self):
        """
        Opens the feedback submission dialog.
        """
        dialog = FeedbackDialog(self)
        dialog.exec()

    def open_help_dialog(self):
        """
        Opens the help documentation dialog.
        """
        dialog = HelpDialog(self)
        dialog.exec()

    def load_settings(self):
        """
        Loads user settings from QSettings.
        """
        settings = {
            'duplicate_method': self.settings.value('duplicate_method', 'MD5 Hash'),
            'include_jpg': self.settings.value('include_jpg', True, type=bool),
            'include_png': self.settings.value('include_png', True, type=bool),
            'include_mp4': self.settings.value('include_mp4', True, type=bool),
            'include_mov': self.settings.value('include_mov', True, type=bool),
            'naming_convention': self.settings.value('naming_convention', 'Date_Location')
        }
        return settings

    def closeEvent(self, event):
        """
        Overrides the close event to perform any necessary cleanup.
        """
        if self.thread and self.thread.isRunning():
            reply = QMessageBox.question(
                self,
                'Quit',
                "An organization process is still running. Do you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.thread.stop()
                self.thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()  # Let the window close

# Entry point for the application
def main():
    """
    Entry point for the Photo and Video Organizer GUI application.
    """
    app = QApplication(sys.argv)
    gui = PhotoOrganizerGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
