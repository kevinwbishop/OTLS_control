# pip install -U pyinstaller
# pip install PyQt5

import json
from laser_control import Laser
from daq_control import Daq
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDoubleSpinBox, QGridLayout, QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QAction)
from PyQt5.QtCore import Qt
import hardware.fw102c as fw102c


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OTLS Preview")

        # Load and define parameters
        with open('static_params.json', 'r') as read_file:
            self.static_params = json.load(read_file)
        self.laser_dict = self.static_params['laser']
        self.wheel_dict = self.static_params['wheel']
        self.min_currents = self.laser_dict['min_currents']
        self.max_currents = self.laser_dict['max_currents']
        self.ymax = 1.8000
        self.eoffset = 0.9000
        self.current_405 = self.min_currents['405'] # replicate this for other lasers
        self.current_488 = self.min_currents['488']
        self.current_561 = self.min_currents['561']
        self.current_638 = self.min_currents['638']

        # Load laser currents and powers (as measured with power meter)
        with open('power_current.json', 'r') as read_file:
            self.power_current = json.load(read_file)

        # Initialize the Laser
        self.laser = Laser(self.laser_dict)

        # Initialize the Daq
        self.daq = Daq(self.ymax, self.eoffset)
        self.daq.create_voltages_daq()
        self.daq.create_voltages_etl()
        self.daq.create_voltages_galvo()
        self.daq.create_voltages_lasers()
        self.daq.create_ao_channels()

        # Initialize the filter
        self.fWheel = fw102c.FW102C(baudrate=self.wheel_dict["rate"], port=self.wheel_dict["port"])
        print("Filter Initialized!")

        # Create layout for the UI
        layout = QGridLayout()

        # quit event
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

########### 405nm laser ###########
        self.label_405 = QLabel()
        self.label_405.setStyleSheet("border: 1px solid; border-color: purple")
        layout.addWidget(self.label_405, 0,0)

        self.on_button_405 = QPushButton("Turn on 405 nm laser!")
        self.button_is_checked_405 = True
        self.on_button_405.setChecked(self.button_is_checked_405)
        self.on_button_405.clicked.connect(self.the_on_button_was_clicked_405)
        layout.addWidget(self.on_button_405, 1,0)

        self.off_button_405 = QPushButton("Turn off 405 nm laser!")
        self.off_button_405.clicked.connect(self.the_off_button_was_clicked_405)
        self.off_button_405.setDisabled(True)
        layout.addWidget(self.off_button_405, 2,0)

        min_label_405 = QLabel("Lower Limit: " + str(self.min_currents['405']) + " mA")
        min_label_405.setAlignment(Qt.AlignCenter) 
        layout.addWidget(min_label_405, 3,0)

        self.input_405 = QDoubleSpinBox()
        self.input_405.setMinimum(self.min_currents['405'])
        self.input_405.setMaximum(self.max_currents['405'])
        self.input_405.setValue(self.current_405)
        self.input_405.setSuffix(" mA")
        self.input_405.setSingleStep(0.1)
        self.input_405.setDisabled(True)
        self.input_405.valueChanged.connect(self.the_current_was_changed_405)
        layout.addWidget(self.input_405, 4,0)

        max_label_405 = QLabel("Upper Limit: " + str(self.max_currents['405']) + " mA")
        max_label_405.setAlignment(Qt.AlignCenter)
        layout.addWidget(max_label_405, 5,0)
###################################


