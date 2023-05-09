# pip install -U pyinstaller
# pip install PyQt5

import json
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDoubleSpinBox, QGridLayout, QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QAction)
from PyQt5.QtCore import Qt
import numpy as np
import move2well
import time


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Move to well")
        # Create layout for the UI
        layout = QGridLayout()

        self.hivex_well = dict()
        for i in range(1, 13):
            self.well_number = i
            row = np.floor((i-1)/3)
            col = i - 3*row - 1
            self.hivex_well[i] = QPushButton(str(i))
            # print(self.hivex_well[i])
            self.hivex_well[i].setChecked(False)

            ## I really wish I knew how to pass parameters to button functions
            if i == 1:
                self.hivex_well[i].clicked.connect(self.move_to_1)
            if i == 2:
                self.hivex_well[i].clicked.connect(self.move_to_2)
            if i == 3:
                self.hivex_well[i].clicked.connect(self.move_to_3)
            if i == 4:
                self.hivex_well[i].clicked.connect(self.move_to_4)
            if i == 5:
                self.hivex_well[i].clicked.connect(self.move_to_5)
            if i == 6:
                self.hivex_well[i].clicked.connect(self.move_to_6)
            if i == 7:
                self.hivex_well[i].clicked.connect(self.move_to_7)
            if i == 8:
                self.hivex_well[i].clicked.connect(self.move_to_8)
            if i == 9:
                self.hivex_well[i].clicked.connect(self.move_to_9)
            if i == 10:
                self.hivex_well[i].clicked.connect(self.move_to_10)
            if i == 11:
                self.hivex_well[i].clicked.connect(self.move_to_11)
            if i == 12:
                self.hivex_well[i].clicked.connect(self.move_to_12)


            layout.addWidget(self.hivex_well[i], row + 1, col)
            i += 1

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


########### on buttons ############
    def move_to_1(self):
        ## Initialize XYZ stage
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(1)
        stage.go_to_well(xyzStage, well)

    def move_to_2(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(2)
        stage.go_to_well(xyzStage, well)

    def move_to_3(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(3)
        stage.go_to_well(xyzStage, well)

    def move_to_4(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(4)
        stage.go_to_well(xyzStage, well)

    def move_to_5(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(5)
        stage.go_to_well(xyzStage, well)

    def move_to_6(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(6)
        stage.go_to_well(xyzStage, well)

    def move_to_7(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(7)
        stage.go_to_well(xyzStage, well)

    def move_to_8(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(8)
        stage.go_to_well(xyzStage, well)

    def move_to_9(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(9)
        stage.go_to_well(xyzStage, well)

    def move_to_10(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(10)
        stage.go_to_well(xyzStage, well)

    def move_to_11(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(11)
        stage.go_to_well(xyzStage, well)

    def move_to_12(self):
        stage = move2well.stage() ## Grab stage parameters
        xyzStage = stage.init_stage() ## Initialize stage
        well = move2well.register_well(12)
        stage.go_to_well(xyzStage, well)





###########close event#############
    def closeEvent(self, event):

        event.accept()
###################################

app = QApplication([])
w = MainWindow()
w.show()
app.exec()