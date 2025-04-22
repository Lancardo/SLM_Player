import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageFullScreen(QWidget):
    def __init__(self, pixmap, screen=None):
        super().__init__()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setCursor(Qt.BlankCursor)
        self.pixmap = pixmap
        if screen:
            geo = screen.geometry()
            self.setGeometry(geo)
        else:
            self.showFullScreen()
        self.update_pixmap()

    def update_pixmap(self):
        # 点对点显示，不缩放
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.size())
        self.resize(self.pixmap.size())
        self.move(0, 0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('图片全屏展示')
        self.image_path = None
        self.pixmap = None
        self.image_size = None
        self.screen_sizes = []
        self.warning_label = QLabel()
        self.screen_info_label = QLabel()
        self.init_ui()

    def init_ui(self):
        self.label = QLabel('未选择图片')
        self.label.setAlignment(Qt.AlignCenter)
        self.btn_select = QPushButton('选择图片')
        self.btn_show_main = QPushButton('主屏全屏展示')
        self.btn_show_ext = QPushButton('扩展屏全屏展示')
        self.btn_show_main.setEnabled(False)
        self.btn_show_ext.setEnabled(False)

        self.btn_select.clicked.connect(self.select_image)
        self.btn_show_main.clicked.connect(self.show_on_main)
        self.btn_show_ext.clicked.connect(self.show_on_ext)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.screen_info_label)
        vbox.addWidget(self.warning_label)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_select)
        hbox.addWidget(self.btn_show_main)
        hbox.addWidget(self.btn_show_ext)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.resize(500, 350)

    def update_screen_info(self):
        screens = QApplication.screens()
        info = []
        self.screen_sizes = []
        for idx, s in enumerate(screens):
            geo = s.geometry()
            info.append(f"屏幕{idx}: {geo.width()}x{geo.height()}")
            self.screen_sizes.append((geo.width(), geo.height()))
        self.screen_info_label.setText(" | ".join(info))

    def check_resolution(self):
        if not self.pixmap:
            self.warning_label.setText("")
            return
        img_w = self.pixmap.width()
        img_h = self.pixmap.height()
        warnings = []
        for idx, (sw, sh) in enumerate(self.screen_sizes):
            if img_w == sw and img_h == sh:
                continue
            else:
                warnings.append(f"图片与屏幕{idx}分辨率不匹配: 图片{img_w}x{img_h} 屏幕{sw}x{sh}")
        if warnings:
            self.warning_label.setStyleSheet('color: red')
            self.warning_label.setText("; ".join(warnings))
        else:
            self.warning_label.setStyleSheet('color: green')
            self.warning_label.setText("图片分辨率与所有屏幕点对点匹配")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg *.bmp *.gif)')
        if file_path:
            self.image_path = file_path
            self.pixmap = QPixmap(file_path)
            if self.pixmap.isNull():
                QMessageBox.warning(self, '错误', '无法加载图片')
                self.label.setText('未选择图片')
                self.btn_show_main.setEnabled(False)
                self.btn_show_ext.setEnabled(False)
                self.warning_label.setText("")
            else:
                self.label.setPixmap(self.pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.btn_show_main.setEnabled(True)
                screens = QApplication.screens()
                if len(screens) > 1:
                    self.btn_show_ext.setEnabled(True)
                else:
                    self.btn_show_ext.setEnabled(False)
                self.update_screen_info()
                self.check_resolution()

    def show_on_main(self):
        if self.pixmap:
            # 主屏分辨率
            screen = QApplication.screens()[0]
            geo = screen.geometry()
            img_w, img_h = self.pixmap.width(), self.pixmap.height()
            if img_w > geo.width() or img_h > geo.height():
                QMessageBox.warning(self, '警告', f'图片分辨率({img_w}x{img_h})大于主屏({geo.width()}x{geo.height()})，可能无法完整显示')
            self.fullscreen = ImageFullScreen(self.pixmap, screen)
            self.fullscreen.show()

    def show_on_ext(self):
        screens = QApplication.screens()
        if len(screens) > 1 and self.pixmap:
            ext_screen = screens[1]
            geo = ext_screen.geometry()
            img_w, img_h = self.pixmap.width(), self.pixmap.height()
            if img_w > geo.width() or img_h > geo.height():
                QMessageBox.warning(self, '警告', f'图片分辨率({img_w}x{img_h})大于扩展屏({geo.width()}x{geo.height()})，可能无法完整显示')
            self.fullscreen = ImageFullScreen(self.pixmap, ext_screen)
            self.fullscreen.show()
        else:
            QMessageBox.information(self, '提示', '未检测到扩展屏')

def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 