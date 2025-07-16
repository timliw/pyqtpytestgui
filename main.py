import sys
import json
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QSplitter,
    QDialog, QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
)
from PyQt5.QtCore import QProcess, pyqtSignal, Qt, QTimer, QProcessEnvironment

class TestRunner(QProcess):
    test_finished = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.log = ""
        self.setProcessChannelMode(QProcess.MergedChannels)
        self.readyReadStandardOutput.connect(self.on_ready_read_standard_output)
        self.finished.connect(self.on_finished)

    def run_test(self, pytest_name, parameters):
        self.log = ""
        env = QProcessEnvironment.systemEnvironment()
        if isinstance(parameters, dict):
            for key, value in parameters.items():
                env.insert(key.upper(), str(value))
        self.setProcessEnvironment(env)
        command = [sys.executable, "-m", "pytest", pytest_name]
        self.start(command[0], command[1:])

    def on_ready_read_standard_output(self):
        self.log += self.readAllStandardOutput().data().decode()

    def on_finished(self, exit_code, exit_status):
        outcome = "passed" if exit_code == 0 else "failed"
        self.test_finished.emit(outcome, self.log)

class LogDialog(QDialog):
    def __init__(self, log_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test Log")
        self.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout(self)
        log_view = QTextEdit(self)
        log_view.setReadOnly(True)
        log_view.setText(log_text)
        layout.addWidget(log_view)

class TestWidgetItem(QWidget):
    def __init__(self, test_item, parent_app):
        super().__init__()
        self.test_item = test_item
        self.parent_app = parent_app
        self.log = ""
        self.test_runner = TestRunner(self)
        self.test_runner.test_finished.connect(self.on_test_finished)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.name_label = QLabel(test_item["label"])
        layout.addWidget(self.name_label)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_test)
        layout.addWidget(self.run_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        self.status_label = QLabel("Untested")
        layout.addWidget(self.status_label)

        self.timer_label = QLabel("0s")
        layout.addWidget(self.timer_label)

        self.log_button = QPushButton("Log")
        self.log_button.clicked.connect(self.show_log)
        self.log_button.setEnabled(False)
        layout.addWidget(self.log_button)

    def run_test(self):
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Running")
        self.elapsed_time = 0
        self.timer.start(1000)
        self.test_runner.run_test(self.test_item["pytest_name"], self.test_item.get("parameters", {}))

    def stop_test(self):
        self.test_runner.kill()
        self.timer.stop()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Stopped")

    def on_test_finished(self, outcome, log):
        self.log = log
        self.timer.stop()
        self.status_label.setText(outcome)
        if outcome == "passed":
            self.status_label.setStyleSheet("color: green")
        else:
            self.status_label.setStyleSheet("color: red")
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_button.setEnabled(True)
        self.parent_app.log_view.append(log)

    def show_log(self):
        dialog = LogDialog(self.log, self.parent_app)
        dialog.exec_()

    def update_timer(self):
        self.elapsed_time += 1
        self.timer_label.setText(f"{self.elapsed_time}s")

class TestRunnerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pytest Runner")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.test_tree_view = QTreeWidget()
        self.test_tree_view.setHeaderHidden(True)
        self.left_layout.addWidget(self.test_tree_view)

        self.progress_bar = QProgressBar(self)
        self.left_layout.addWidget(self.progress_bar)

        all_controls_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.run_all_tests)
        all_controls_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_all_tests)
        self.stop_button.setEnabled(False)
        all_controls_layout.addWidget(self.stop_button)
        self.left_layout.addLayout(all_controls_layout)

        self.splitter.addWidget(self.left_panel)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        
        self.right_layout.addWidget(self.log_view)
        self.splitter.addWidget(self.right_panel)
        
        self.splitter.setSizes([400, 800])

        self.load_tests()
        self.current_test_widget = None
        self.is_running_all = False

    def load_tests(self):
        try:
            with open("test_data.json", "r") as f:
                data = json.load(f)
                self.tests = data["tests"]
        except FileNotFoundError:
            self.tests = []
        
        self.test_tree_view.clear()
        self.populate_test_tree(self.tests, self.test_tree_view)
        self.flat_tests = self.flatten_tests(self.tests)
        self.progress_bar.setMaximum(len(self.flat_tests))

    def flatten_tests(self, tests):
        flat_list = []
        for test in tests:
            if test["type"] == "group":
                flat_list.extend(self.flatten_tests(test["items"]))
            else:
                flat_list.append(test)
        return flat_list

    def populate_test_tree(self, tests, parent_item):
        for test in tests:
            item = QTreeWidgetItem(parent_item)
            if test["type"] == "group":
                item.setText(0, test["label"])
                self.populate_test_tree(test["items"], item)
            else:
                widget = TestWidgetItem(test, self)
                self.test_tree_view.setItemWidget(item, 0, widget)

    def run_all_tests(self):
        self.is_running_all = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.run_next_test()

    def run_next_test(self):
        if self.progress_bar.value() == len(self.flat_tests):
            self.on_all_tests_finished()
            return

        if self.is_running_all:
            widget = self.find_widget(self.flat_tests[self.progress_bar.value()])
            if widget:
                self.current_test_widget = widget
                widget.test_runner.test_finished.connect(self.on_test_run_finished)
                widget.run_test()

    def on_test_run_finished(self, outcome, log):
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        if self.is_running_all:
            self.run_next_test()

    def stop_all_tests(self):
        self.is_running_all = False
        if self.current_test_widget:
            self.current_test_widget.stop_test()
        self.on_all_tests_finished()

    def on_all_tests_finished(self):
        self.is_running_all = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.current_test_widget = None

    def find_widget(self, test_item):
        iterator = QTreeWidgetItemIterator(self.test_tree_view)
        while iterator.value():
            item = iterator.value()
            widget = self.test_tree_view.itemWidget(item, 0)
            if widget and widget.test_item == test_item:
                return widget
            iterator += 1
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = TestRunnerApp()
    main_win.show()
    sys.exit(app.exec_())