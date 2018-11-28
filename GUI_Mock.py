import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot



class Ui_Form(object):
    
    def readFile(self, fileName):
        file = open(fileName, 'r')
        return file.readline()
 
    
    def setupUi(self, Form):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        # Create Label for Config File Input
        self.textLabel = QLabel(self)
        self.textLabel.setText("Please Enter the Config File Name: ")
        self.textLabel.resize(280,20)
        self.textLabel.move(20,0)
        
        # Create textbox for config File Input
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280,20)
 
        # Create a button to get Config File
        self.button = QPushButton('Retrieve Config', self)
        self.button.resize(120,30)
        self.button.move(20,80)
        
        # Create a button to Push a file into Cloud
        self.button2 = QPushButton('Add File', self)
        self.button2.resize(120,30)
        self.button2.move(140,80)
        
        # Create a button to Retrieve from Cloud
        self.button3 = QPushButton('Retrieve File', self)
        self.button3.resize(120,30)
        self.button3.move(260,80)
        
        
        # Add a Text Box Saying what file is being uploaded
        self.uploadConfirm = QLabel(self)
        self.uploadConfirm.setText("File to upload: None")
        self.uploadConfirm.resize(280,20)
        self.uploadConfirm.move(20,40)
 
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
       

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "PushButton"))
        
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        print(type(textboxValue))
        
        messageToast = self.readFile(textboxValue)
        QMessageBox.question(self, 'Message - Cloud Storage', "Your Config File is: " + messageToast, QMessageBox.Ok, QMessageBox.Ok)
        self.textbox.setText(messageToast)
 


class Widget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.title = 'CSE 8377 Cloud Storage'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 140
        self.setupUi(self)
        self.button2.clicked.connect(self.openFile)

    def openFile(self):   
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName == "":
            self.uploadConfirm.setText("File to upload: None")
        if fileName != "":
            buttonReply = QMessageBox.question(self, 'Message - Cloud Storage', "You are wanting to upload: " + fileName, QMessageBox.Yes, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')
                self.uploadConfirm.setText("File to upload: " + fileName)
            if buttonReply == QMessageBox.No:
                print('No clicked.')
                self.uploadConfirm.setText("File to upload: None")
            if buttonReply == QMessageBox.Cancel:
                print('Cancel')
                self.uploadConfirm.setText("File to upload: None")



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = Widget()
    ui = Ui_Form()
    Form.show()
    sys.exit(app.exec_())