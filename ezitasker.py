import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QDialog, QTextEdit, QMessageBox
from PyQt5.QtCore import QTime, QTimer, Qt, QSignalBlocker, QDate, QPoint
from PyQt5.QtGui import QIcon,QPixmap
import requests
import json
import urllib3
import contextlib
from contextlib import suppress
import warnings
import threading
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import threading
import time
import re
import dropbox
import mysql.connector
from datetime import datetime
import pyautogui
import io
# from dropbox.files import WriteMode

access_token = "bJoFnHX6gFAAAAAAAAHgbKZOVmUfutbYrQsqEJ1hbzwKIRxHv7mejju9OB48xBMa"
# db_config = {
# 'host':'localhost',
# 'port':'3307',
# 'user':'root',
# 'password':'',
# 'database':'ezitasker'       
# }

db_config = {
        'host': '209.124.66.28',  
        'port': '3306',
        'user': 'eziline_taskerusr',
        'password': 'YXHx3lD2HV=i',
        'database': 'eziline_tasker'
}
# user_id=None
def get_db_connection():
        return mysql.connector.connect(**db_config)
    

class suppress_warnings(contextlib.ContextDecorator):

    def __enter__(self):
        self.original_filters = warnings.filters[:]
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        warnings.filters = self.original_filters

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 600, 400)  # Smaller window size
        self.setWindowFlags(Qt.FramelessWindowHint)
                
        gradient = 'qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1B1B1C, stop: 1 #38383A);'
        self.setStyleSheet(f"""background: {gradient} color: white; font-weight: bold;
                           border-radius: 10px;""")

        # self.setStyleSheet("""
        #     background: #1B1B1C;
        #     color: white;
        #     font-weight: bold;
        #     border-radius: 10px;
        # """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        self.login_label = QLabel('Member Login',self)
        self.login_label.setStyleSheet(f"""font-family: Poppins-Medium;
                                font-size: 35px;
                                line-height: 1.5;
                                color: #666666;
                                width: 100%;
                                background: {gradient};
                                height: 50px;
                                border-radius: 10px;
                                padding: 0 30px 0 20px;
                                """)
        layout.addWidget(self.login_label, alignment=Qt.AlignCenter)
        
        # Create a QLabel and set the pixmap (image) as its content
        self.image_pixmap = QPixmap("icons\\img-01.png")
        self.image_label = QLabel()
        self.image_label.setPixmap(self.image_pixmap)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Create input fields
        self.input1 = QLineEdit()
        self.input1.setStyleSheet("""font-family: Poppins-Medium;
                                        font-size: 15px;
                                        line-height: 1.5;
                                        color: #666666;
                                        width: 100%;
                                        background: #e6e6e6;
                                        height: 50px;
                                        border-radius: 10px;
                                        padding: 0 30px 0 20px;
                                        """)
        self.input1.setPlaceholderText("Email")
        layout.addWidget(self.input1)

        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.Password)  # Set echo mode to Password
        self.input2.setStyleSheet("""font-family: Poppins-Medium;
                                    font-size: 15px;
                                    line-height: 1.5;
                                    color: #666666;
                                    width: 100%;
                                    background: #e6e6e6;
                                    height: 50px;
                                    border-radius: 10px;
                                    padding: 0 30px 0 20px;
                                    """)
        self.input2.setPlaceholderText("Password")
        layout.addWidget(self.input2)

        # Create button
        self.button = QPushButton("Login")
        self.button.setStyleSheet(f"""
                                background : #38383A;
                                font-family: Montserrat-Bold;
                                font-size: 35px;
                                line-height: 1.5;
                                color: #8D9191;
                                text-transform: uppercase;
                                width: 20%;
                                border-radius: 10px;
                                padding: 0 25px;
                                """)
        self.button.clicked.connect(self.login)
        layout.addWidget(self.button)

        central_widget.setLayout(layout)

    def login(self):
        email = self.input1.text()
        password = self.input2.text()
        with suppress(Exception):  # This will catch any exception raised within the block
            token_or_error,user_id,user_name = self.login_post_api(email, password)
            
            # print(token_or_error,user_id,user_name)
            if token_or_error is None:  # If login_post_api didn't return a valid token
                QMessageBox.warning(self, "Login Failed", "Invalid email or password. Please try again.")
                print("Login unsuccessful!")
            else:  # If login_post_api returned a token
                token = token_or_error
                self.project_window = ProjectWindow(token,user_id,user_name)
                self.project_window.show()
                self.close()

    def login_post_api(self, email, password):
        login_url = f'https://ezitasker.com/api/v1/auth/login?email={email}&password={password}'
        try:
            response = requests.post(login_url, verify=False)
            data = json.loads(response.text)
            if response.status_code == 200:  # Login Successfully
                token = data["data"]["token"]
                user_info = data["data"]["user"]
                user_id = user_info["id"]
                user_name = user_info["name"]
                conn = get_db_connection()
                cursor = conn.cursor()
                query1 = "SELECT Employee_ID FROM employee"
                
                cursor.execute(query1)
                
                results = cursor.fetchall()
                # print(results)
                
                # Extract the existing employee IDs from the results
                existing_employee_ids = [result[0] for result in results]
                # print(existing_employee_ids)
                if user_id not in existing_employee_ids:
                    query = 'INSERT INTO employee(Employee_ID, Employee_Name) VALUES (%s, %s)'
                    cursor.execute(query, (user_id, user_name))
                    conn.commit()  # Don't forget to commit the changes to the database
                    print("New employee inserted.")
                else:
                    print("Old employee.")

                conn.commit()
                conn.close()
                return token,user_id,user_name
            
            else:
                issue = json.loads(response.text)
                error = issue["message"]
                if error == 'Request could not be validated':  # Password must be at least 6 characters
                    error = issue["error"]["details"]
                # Return None for unsuccessful login
                return None
        except requests.exceptions.RequestException as e:
            print('Error:', e)
        # Return None for unsuccessful login
            return None

