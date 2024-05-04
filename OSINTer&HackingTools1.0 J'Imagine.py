import sys
import time
import os
import dlib
import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QSlider, QDialog, \
    QHBoxLayout, QCheckBox, QMessageBox, QProgressBar, QComboBox, QFileDialog, QMainWindow, QAction

import pandas as pd

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 200)

        self.language_label = QLabel("Language:")
        self.language_combobox = QComboBox()
        self.language_combobox.addItem("English")
        self.language_combobox.addItem("Russian")

        self.function_label = QLabel("Select Functions to Show:")
        self.instagram_checkbox = QCheckBox("Instagram Phone Number Extractor")
        self.scan_face_checkbox = QCheckBox("Scan Face")
        self.whatsapp_checkbox = QCheckBox("WhatsApp Phone Number Search")
        self.phone_number_checkbox = QCheckBox("Phone Number Search by Full Name")
        self.network_scanning_checkbox = QCheckBox("Network Scanning")

        self.vpn_label = QLabel("VPN Key:")
        self.vpn_input = QLineEdit()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        layout = QVBoxLayout()
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combobox)
        layout.addWidget(self.function_label)
        layout.addWidget(self.instagram_checkbox)
        layout.addWidget(self.scan_face_checkbox)
        layout.addWidget(self.whatsapp_checkbox)
        layout.addWidget(self.phone_number_checkbox)
        layout.addWidget(self.network_scanning_checkbox)
        layout.addWidget(self.vpn_label)
        layout.addWidget(self.vpn_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        language = self.language_combobox.currentText()
        functions = {
            "Instagram Phone Number Extractor": self.instagram_checkbox.isChecked(),
            "Scan Face": self.scan_face_checkbox.isChecked(),
            "WhatsApp Phone Number Search": self.whatsapp_checkbox.isChecked(),
            "Phone Number Search by Full Name": self.phone_number_checkbox.isChecked(),
            "Network Scanning": self.network_scanning_checkbox.isChecked()
        }
        vpn_key = self.vpn_input.text()

        # Save settings here or emit a signal to notify MainWindow
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Multi-Function Extractor")
        self.setGeometry(100, 100, 800, 600)

        self.function_label = QLabel("Multi-Function Extractor")
        self.function_label.setAlignment(Qt.AlignCenter)

        self.username_label = QLabel("Username / Full Name:")
        self.username_input = QLineEdit()
        self.get_number_button = QPushButton("Start Extraction")
        self.result_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.function_combobox = QComboBox()
        self.function_combobox.addItem("Instagram Phone Number Extractor")
        self.function_combobox.addItem("Scan Face")
        self.function_combobox.addItem("WhatsApp Phone Number Search")
        self.function_combobox.addItem("Phone Number Search by Full Name")
        self.function_combobox.addItem("Network Scanning")  # Added Function 5

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.add_photo_button = QPushButton("Add Photo")
        self.scan_face_button = QPushButton("Scan Face")
        self.add_photo_button.clicked.connect(self.add_photo)
        self.scan_face_button.clicked.connect(self.scan_face)
        self.photo_path = ""
        self.face_rects = []

        self.country_combobox = QComboBox()
        self.country_combobox.addItem("Russia")
        self.operator_combobox = QComboBox()
        self.operator_combobox.addItem("MTS")
        self.operator_combobox.addItem("MegaFon")
        self.operator_combobox.addItem("Beeline")
        self.operator_combobox.addItem("Tele2")
        self.country_combobox.hide()
        self.operator_combobox.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.function_label)
        layout.addWidget(self.function_combobox)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.country_combobox)
        layout.addWidget(self.operator_combobox)
        layout.addWidget(self.get_number_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.photo_label)
        layout.addWidget(self.add_photo_button)
        layout.addWidget(self.scan_face_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.get_number_button.clicked.connect(self.start_extraction)
        self.function_combobox.currentIndexChanged.connect(self.handle_function_selection)

        self.create_menus()

    def create_menus(self):
        about_action = QAction("About J'Imagine", self)
        about_action.triggered.connect(self.show_about_dialog)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)

        menu_bar = self.menuBar()
        about_menu = menu_bar.addMenu("About")
        settings_menu = menu_bar.addMenu("Settings")
        about_menu.addAction(about_action)
        settings_menu.addAction(settings_action)

    def show_about_dialog(self):
        QMessageBox.about(self, "About J'Imagine", "J'Imagine is a multi-function extractor program. Inspired by the song 'J'Imagine' by Valentina Tronel. Contact Email: ulevaskevic@gmail.com. Version: 1.0")

    def show_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def start_extraction(self):
        selected_function = self.function_combobox.currentText()
        if selected_function == "Instagram Phone Number Extractor":
            username = self.username_input.text()

            self.thread = InstagramPhoneNumberExtractorThread(username)
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.finished.connect(self.show_phone_number)
            self.thread.start()
        elif selected_function == "Scan Face":
            self.username_label.clear()
            self.username_input.clear()
            self.get_number_button.hide()
            self.result_label.clear()
            self.progress_bar.setValue(0)
            self.username_label.hide()
            self.username_input.hide()
            self.result_label.hide()
            self.progress_bar.hide()
            self.photo_label.show()
            self.add_photo_button.show()
            self.scan_face_button.show()
        elif selected_function == "WhatsApp Phone Number Search":
            self.username_label.setText("WhatsApp Nickname:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Start Search")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
        elif selected_function == "Phone Number Search by Full Name":
            self.username_label.setText("Full Name:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Start Search")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.show()
            self.operator_combobox.show()
        elif selected_function == "Network Scanning":  # Added Function 5
            self.username_label.setText("Wi-Fi Router:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Scan Wi-Fi Router")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.hide()
            self.operator_combobox.hide()

            self.network_scanning_dialog = NetworkScanningDialog(self)
            self.network_scanning_dialog.exec_()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_phone_number(self, phone_number):
        self.result_label.setText(f"The phone number for {self.username_input.text()} is: {phone_number}")

    def handle_function_selection(self, index):
        selected_function = self.function_combobox.itemText(index)
        if selected_function == "Instagram Phone Number Extractor":
            self.username_label.setText("Instagram Username:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Get Phone Number")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.hide()
            self.operator_combobox.hide()
        elif selected_function == "Scan Face":
            self.username_label.clear()
            self.username_input.clear()
            self.get_number_button.hide()
            self.result_label.clear()
            self.progress_bar.setValue(0)
            self.username_label.hide()
            self.username_input.hide()
            self.result_label.hide()
            self.progress_bar.hide()
            self.photo_label.show()
            self.add_photo_button.show()
            self.scan_face_button.show()
            self.country_combobox.hide()
            self.operator_combobox.hide()
        elif selected_function == "WhatsApp Phone Number Search":
            self.username_label.setText("WhatsApp Nickname:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Start Search")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.hide()
            self.operator_combobox.hide()
        elif selected_function == "Phone Number Search by Full Name":
            self.username_label.setText("Full Name:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Start Search")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.show()
            self.operator_combobox.show()
        elif selected_function == "Network Scanning":  # Added Function 5
            self.username_label.setText("Wi-Fi Router:")
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.setText("Scan Wi-Fi Router")
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
            self.country_combobox.hide()
            self.operator_combobox.hide()

            self.network_scanning_dialog = NetworkScanningDialog(self)
            self.network_scanning_dialog.exec_()

    def add_photo(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                self.photo_path = file_paths[0]
                pixmap = QPixmap(self.photo_path)
                self.photo_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
                self.face_rects = []

    def scan_face(self):
        if self.photo_path:
            self.recognition_thread = ScanFaceThread(self.photo_path)
            self.recognition_thread.image_processed.connect(self.handle_image_processed)
            self.recognition_thread.start()

    def handle_image_processed(self, processed_image_path):
        # Update the displayed image with the marked faces
        pixmap = QPixmap(processed_image_path)
        painter = QPainter(pixmap)
        pen = QPen(Qt.red, 2)
        painter.setPen(pen)
        for face_rect in self.face_rects:
            painter.drawRect(face_rect)
        painter.end()

        # Set the updated image to the photo label
        self.photo_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))

    def detect_faces(self, image):
        # Load the face detector model from dlib
        detector = dlib.get_frontal_face_detector()

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = detector(gray)

        # Store the face rectangles
        self.face_rects = [dlib.rectangle(face.left(), face.top(), face.right(), face.bottom()) for face in faces]

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = event.mimeData().urls()
        if files:
            self.photo_path = files[0].toLocalFile()
            pixmap = QPixmap(self.photo_path)
            self.photo_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
            self.face_rects = []
            self.scan_face()  # Scan face after dropping the photo

    def save_numbers_to_file(self, numbers):
        file_dialog = QFileDialog()
        file_dialog.setDefaultSuffix(".xlsx")
        file_name, _ = file_dialog.getSaveFileName(self, "Save Numbers", "", "Excel Files (*.xlsx)")
        if file_name:
            numbers.to_excel(file_name, index=False)

    def show_network_devices(self, network_devices):
        virus_name, solution = network_devices

        if virus_name:
            # Save the virus report to a DOCX file
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix(".docx")
            file_name, _ = file_dialog.getSaveFileName(self, "Save Virus Report", "", "DOCX Files (*.docx)")
            if file_name:
                save_virus_report(file_name, virus_name, solution)

        if self.language_combobox.currentText() == "English":
            if virus_name:
                self.result_label.setText(f"Network scanning detected virus: {virus_name}\nSolution: {solution}")
            else:
                self.result_label.setText("No viruses found during network scanning.")
        elif self.language_combobox.currentText() == "Russian":
            if virus_name:
                self.result_label.setText(f"Сканирование сети обнаружило вирус: {virus_name}\nРешение: {solution}")
            else:
                self.result_label.setText("Во время сканирования сети вирусы не обнаружены.")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
