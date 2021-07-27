from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import socket, pickle, sys, threading

#GLOBAL VARIABLES
contact_list = []
msgs = {}

class msg:
    def __init__(self):
        self.type = ""
        self.msg = ""



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Chat App")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # adding line_edit and button
        self.content = QLineEdit(self.centralWidget)
        self.send_but = QPushButton(self.centralWidget)
        self.send_but.setText("SEND")
        self.send_but.setGeometry(QRect(710, 510, 75, 31))
        self.send_but.clicked.connect(self.test)
        self.content.setGeometry(QRect(260, 510, 451, 31))

        
        self.list_contact = QListWidget(self.centralWidget)
        self.list_contact.setObjectName("list_contact")
        self.list_contact.setGeometry(QRect(0, 10, 256, 541))
        for i in range(len(contact_list)):
            self.list_contact.addItem(contact_list[i])
        self.list_contact.clicked.connect(self.update_msgs)

        self.list_msgs = QListWidget(self.centralWidget)
        self.list_msgs.setObjectName("list_msgs")
        self.list_msgs.addItem("Hello")
        self.list_msgs.setGeometry(QRect(260, 10, 521, 501))


    def test(self):
        current = self.list_contact.currentItem().text()
        mx = msg()
        mx.type = "msg"
        ss = self.content.text()
        mx.msg = ss + ',' + current
        self.content.clear()
        msgs[current].append(name + ": " +mx.msg)
        s.send(pickle.dumps(mx))

    def update_msgs(self):
        current = self.list_contact.currentItem().text()
        self.list_msgs.deleteLater()
        self.list_msgs = QListWidget(self.centralWidget)
        self.list_msgs.setObjectName("list_msgs")
        for i in range(len(msgs[current])):
            self.list_msgs.addItem(msgs[current][i])
        self.list_msgs.setGeometry(QRect(260, 10, 521, 501))
        self.list_msgs.show()

    def update_contact(self):
        print("Entered in update contact function")
        self.list_contact.deleteLater()
        self.list_contact = QListWidget(self.centralWidget)
        self.list_contact.setObjectName("list_contact")
        self.list_contact.setGeometry(QRect(0, 10, 256, 541))
        for i in range(len(contact_list)):
            self.list_contact.addItem(contact_list[i])
        self.list_contact.show()

class receive(QThread):
    hin = Signal()
    dhr = Signal()
    def run(self, s):
        while True:
            global contact_list
            m = pickle.loads(s.recv(1024))
            if m.type == "new":
                contact_list.append(m.msg)
                msgs[m.msg] = []
                self.dhr.emit()
            else:
                se, content = m.msg.split(':')
                msgs[se].append(m.msg)
                print(m.msg)
                self.hin.emit()


###################################################################################################################


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",12345))
#sending the name through cmd
name = input()
s.send(name.encode())
contact_list = pickle.loads(s.recv(4000)) #Got previous contact_list
for i in contact_list:
    msgs[i] = []
# threading.Thread(target=receiver, args = (s,)).start()


######################################################################################################################
app = QApplication(sys.argv)
window = MainWindow()
window.resize(800,600)
receive_thread = receive()
receive_thread.hin.connect(window.update_msgs)
receive_thread.dhr.connect(window.update_contact)
window.show()
sys.exit(app.exec())