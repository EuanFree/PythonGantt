import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QWidget, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from GanttViewer import GanttViewer, GTask  # Assuming GanttViewer is correctly imported
from datetime import datetime

class GanttApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Project Management Gantt Viewer')
        self.setGeometry(100, 100, 1200, 800)

        self.gantt_viewer = GanttViewer(figsize=(10, 6))
        self.populate_initial_tasks()

        # Main Layout
        main_layout = QHBoxLayout()

        # Task Editor Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(['Task Name', 'Start Date', 'End Date'])
        self.populate_task_table()
        main_layout.addWidget(self.task_table)

        # Button Layout
        button_layout = QVBoxLayout()
        update_button = QPushButton('Update Gantt Chart')
        update_button.clicked.connect(self.update_gantt_chart)
        button_layout.addWidget(update_button)

        add_task_button = QPushButton('Add New Task')
        add_task_button.clicked.connect(self.add_new_task)
        button_layout.addWidget(add_task_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Gantt Chart Layout
        self.chart_layout = QVBoxLayout()
        main_layout.addLayout(self.chart_layout)
        self.draw_gantt_chart()

        self.setLayout(main_layout)

    def populate_initial_tasks(self):
        # Populate GanttViewer with example tasks
        self.gantt_viewer.add_task(GTask('Task A', '2024-11-01', '2024-11-10'))
        self.gantt_viewer.add_task(GTask('Task B', '2024-11-05', '2024-11-15'))
        self.gantt_viewer.add_task(GTask('Task C', '2024-11-12', '2024-11-20'))

    def populate_task_table(self):
        self.task_table.setRowCount(len(self.gantt_viewer.tasks))
        for row, task in enumerate(self.gantt_viewer.tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(task.name))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.start.strftime('%Y-%m-%d')))
            self.task_table.setItem(row, 2, QTableWidgetItem(task.end.strftime('%Y-%m-%d')))

    def update_gantt_chart(self):
        # Clear existing tasks and add updated ones
        self.gantt_viewer.tasks = []
        for row in range(self.task_table.rowCount()):
            task_name = self.task_table.item(row, 0).text()
            start_date = self.task_table.item(row, 1).text()
            end_date = self.task_table.item(row, 2).text()
            self.gantt_viewer.add_task(GTask(task_name, start_date, end_date))
        self.draw_gantt_chart()

    def add_new_task(self):
        row_position = self.task_table.rowCount()
        self.task_table.insertRow(row_position)
        self.task_table.setItem(row_position, 0, QTableWidgetItem('New Task'))
        self.task_table.setItem(row_position, 1, QTableWidgetItem('2024-11-25'))
        self.task_table.setItem(row_position, 2, QTableWidgetItem('2024-12-05'))

    def draw_gantt_chart(self):
        # Clear previous chart
        while self.chart_layout.count():
            child = self.chart_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Use GanttViewer to create the figure
        fig = self.gantt_viewer.fig
        self.gantt_viewer.draw()

        # Add the figure to the canvas
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GanttApp()
    window.show()
    sys.exit(app.exec_())