########### 488nm laser ###########
        self.label_488 = QLabel()
        self.label_488.setStyleSheet("border: 1px solid; border-color: blue")
        layout.addWidget(self.label_488, 0,1)

        self.on_button_488 = QPushButton("Turn on 488 nm laser!")
        self.button_is_checked_488 = True
        self.on_button_488.setChecked(self.button_is_checked_488)
        self.on_button_488.clicked.connect(self.the_on_button_was_clicked_488)
        layout.addWidget(self.on_button_488, 1,1)

        self.off_button_488 = QPushButton("Turn off 488 nm laser!")
        self.off_button_488.clicked.connect(self.the_off_button_was_clicked_488)
        self.off_button_488.setDisabled(True)
        layout.addWidget(self.off_button_488, 2,1)

        min_label_488 = QLabel("Lower Limit: " + str(self.min_currents['488']) + " mA")
        min_label_488.setAlignment(Qt.AlignCenter)
        layout.addWidget(min_label_488, 3,1)

        self.input_488 = QDoubleSpinBox()
        self.input_488.setMinimum(self.min_currents['488'])
        self.input_488.setMaximum(self.max_currents['488'])
        self.input_488.setValue(self.current_488)
        self.input_488.setSuffix(" mA")
        self.input_488.setSingleStep(0.1)
        self.input_488.setDisabled(True)
        self.input_488.valueChanged.connect(self.the_current_was_changed_488)
        layout.addWidget(self.input_488, 4,1)

        max_label_488 = QLabel("Upper Limit: " + str(self.max_currents['488']) + " mA")
        max_label_488.setAlignment(Qt.AlignCenter)
        layout.addWidget(max_label_488, 5,1)
###################################


########### 561nm laser ###########
        self.label_561 = QLabel()
        self.label_561.setStyleSheet("border: 1px solid; border-color: green")
        layout.addWidget(self.label_561, 0,2)

        self.on_button_561 = QPushButton("Turn on 561 nm laser!")
        self.button_is_checked_561 = True
        self.on_button_561.setChecked(self.button_is_checked_561)
        self.on_button_561.clicked.connect(self.the_on_button_was_clicked_561)
        layout.addWidget(self.on_button_561, 1,2)

        self.off_button_561 = QPushButton("Turn off 561 nm laser!")
        self.off_button_561.clicked.connect(self.the_off_button_was_clicked_561)
        self.off_button_561.setDisabled(True)
        layout.addWidget(self.off_button_561, 2,2)

        min_label_561 = QLabel("Lower Limit: " + str(self.min_currents['561']) + " mA")
        min_label_561.setAlignment(Qt.AlignCenter)
        layout.addWidget(min_label_561, 3,2)

        self.input_561 = QDoubleSpinBox()
        self.input_561.setMinimum(self.min_currents['561'])
        self.input_561.setMaximum(self.max_currents['561'])
        self.input_561.setValue(self.current_561)
        self.input_561.setSuffix(" mA")
        self.input_561.setSingleStep(0.1)
        self.input_561.setDisabled(True)
        self.input_561.valueChanged.connect(self.the_current_was_changed_561)
        layout.addWidget(self.input_561, 4,2)

        max_label_561 = QLabel("Upper Limit: " + str(self.max_currents['561']) + " mA")
        max_label_561.setAlignment(Qt.AlignCenter)
        layout.addWidget(max_label_561, 5,2)
###################################


########### 638nm laser ###########
        self.label_638 = QLabel()
        self.label_638.setStyleSheet("border: 1px solid; border-color: red")
        layout.addWidget(self.label_638, 0,3)

        self.on_button_638 = QPushButton("Turn on 638 nm laser!")
        self.button_is_checked_638 = True
        self.on_button_638.setChecked(self.button_is_checked_638)
        self.on_button_638.clicked.connect(self.the_on_button_was_clicked_638)
        layout.addWidget(self.on_button_638, 1,3)

        self.off_button_638 = QPushButton("Turn off 638 nm laser!")
        self.off_button_638.clicked.connect(self.the_off_button_was_clicked_638)
        self.off_button_638.setDisabled(True)
        layout.addWidget(self.off_button_638, 2,3)

        min_label_638 = QLabel("Lower Limit: " + str(self.min_currents['638']) + " mA")
        min_label_638.setAlignment(Qt.AlignCenter)
        layout.addWidget(min_label_638, 3,3)

        self.input_638 = QDoubleSpinBox()
        self.input_638.setMinimum(self.min_currents['638'])
        self.input_638.setMaximum(self.max_currents['638'])
        self.input_638.setValue(self.current_638)
        self.input_638.setSuffix(" mA")
        self.input_638.setSingleStep(0.1)
        self.input_638.setDisabled(True)
        self.input_638.valueChanged.connect(self.the_current_was_changed_638)
        layout.addWidget(self.input_638, 4,3)

        max_label_638 = QLabel("Upper Limit: " + str(self.max_currents['638']) + " mA")
        max_label_638.setAlignment(Qt.AlignCenter)
        layout.addWidget(max_label_638, 5,3)
