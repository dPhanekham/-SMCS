import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot



class Ui_Form(object):
    
    def readFile(self, fileName):
        if (fileName == ''):
            return " "
        file = open(fileName, 'r')
        return file.readline()
 
    
    def setupUi(self, Form):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        # Create Label for Config File Input
        self.textLabel = QLabel(self)
        self.textLabel.setText("Please Enter the Config File Name: ")
#        self.textLabel.resize(280,20)
#        self.textLabel.move(20,0)
        
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
        
        # Create a button to Update Files in Cloud
        self.button4 = QPushButton('Update File List', self)
        self.button4.resize(120,30)
        self.button4.move(260,60)
        
        # Create a button to Retrieve from Cloud
        self.button3 = QPushButton('Retrieve File', self)
#        self.button3.resize(120,30)
#        self.button3.move(260,80)
        
        
        # Add a Text Box Saying what file is being uploaded
        self.uploadConfirm = QLabel(self)
        self.uploadConfirm.setText("File to upload: None")
        self.uploadConfirm.setWordWrap(True)
#        self.uploadConfirm.resize(600,40)
#        self.uploadConfirm.move(20,40)
        
        
        # Add in area with Files in Cloud
        self.remoteFiles = QLabel(self)
        self.remoteFiles.setText("Files in cloud: ")
#        self.remoteFiles.resize(400,400)
#        self.remoteFiles.move(20,50)
 
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        
        self.button4.clicked.connect(self.on_click2)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.button2)
        hbox.addWidget(self.button3)
        
        hbox2 =QHBoxLayout()
        hbox2.addWidget(self.button,1,QtCore.Qt.AlignLeft)
        
        
        
        hbox3 =QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(self.button4)
        
        hbox4 =QHBoxLayout()
        hbox4.addWidget(self.textLabel)
        hbox4.addWidget(self.textbox)
        hbox6 =QHBoxLayout()
        hbox6.addWidget(self.uploadConfirm)
        hbox7 =QHBoxLayout()
        hbox7.addWidget(self.remoteFiles)
        
       


        vbox = QVBoxLayout()
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox2)

        
        vbox.addLayout(hbox3)
        
         

        vbox.addLayout(hbox6)

        vbox.addLayout(hbox7)
        vbox.addStretch(1)
        vbox.addLayout(hbox)
        
        
        

        
        
        self.setLayout(vbox)
         
        
#        self.setGeometry(300, 300, 300, 150)
#        self.setWindowTitle('Buttons')    
        self.show()
       

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "PushButton"))
        
    @pyqtSlot()
    def on_click(self):
        textboxValue = self.textbox.text()
        if(textboxValue != ""):
            messageToast = self.readFile(textboxValue)
            QMessageBox.question(self, 'Message - Cloud Storage', "Your Config File is: " + messageToast, QMessageBox.Ok, QMessageBox.Ok)
            self.textbox.setText(messageToast)
        
    @pyqtSlot()
    def on_click2(self):
        self.remoteFiles.setText("File in cloud: None")

 


class Widget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.title = 'CSE 8377 Cloud Storage'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 600
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