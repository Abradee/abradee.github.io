import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QHBoxLayout, QTabWidget, QToolBar, QAction, QDialog, QVBoxLayout, QListWidget,
    QDialogButtonBox, QLabel, QComboBox, QInputDialog, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None, homepage=None, theme=None, bookmarks=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.homepage = homepage
        self.theme = theme
        self.bookmarks = bookmarks

        layout = QVBoxLayout()

        # Homepage settings
        layout.addWidget(QLabel("Homepage:"))
        self.homepage_edit = QLineEdit(self.homepage)
        layout.addWidget(self.homepage_edit)

        # Theme settings
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.theme)
        layout.addWidget(self.theme_combo)

        # Bookmark management
        layout.addWidget(QLabel("Bookmarks:"))
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.addItems(self.bookmarks)
        layout.addWidget(self.bookmarks_list)

        # Add, Edit, and Remove Bookmark Buttons
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_bookmark)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_bookmark)
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_bookmark)

        bookmark_buttons_layout = QHBoxLayout()
        bookmark_buttons_layout.addWidget(self.add_button)
        bookmark_buttons_layout.addWidget(self.edit_button)
        bookmark_buttons_layout.addWidget(self.remove_button)
        layout.addLayout(bookmark_buttons_layout)

        # OK and Cancel Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def add_bookmark(self):
        url, ok = QInputDialog.getText(self, "Add Bookmark", "Enter URL:")
        if ok and url:
            self.bookmarks_list.addItem(url)

    def edit_bookmark(self):
        selected_item = self.bookmarks_list.currentItem()
        if selected_item:
            new_url, ok = QInputDialog.getText(self, "Edit Bookmark", "Edit URL:", text=selected_item.text())
            if ok and new_url:
                selected_item.setText(new_url)

    def remove_bookmark(self):
        selected_item = self.bookmarks_list.currentItem()
        if selected_item:
            self.bookmarks_list.takeItem(self.bookmarks_list.row(selected_item))

    def get_settings(self):
        homepage = self.homepage_edit.text()
        theme = self.theme_combo.currentText()
        bookmarks = [self.bookmarks_list.item(i).text() for i in range(self.bookmarks_list.count())]
        return homepage, theme, bookmarks

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.page().settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

    def load_url(self, url):
        self.browser.setUrl(QUrl(url))

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Default settings
        self.homepage = "https://www.google.com"
        self.theme = "Light"
        self.bookmarks = []
        self.adblocker_enabled = True  # New attribute for Adblocker
        self.webgl_enabled = True  # New attribute for WebGL

        # Window settings
        self.setWindowTitle("bored browser")
        self.setGeometry(100, 100, 1000, 700)

        # Toolbar
        self.toolbar = QToolBar("Navigation")
        self.addToolBar(self.toolbar)

        # Back Button
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)

        # Forward Button
        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(forward_action)

        # Reload Button
        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(reload_action)

        # Home Button
        home_action = QAction("Home", self)
        home_action.triggered.connect(self.go_home)
        self.toolbar.addAction(home_action)

        # Settings Button
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        self.toolbar.addAction(settings_action)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.url_bar)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Open first tab with homepage
        self.new_tab(self.homepage)

        # Apply initial theme
        self.apply_theme()

    def new_tab(self, url=None):
        tab = BrowserTab()
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        if url:
            tab.load_url(url)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def load_url(self):
        current_tab = self.current_tab()
        if not current_tab:
            return

        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        current_tab.load_url(url)

    def go_back(self):
        current_tab = self.current_tab()
        if current_tab:
            current_tab.browser.back()

    def go_forward(self):
        current_tab = self.current_tab()
        if current_tab:
            current_tab.browser.forward()

    def reload_page(self):
        current_tab = self.current_tab()
        if current_tab:
            current_tab.browser.reload()

    def go_home(self):
        self.new_tab(self.homepage)

    def open_settings(self):
        dialog = SettingsDialog(self, homepage=self.homepage, theme=self.theme, bookmarks=self.bookmarks)
        if dialog.exec_() == QDialog.Accepted:
            self.homepage, self.theme, self.bookmarks = dialog.get_settings()
            self.apply_theme()

    def apply_theme(self):
        if self.theme == "Dark":
            self.setStyleSheet("QMainWindow { background-color: #2b2b2b; color: white; }")
        else:
            self.setStyleSheet("")

    def current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            return self.tabs.widget(current_index)
        return None

    def toggle_adblocker(self):
        self.adblocker_enabled = not self.adblocker_enabled
        # Apply adblocker setting to all tabs
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.browser.page().profile().setHttpAcceptLanguage(
                "en, en-US;q=0.8, *;q=0.5")
            if self.adblocker_enabled:
                tab.browser.page().settings().setAttribute(
                    QWebEngineSettings.PluginsEnabled, False)
            else:
                tab.browser.page().settings().setAttribute(
                    QWebEngineSettings.PluginsEnabled, True)

    def toggle_webgl(self):
        self.webgl_enabled = not self.webgl_enabled
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            tab.browser.page().settings().setAttribute(
                QWebEngineSettings.WebGLEnabled, self.webgl_enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec_())