###################################

        # ymax input
        placeholder = QLabel()
        layout.addWidget(placeholder, 6,1)
        label_ymax = QLabel("Adjust Ymax: ")
        label_ymax.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_ymax, 7,1)

        self.input_ymax = QDoubleSpinBox()
        self.input_ymax.setValue(self.ymax)
        self.input_ymax.setSuffix(" V")
        self.input_ymax.setDecimals(4)
        self.input_ymax.setSingleStep(0.0010) # change this to 0.0010
        self.input_ymax.valueChanged.connect(self.the_voltage_was_changed_ymax)
        layout.addWidget(self.input_ymax, 7,2)

        # eoffset input
        label_eoffset = QLabel("Adjust ETL: ")
        label_eoffset.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_eoffset, 8,1)

        self.input_eoffset = QDoubleSpinBox()
        self.input_eoffset.setValue(self.eoffset)
        self.input_eoffset.setSuffix(" V")
        self.input_eoffset.setDecimals(4)
        self.input_eoffset.setSingleStep(0.0010) # change this to 0.0010
        self.input_eoffset.valueChanged.connect(self.the_voltage_was_changed_eoffset)
        layout.addWidget(self.input_eoffset, 8,2)

##### power-current table #####
        layout.addWidget(placeholder, 9, 0, 1, 4)
        label_table = QLabel("Approximate current - power conversions for selected laser:")
        label_table.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_table, 10, 1, 1, 2)

        self.tableWidget = QTableWidget(6,2)
        self.tableWidget.setHorizontalHeaderLabels(["Current (mA)", "Power (mW)"])
        layout.addWidget(self.tableWidget, 11, 1, 1, 2)
###################################

        # Layout finalized
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

########### on buttons ############
    def the_on_button_was_clicked_405(self):
        self.fWheel.setPosition(self.wheel_dict["names_to_channels"]["405"])
        print("Filter 1 set!")
        self.laser.turn_laser_on('405', self.current_405)
        self.daq.start("405")
        self.off_button_405.setDisabled(False)
        self.on_button_488.setDisabled(True)
        self.on_button_561.setDisabled(True)
        self.on_button_638.setDisabled(True)
        self.input_405.setDisabled(False)
        self.label_405.setStyleSheet("background-color: purple")
        self.update_table("405")

    def the_on_button_was_clicked_488(self):
        self.fWheel.setPosition(self.wheel_dict["names_to_channels"]["488"])
        print("Filter 2 set!")
        self.laser.turn_laser_on('488', self.current_488)
        self.daq.start("488")
        self.off_button_488.setDisabled(False)
        self.on_button_405.setDisabled(True)
        self.on_button_561.setDisabled(True)
        self.on_button_638.setDisabled(True)
        self.input_488.setDisabled(False)
        self.label_488.setStyleSheet("background-color: blue")
        self.update_table("488")

    def the_on_button_was_clicked_561(self):
        self.fWheel.setPosition(self.wheel_dict["names_to_channels"]["561"])
        print("Filter 3 set!")
        self.laser.turn_laser_on('561', self.current_561)
        self.daq.start("561")
        self.off_button_561.setDisabled(False)
        self.on_button_405.setDisabled(True)
        self.on_button_488.setDisabled(True)
        self.on_button_638.setDisabled(True)
        self.input_561.setDisabled(False)
        self.label_561.setStyleSheet("background-color: green")
        self.update_table("561")
    
    def the_on_button_was_clicked_638(self):
        self.fWheel.setPosition(self.wheel_dict["names_to_channels"]["638"])
        print("Filter 4 set!")
        self.laser.turn_laser_on('638', self.current_638)
        self.daq.start("638")
        self.off_button_638.setDisabled(False)
        self.on_button_405.setDisabled(True)
        self.on_button_488.setDisabled(True)
        self.on_button_561.setDisabled(True)
        self.input_638.setDisabled(False)
        self.label_638.setStyleSheet("background-color: red")
        self.update_table("638")
