import sys
import time
import os
import dlib
import cv2  # Add this line
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QSlider, QDialog, \
    QHBoxLayout, QCheckBox, QMessageBox, QProgressBar, QComboBox, QFileDialog

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 400, 200)

        checkbox1 = QCheckBox("Option 1")
        checkbox2 = QCheckBox("Option 2")
        checkbox3 = QCheckBox("Option 3")

        layout = QVBoxLayout()
        layout.addWidget(checkbox1)
        layout.addWidget(checkbox2)
        layout.addWidget(checkbox3)

        proxy_checkbox = QCheckBox("Enable Proxy")
        layout.addWidget(proxy_checkbox)

        tor_checkbox = QCheckBox("Enable Tor")
        layout.addWidget(tor_checkbox)

        gdpr_checkbox = QCheckBox("Disable European GDPR Protection")
        layout.addWidget(gdpr_checkbox)

        self.setLayout(layout)



class ExtractPhoneNumberThread(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, username):
        super(ExtractPhoneNumberThread, self).__init__()
        self.username = username

    def run(self):
        for i in range(101):
            time.sleep(0.05)  # Simulating processing time
            self.progress_updated.emit(i)

        phone_number = extract_phone_number(self.username)
        self.progress_updated.emit(100)
        self.finished.emit(phone_number)

class FaceRecognitionThread(QThread):
    image_processed = pyqtSignal(str)

    def __init__(self, image_path):
        super(FaceRecognitionThread, self).__init__()
        self.image_path = image_path

    def run(self):
        # Simulating face recognition process
        time.sleep(2)

        # Load the face detector model from dlib
        detector = dlib.get_frontal_face_detector()

        # Load the image and convert it to grayscale
        image = dlib.load_rgb_image(self.image_path)
        gray = dlib.cvtColor(image, dlib.COLOR_RGB2GRAY)

        # Detect faces in the image
        faces = detector(gray)

        # Create an OpenCV image object
        cv_image = cv2.imread(self.image_path)

        # Draw red rectangle around each detected face
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            # Convert the face coordinates to OpenCV format
            cv_face = (x, y, x + w, y + h)
            # Draw the rectangle on the image
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Save the processed image with face marks
        processed_image_path = "processed_image.jpg"
        cv2.imwrite(processed_image_path, cv_image)

        # Emitting the processed image path
        self.image_processed.emit(processed_image_path)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Instagram Phone Number Extractor")
        self.setGeometry(100, 100, 800, 600)

        self.function_label = QLabel("Instagram Phone Number Extractor")
        self.function_label.setAlignment(Qt.AlignCenter)

        self.username_label = QLabel("Instagram Username:")
        self.username_input = QLineEdit()
        self.get_number_button = QPushButton("Get Phone Number")
        self.result_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.function_combobox = QComboBox()
        self.function_combobox.addItem("Function 1")
        self.function_combobox.addItem("Function 2")
        self.function_combobox.addItem("Function 3")

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.add_photo_button = QPushButton("Add Photo")
        self.scan_face_button = QPushButton("Scan Face")
        self.add_photo_button.clicked.connect(self.add_photo)
        self.scan_face_button.clicked.connect(self.scan_face)
        self.photo_path = ""
        self.face_rects = []

        layout = QVBoxLayout()
        layout.addWidget(self.function_label)
        layout.addWidget(self.function_combobox)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.get_number_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.photo_label)
        layout.addWidget(self.add_photo_button)
        layout.addWidget(self.scan_face_button)

        self.get_number_button.clicked.connect(self.start_extraction)
        self.function_combobox.currentIndexChanged.connect(self.handle_function_selection)

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings_dialog)
        layout.addWidget(settings_button)

        self.setLayout(layout)

    def start_extraction(self):
        username = self.username_input.text()

        self.thread = ExtractPhoneNumberThread(username)
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.finished.connect(self.show_phone_number)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_phone_number(self, phone_number):
        self.result_label.setText(f"The phone number for {self.username_input.text()} is: {phone_number}")

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec_()

    def handle_function_selection(self, index):
        selected_function = self.function_combobox.itemText(index)
        if selected_function == "Function 1":
            # Here you can add logic for Function 1
            self.username_label.show()
            self.username_input.show()
            self.get_number_button.show()
            self.result_label.show()
            self.progress_bar.show()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()
        elif selected_function == "Function 2":
            # Clear and hide elements for other functions
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
        else:
            # Clear and hide elements for other functions
            self.username_label.clear()
            self.username_input.clear()
            self.get_number_button.hide()
            self.result_label.clear()
            self.progress_bar.setValue(0)
            self.username_label.hide()
            self.username_input.hide()
            self.result_label.hide()
            self.progress_bar.hide()
            self.photo_label.hide()
            self.add_photo_button.hide()
            self.scan_face_button.hide()

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
            self.recognition_thread = FaceRecognitionThread(self.photo_path)
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

app = QApplication(sys.argv)
window = MainWindow()
window.show()

sys.exit(app.exec_())