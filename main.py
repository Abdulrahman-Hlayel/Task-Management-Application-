import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
    QTextEdit, QCalendarWidget, QListWidget, QMessageBox
)
from PySide6.QtCore import QDate, QTimer
import sqlite3

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_tasks()

    def initUI(self):
        self.setWindowTitle('Task Management Application')
        self.setGeometry(100, 100, 400, 600)

        self.layout = QVBoxLayout()

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText('Task Title')
        self.layout.addWidget(self.title_input)

        self.description_input = QTextEdit(self)
        self.description_input.setPlaceholderText('Task Description')
        self.layout.addWidget(self.description_input)

        self.calendar = QCalendarWidget(self)
        self.layout.addWidget(self.calendar)

        self.priority_input = QLineEdit(self)
        self.priority_input.setPlaceholderText('Priority (High/Medium/Low)')
        self.layout.addWidget(self.priority_input)

        self.add_button = QPushButton('Add Task', self)
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        self.task_list = QListWidget(self)
        self.layout.addWidget(self.task_list)

        self.setLayout(self.layout)

        # Timer for notifications
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_due_dates)
        self.timer.start(60000)  # Check every minute

    def add_task(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        due_date = self.calendar.selectedDate().toString('yyyy-MM-dd')
        priority = self.priority_input.text()

        if title:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)',
                           (title, description, due_date, priority))
            conn.commit()
            conn.close()
            self.load_tasks()
            self.title_input.clear()
            self.description_input.clear()
            self.priority_input.clear()
        else:
            QMessageBox.warning(self, 'Error', 'Task title cannot be empty!')

    def load_tasks(self):
        self.task_list.clear()
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title, due_date FROM tasks WHERE completed = 0')
        tasks = cursor.fetchall()
        for task in tasks:
            self.task_list.addItem(f"{task[0]} (Due: {task[1]})")
        conn.close()

    def check_due_dates(self):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('SELECT title FROM tasks WHERE due_date = ?', (QDate.currentDate().toString('yyyy-MM-dd'),))
        tasks_due_today = cursor.fetchall()
        conn.close()

        if tasks_due_today:
            task_titles = ', '.join([task[0] for task in tasks_due_today])
            QMessageBox.information(self, 'Due Tasks', f'The following tasks are due today: {task_titles}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    task_manager = TaskManager()
    task_manager.show()
    sys.exit(app.exec())