###################################


########### off buttons ###########
    def the_off_button_was_clicked_405(self):
        self.daq.stop("405")
        self.input_405.setDisabled(True)
        self.off_button_405.setDisabled(True)
        self.on_button_488.setDisabled(False)
        self.on_button_561.setDisabled(False)
        self.on_button_638.setDisabled(False)
        self.label_405.setStyleSheet("border: 1px solid; border-color: purple")
        self.update_table(0)

    def the_off_button_was_clicked_488(self):
        self.daq.stop("488")
        self.input_488.setDisabled(True)
        self.off_button_488.setDisabled(True)
        self.on_button_405.setDisabled(False)
        self.on_button_561.setDisabled(False)
        self.on_button_638.setDisabled(False)
        self.label_488.setStyleSheet("border: 1px solid; border-color: blue")
        self.update_table(0)

    def the_off_button_was_clicked_561(self):
        self.daq.stop("561")
        self.input_561.setDisabled(True)
        self.off_button_561.setDisabled(True)
        self.on_button_405.setDisabled(False)
        self.on_button_488.setDisabled(False)
        self.on_button_638.setDisabled(False)
        self.label_561.setStyleSheet("border: 1px solid; border-color: green")
        self.update_table(0)

    def the_off_button_was_clicked_638(self):
        self.daq.stop("638")
        self.input_638.setDisabled(True)
        self.off_button_638.setDisabled(True)
        self.on_button_405.setDisabled(False)
        self.on_button_488.setDisabled(False)
        self.on_button_561.setDisabled(False)
        self.label_638.setStyleSheet("border: 1px solid; border-color: red")
        self.update_table(0)
###################################


######### current changed #########
    def the_current_was_changed_405(self, current_405):
        self.current_405 = current_405
        self.laser.update('405', self.current_405)

    def the_current_was_changed_488(self, current_488):
        self.current_488 = current_488
        self.laser.update('488', self.current_488)

    def the_current_was_changed_561(self, current_561):
        self.current_561 = current_561
        self.laser.update('561', self.current_561)

    def the_current_was_changed_638(self, current_638):
        self.current_638 = current_638
        self.laser.update('638', self.current_638)
###################################


########### ymax changed ##########
    def the_voltage_was_changed_ymax(self, ymax):
        self.ymax = ymax
        self.daq.adjust_ymax(self.ymax)
        self.daq.create_voltages_galvo()
        self.daq.update()
###################################


########### etl changed ###########
    def the_voltage_was_changed_eoffset(self, eoffset):
        self.eoffset = eoffset
        self.daq.adjust_eoffset(self.eoffset)
        self.daq.create_voltages_etl()
        self.daq.update()
###################################


#### update current-power table ###
    def update_table(self, wavelength):
        if wavelength == 0:
            self.tableWidget.clear()
            self.tableWidget.setHorizontalHeaderLabels(["Current (mA)", "Power (mW)"])
        else:
            print("writing power-current table")
            for i in range(6):
                item = QTableWidgetItem(str(self.power_current[wavelength]["current"][i]))
                self.tableWidget.setItem(i, 0, item)
            for i in range(6):
                item = QTableWidgetItem(str(self.power_current[wavelength]["power"][i]))
                self.tableWidget.setItem(i, 1, item)
###################################


###########close event#############
    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("You sure?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            event.accept()
            self.laser.turn_laser_off("405")
            self.laser.turn_laser_off("488")
            self.laser.turn_laser_off("561")
            self.laser.turn_laser_off("638")
        else:
            event.ignore()
###################################


app = QApplication([])
w = MainWindow()
w.show()
app.exec()