class TimeLogDialog(QDialog):
    def __init__(self, time_log_text):
        super().__init__()
        self.setWindowTitle("Time Log History")
        self.setGeometry(300, 300, 500, 300)

        self.time_log_text = time_log_text

        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(self.time_log_text)
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        
        
class TimeLogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Log History")
        self.setGeometry(300, 300, 500, 300)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)        
        
        
    def update_time_log(self, time_log_text):
        self.text_edit.setPlainText(time_log_text)

class ProjectWindow(QMainWindow):
    def __init__(self, token,user_id,user_name):
        super().__init__()
        # self.setWindowTitle("Ezitasker - Projects and Tasks")
        # # Create a QIcon object with your icon file path
        icon = QIcon("app.ico")
        self.setWindowIcon(icon)
        # Set window flags to remove the title bar and stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(300, 300, 600, 60)
        # gradient = 'qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3498db, stop: 1 #FFFFFF);'
        # gradient = 'qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1e6dab, stop: 1 #5C5E5E);'
        gradient = 'qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1B1B1C, stop: 1 #38383A);'
        self.setStyleSheet(f'background: {gradient} color: white; font-weight: bold;')
        self.token = token
        self.user_id = user_id
        self.user_name = user_name
        self.selected_project_id = None
        self.selected_task_id = None
        self.selected_task = None
        self.time_list = []
        self.total_time = QTime(0, 0, 0)
        self.date = QDate.currentDate()
        # self.elapsed_time = QTime(0, 0, 0)
        self.access_token = "bJoFnHX6gFAAAAAAAAHgbKZOVmUfutbYrQsqEJ1hbzwKIRxHv7mejju9OB48xBMa"
        self.pause_flag = False  # Flag to indicate whether to pause activity detection
        self.screen_shot_flag = False # Flag to indicate whether to screenshot should be taken detection
        self.is_timer_running = False
        self.time_log_id = None
        self.time_log = ""
        self.pause_time = None  # Track pause time
        self.flag = True
        # Create a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        # self.count = 0
        # Fetch the project names and IDs from the API
        self.projects = self.get_projects()
        
        # Create a dropdown list for projects using QComboBox
        self.project_dropdown = QComboBox(self)
        self.project_dropdown.addItem("Select Project")
        self.project_dropdown.setStyleSheet("background-color: transparent; border: None;")
        # 300, 300, 600, 100
        self.project_dropdown.addItems([project[1] for project in self.projects])
        self.project_dropdown.currentIndexChanged.connect(self.on_project_selected)

        # Create a dropdown list for tasks using QComboBox
        self.task_dropdown = QComboBox(self)
        # self.task_dropdown.setGeometry(120, 150, 750, 500)  # Initial geometry
        self.task_dropdown.addItem("Select Task")
        self.task_dropdown.setStyleSheet("background-color: transparent; border: None;")
        self.task_dropdown.setEnabled(False)
        # self.project_dropdown.addItems([project[1] for project in self.projects])

        self.task_dropdown.currentIndexChanged.connect(self.on_task_selected)

        # Create labels for time tracking
        self.time_label = QLabel("00:00:00", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("background-color: #ffffff; border: 5px; color: #666666;")
        self.time_label.setVisible(False)  # Hide the timer label initially

        # Create buttons
        self.start_button = QPushButton("Start",self)
        self.start_button.setEnabled(False)
        self.Start_icon = QIcon("icons\\start-96.png")
        self.start_button.setIcon(self.Start_icon)
        self.start_button.setStyleSheet("background-color: transparent; border: 10px;")
        self.start_button.clicked.connect(self.start_timer)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setEnabled(False)
        self.pause_icon = QIcon("icons\\pause-96.png")
        self.pause_button.setIcon(self.pause_icon)
        self.pause_button.setStyleSheet("background-color: transparent; border: 10px;")
        self.pause_button.clicked.connect(self.pause_timer)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setEnabled(False)
        self.stop_icon = QIcon("icons\\stop-96.png")
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setStyleSheet("background-color: transparent; border: 10px;")
        self.stop_button.clicked.connect(self.stop_timer)

        # Create a time log widget
        self.time_log_widget = TimeLogWidget()
        self.time_log_widget.hide()

        # Create a layout to organize the widgets
        layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(self.project_dropdown)
        layout1.addWidget(self.task_dropdown)
        layout.addLayout(layout1)
        # layout.addWidget(self.move_button)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.start_button)
        time_layout.addWidget(self.pause_button)
        time_layout.addWidget(self.stop_button)
        layout.addLayout(time_layout)

        # layout.addWidget(self.time_log_table)
        # Create a layout to organize the widgets
                # Create a widget to display the layout
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Create a button for moving the window
        self.move_button = QPushButton(self)
        self.move_button.setGeometry(self.width() - 60, 60, 200, 200)
        
        
        # Create a QIcon object with your icon file path
        icon = QIcon("icons\\drag-96.png")
        # D:\Ezitasker\icons\drag-96.png
        # Set the QIcon for the button
        
        self.move_button.setIcon(icon)
        
        # Remove background and border
        self.move_button.setStyleSheet("background-color: transparent; border: none;")
        # self.button.setStyleSheet("""
                                
        #                         font-family: Montserrat-Bold;
        #                         font-size: 15px;
        #                         line-height: 1.5;
        #                         color: #fff;
        #                         text-transform: uppercase;
        #                         width: 100%;
        #                         border-radius: 10px;
        #                         background: transparent;
        #                         padding: 0 25px;
        #                         """)
        
        self.move_button.clicked.connect(self.enable_move)
        
        # Initialize variables for dragging
        self.dragging = False
        self.offset = QPoint()
        
        layout_btn = QHBoxLayout()
        layout_btn.addWidget(self.move_button)
        layout1.addLayout(layout_btn)
        
    def enable_move(self):
        # Enable dragging when the button is clicked
        self.dragging = True
        self.offset = self.move_button.pos()
        
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToGlobal(event.pos() - self.offset)
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def get_projects(self):
        url = "https://ezitasker.com/api/v1/project"
        # Define query parameters for the initial request
        params = {
            'fields': 'id,project_name',
            'limit': 100,  # Number of projects per page
            'offset': 0   # Start from the beginning
        }
        headers = {'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                    }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if response.status_code == 200 and 'data' in data:
            projects = [(project['id'], project['project_name']) for project in data['data']]
            return projects
        else:
            return []

    def get_tasks_by_project(self, project_id):
        url = f"https://ezitasker.com/api/v1/project/{project_id}/tasks"
        headers = {'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                    }
        params = {
            'limit': 100,  # Number of projects per page
            'offset': 0   # Start from the beginning
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        # print(data)
        if response.status_code == 200 and 'data' in data:
            task_id = [task['id'] for task in data['data']]
            tasks = [task['heading'] for task in data['data']]
            # print(task_id)
            return tasks,task_id
        else:
            return []

    def on_project_selected(self, index):
        blocker = QSignalBlocker(self.project_dropdown)

        if index == 0:
            self.task_dropdown.clear()
            self.task_dropdown.addItem("Select Task")
            self.task_dropdown.setEnabled(False)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.selected_project_id = None
            self.selected_task = None
        else:
            selected_project_id = self.projects[index - 1][0]
            if selected_project_id:
                if selected_project_id != self.selected_project_id:
                    self.total_time = QTime(0, 0, 0)
                    self.selected_task = None

                self.selected_project_id = selected_project_id
                tasks, task_id = self.get_tasks_by_project(selected_project_id)
                self.task_dropdown.clear()
                self.task_dropdown.addItem("Select Task")
                self.task_dropdown.addItems(tasks)
                self.task_dropdown.setEnabled(True)
                self.start_button.setEnabled(False)
                self.pause_button.setEnabled(False)
                self.stop_button.setEnabled(False)

    def on_task_selected(self, index):
        if index == 0:
            # Placeholder text for task dropdown
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.selected_task = None
            self.selected_task_id = None
        else:
            self.tasks,self.task_id = self.get_tasks_by_project(self.selected_project_id)
            # print(self.task_id)
            selected_task_id = self.task_id[index - 1]
            if selected_task_id:
                if selected_task_id != self.selected_task_id:
                    self.total_time = QTime(0, 0, 0)
                    self.selected_task = None

                self.selected_task_id = selected_task_id
            selected_task = self.task_dropdown.currentText()
            # print(selected_task_id)
            if selected_task:
                self.selected_task = selected_task
                print(selected_task)
                self.start_button.setEnabled(True)
                #task_id handle





    def on_timelog_start(self):
        project_id = self.selected_project_id
        task_id = self.selected_task_id
        memo = "Logged By Ezitasker Desktop"
        auth_token = self.token
        # print(auth_token)
        # Define the API endpoint
        url = "https://ezitasker.com/api/v1/timelog"
        
        # Create a dictionary with the form-data arguments
        data = {
            "project[id]": str(project_id),
            "task[id]": str(self.selected_task_id),
            "memo" : memo #"#Task"+str(self.selected_task_id)
        }
        headers = {'Authorization': f'Bearer {auth_token}'}

        # Send the POST request
        response = requests.post(url, data=data,headers=headers)

        # Check the response
        if response.status_code == 200:
            print("Request was successful.")
            # You can also print the response content if needed
            # Parse the JSON response
            response_json = response.json()
            
            # Extract and print the "message" and "data" fields
            message = response_json.get("message")
            data = response_json.get("data")
            
            print(f"Message: {message}")
            self.time_log_id = data.get("id")
            # print(f"ID: {self.time_log_id}")
            
            return self.time_log_id
        else:
            # print(f"Request failed with status code {response.status_code}.")
            # print(f"Request failed with content {response.content}.")
            content = response.content
            return content


    def start_timer(self):
        start_id = self.on_timelog_start()
        # print(start_id)
        # print(type(start_id))
        # if :
        if self.selected_task and not self.is_timer_running and isinstance(start_id, int):
            self.is_timer_running = True
            self.pause_flag = False
            self.screen_shot_flag = False
            mouse_thread = threading.Thread(target=self.start_mouse_detection_thread)
            mouse_thread.daemon = True
            mouse_thread.start()

            screenshot_thread = threading.Thread(target=self.save_screenshot_to_folder)
            screenshot_thread.daemon = True
            screenshot_thread.start()
            # if self.is_timer_running == True:
            
            #     print('SCREENSHOT')
            #     print('mouse detection')
                # Start the mouse detection thread here


            if self.total_time == QTime(0, 0, 0):
                # Only update the session_start_time if it's the first time starting the timer
                self.session_start_time = QTime.currentTime()
                self.time_log += f"Task: {self.selected_task}\n"
                
                # self.time_log += f"Paused at: {self.pause_time.toString('hh:mm:ss')}\n"
            else:
                # If resuming from pause, calculate the elapsed time since pause_time
                if self.pause_time is not None:
                    elapsed_time = self.pause_time.msecsTo(QTime.currentTime())
                    self.session_start_time = self.session_start_time.addMSecs(elapsed_time)
                    self.pause_time = None  # Reset pause time
                    
            self.time_log += f"Start Time: {self.session_start_time.toString('hh:mm:ss')}\n"
            self.timer.start(1000)
            self.time_label.setVisible(True)  # Show the timer label
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.project_dropdown.setEnabled(False)
            self.task_dropdown.setEnabled(False)
            # Disable task selection while the timer is running
            # if self.is_timer_running:
                # self.mousedetect
        else:
            print(start_id)


    def on_timelog_stop(self):
        time_log_id = self.time_log_id
        # task_id = self.selected_task_id
        # memo = task_id
        auth_token = self.token
        # print(auth_token)
        # Define the API endpoint
        # url = "https://ezitasker.com/api/v1/timelog"
        url = f"https://ezitasker.com/api/v1/timelog/{time_log_id}"
        
        # Create a dictionary with the form-data arguments
        # data = {
        #     "project[id]": str(project_id),
        #     "task[id]": str(self.selected_task_id),
        #     "memo" : "#Task"+str(self.selected_task_id)
        # }
        headers = {'Authorization': f'Bearer {auth_token}'}

        # Send the POST request
        response = requests.put(url,headers=headers)

        # Check the response
        if response.status_code == 200:
            print("Request was successful.")
            # You can also print the response content if needed
            # Parse the JSON response
            response_json = response.json()
            
            # Extract and print the "message" and "data" fields
            message = response_json.get("message")
            data = response_json.get("data")
            
            print(f"Data: {data}")
            
            print(f"Message: {message}")
            # self.time_log_id = data.get("id")
            # print(f"ID: {self.time_log_id}")
            
            # return self.time_log_id
        else:
            # print(f"Request failed with status code {response.status_code}.")
            print(f"Request failed with content {response.content}.")
            content = response.content
            return content

    def pause_timer(self):
        self.on_timelog_stop()
        if self.is_timer_running:
            self.is_timer_running = False
            self.pause_flag = True
            self.screen_shot_flag = True
            # if self.is_timer_running == False:
            #     print('NO SCREENSHOTS')
            self.pause_time = QTime.currentTime()
            elapsed_time = self.session_start_time.msecsTo(self.pause_time)
            self.total_time = self.total_time.addMSecs(elapsed_time)
            self.time_log += f"Paused at: {self.pause_time.toString('hh:mm:ss')}\n"
            
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)  # Re-enable the stop button when the timer is paused
            
            # print(self.format_duration(self.total_time.msecsSinceStartOfDay()))
            # print(self.total_time.msecsTo())
            elapsed_time1 = self.format_duration(elapsed_time)
            # ----------------------------------------------------------------
            # self.post_to_db(elapsed_time1,self.time_log) #posting data to db function
            self.time_list.append(elapsed_time1)
            # print(self.time_list)
            index = len(self.time_list)
            if index == 1:
                self.post_to_db(elapsed_time1,self.time_log) #posting data to db function
            else:
                time_to_db = self.subtract_pause_time(self.time_list)
                # print(time_to_db)
                self.post_to_db(time_to_db,self.time_log)
                # last_pause = self.time_list[index-1] + self.time_list[index-2]
                # print(last_pause)
            # elapsed_time = 0
            
            # print(self.format_duration(elapsed_time),self.time_log)
        else:
            # Timer is paused, user clicked the pause button again, resume the timer
            self.is_timer_running = True
            # if self.is_timer_running == True:
            #     print('SCREENSHOT')
            #     print('mouse detection')
            if self.total_time == QTime(0, 0, 0):
                # Only update the session_start_time if it's the first time resuming the timer
                self.session_start_time = QTime.currentTime()
            else:
                # If resuming from pause, update the session_start_time with the elapsed time
                elapsed_time = self.pause_time.msecsTo(QTime.currentTime())
                self.session_start_time = self.session_start_time.addMSecs(elapsed_time)
            
            self.timer.start(1000)
            self.time_label.setVisible(True)  # Show the timer label
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    # def show_warning_messagebox(self):
    #     msg = QMessageBox()
    #     msg.setIcon(QMessageBox.Warning)

    #     # setting message for Message Box
    #     msg.setText("Are You Working? Your Timer is Paused Kindly Check!")
        
    #     # setting Message box window title
    #     msg.setWindowTitle("Idle Warning")
        
    #     # declaring buttons on Message Box
    #     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
    #     # # start the app
    #     retval = msg.exec_()


    
    def start_mouse_detection_thread(self):
    # Global variables to track activity
        global last_activity_time
        last_activity_time = time.time()
        activity_lock = threading.Lock()

        def on_mouse_move(x, y):
            global last_activity_time
            # print(x, y)
            with activity_lock:
                last_activity_time = time.time()

        def on_key_press(key):
            global last_activity_time
            with activity_lock:
                # print(key)
                last_activity_time = time.time()

        def check_activity():
            threshold_time = 600
            while not self.pause_flag:
                with activity_lock:
                    if time.time() - last_activity_time > threshold_time:
                        print('User idle - pausing timer')
                        self.pause_timer()  # Pause the timer when user is idle

                        # self.show_warning_messagebox()
                        # QMessageBox.warning(self, "Login Failed", "Invalid email or password. Please try again.")
                        # warning_thread = threading.Thread(target =self.show_warning_messagebox)  # Show the message box
                        # warning_thread.daemon = True
                        # warning_thread.start()
                        break
                time.sleep(1)
                
        # Start the activity checking thread
        activity_thread = threading.Thread(target=check_activity)
        activity_thread.daemon = True
        activity_thread.start()
        
        # Start listening to mouse and keyboard events
        mouse_listener = MouseListener(on_move=on_mouse_move)
        keyboard_listener = KeyboardListener(on_press=on_key_press)
        with mouse_listener, keyboard_listener:
            activity_thread.join()   # Wait for the activity thread to finish (which it won't)

    def stop_timer(self):
        if self.is_timer_running or self.pause_time is not None:
            # If the timer is running or paused, stop it and reset the time
            self.is_timer_running = False
            current_time = QTime.currentTime()
            
            # if self.is_timer_running == False:
            #     print('NO SCREENSHOTS')
            self.time_log += f"Stopped at: {QTime.currentTime().toString('hh:mm:ss')}\n"
            self.timer.stop()
            
            if self.pause_time is not None:
                # If the timer was paused, use the time elapsed until the last pause
                elapsed_time = self.pause_time.msecsTo(QTime.currentTime())
                self.total_time = self.total_time.addMSecs(elapsed_time)
                self.pause_time = None  # Reset pause time
            else:
                # If the timer was not paused, calculate the elapsed time from session_start_time
                current_time = QTime.currentTime()
                elapsed_time = self.session_start_time.msecsTo(current_time)
                self.total_time = self.total_time.addMSecs(elapsed_time)
            self.time_label.setText(self.format_duration(self.total_time.msecsSinceStartOfDay()))
            self.time_label.setVisible(True)  # Show the timer label

            # Reset timer variables and enable the start button
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.project_dropdown.setEnabled(True)  # Enable project selection after timer stops
            self.task_dropdown.setEnabled(True)  # Enable task selection after timer stops
            self.selected_task = None
            self.time_log += f"Total Duration: {self.format_duration(self.total_time.msecsSinceStartOfDay())}\n\n"
            # Reset timer variables to allow starting the timer again
            self.total_time = QTime(0, 0, 0)
            self.session_start_time = None
            self.pause_time = None
            
            # Clear the timer label text when the timer is stopped
            self.time_label.setText("00:00:00")
            self.time_list = []
            
    def create_folder_if_not_exists(self, dbx, folder_path):
        try:
            metadata = dbx.files_get_metadata(folder_path)
        except dropbox.exceptions.ApiError as e:
            if e.user_message_text and e.user_message_text.startswith("path/not_found"):
                # Folder doesn't exist, create it
                dbx.files_create_folder_v2(folder_path)
            else:
                # Handle other API errors here
                print(f"Error: {e}")

    def save_screenshot_to_folder(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'SELECT Employee_ID, time_for_ss  FROM `screenshot_time_set`;'
        cursor.execute(query)
        user_id = self.user_id 
        results = cursor.fetchall()
        # print(results)
        for ids in results:
            if user_id == ids[0]:
                time_set = ids[1]
                break
            else:
                time_set = 60
        # print(time_set)
        
        
        dbx = dropbox.Dropbox(self.access_token)
        # Define the Dropbox folder path and file name
        task_name = self.selected_task
        # print(task_name)
        for proj_pid, proj_name in self.projects:
            if proj_pid == self.selected_project_id:
                project_name = proj_name
        date = self.get_date(self.date)
        date_today = str(date)
        user_name = self.user_name
        
        folder_path = f'/ezitasker/{user_name}/{date_today}/{project_name}'
        # print(folder_path)
        
        # Create the folder if it doesn't exist
        self.create_folder_if_not_exists(dbx, folder_path)
        
        while not self.screen_shot_flag:
            # Take a screenshot
            screenshot = pyautogui.screenshot()
            time_now = time.time()
            # Convert the timestamp to a datetime object
            datetime_now = datetime.fromtimestamp(time_now)
            
            # Format the datetime object as 'hh:mm:ss'
            formatted_time = datetime_now.strftime('%H:%M:%S')
            
            file_name = f'{task_name}_{formatted_time}.png'
            
            # Convert the screenshot to bytes
            screenshot_bytes = io.BytesIO()
            screenshot.save(screenshot_bytes,format='PNG')
            screenshot_bytes.seek(0)
            file_path = f'{folder_path}/{file_name}'
            
            # Upload the screenshot directly to Dropbox
            dbx.files_upload(screenshot_bytes.read(),file_path)
            time.sleep(time_set)

    def subtract_pause_time(self,time_list):
            # Convert time strings to datetime objects
            index = len(time_list)
            time_format = "%H:%M:%S"
            time_objects = [datetime.strptime(time_str, time_format) for time_str in time_list]
            
            # Calculate time differences
            time_difference_1 = time_objects[index-1] - time_objects[index-2]
            return time_difference_1
        
    def update_time(self):
        if self.is_timer_running:
            current_time = QTime.currentTime()
            elapsed_time = self.session_start_time.msecsTo(current_time)
            self.time_label.setText(self.format_duration(elapsed_time))

    def format_duration(self, time_milliseconds):
        if time_milliseconds < 0:
            time_milliseconds = 0

        seconds, milliseconds = divmod(time_milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def show_time_log_history(self):
        time_log_dialog = TimeLogDialog(self.time_log)
        time_log_dialog.exec_()

    def get_date(self,date):
        return date.toString('yyyy-MM-dd')

    def post_to_db(self,elapsed_time,logs):
            user_id = self.user_id
            user_name = self.user_name
            time_to_db = elapsed_time
            project_id_to_db = self.selected_project_id
            for proj_pid, proj_name in self.projects:
                if proj_pid == self.selected_project_id:
                    project_to_db = proj_name
            task_pattern = re.compile(r'^(.*?)(?=\n)', re.MULTILINE)
            tasks = task_pattern.findall(logs)
            task_to_db = tasks[0]
            date = self.get_date(self.date)
            date_to_db = date
            self.insert_function(user_id,project_id_to_db, project_to_db, task_to_db, date_to_db,time_to_db)

    def insert_function(self, user_id, project_id_to_db, project_to_db, task_to_db, date_to_db, time_to_db):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = 'INSERT INTO timer(Employee_ID, Project_ID, Project_Name, Task_Name, Dated, Time) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (user_id, project_id_to_db, project_to_db, task_to_db, date_to_db, time_to_db))
        
        conn.commit()
        cursor.close()
        conn.close()
        return "done"


if __name__ == "__main__":

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())