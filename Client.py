from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import socket, pickle, sys, threading
import AES
import random

#GLOBAL VARIABLES
contact_list = []
msgs = {}

class msg:
    def __init__(self):
        self.type = ""
        self.msg = ""

x = 0
g=None
n=None
b=None
sk=None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("                                                                                                             "+name)
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
        a = AES.AESCipher(str(sk))
        ss = self.content.text()
        print("content from sender = "+ss)
        ss = a.encrypt(ss)
        print(type(ss))
        mx.msg = ss + ',' + current
        self.content.clear()
        msgs[current].append(name + ": " +a.decrypt(mx.msg.split(',')[0]))
        s.send(pickle.dumps(mx))
        self.update_msgs()

    def update_msgs(self):
        print("Entered in update message")
        current = self.list_contact.currentItem().text()
        self.list_msgs.deleteLater()
        self.list_msgs = QListWidget(self.centralWidget)
        self.list_msgs.setObjectName("list_msgs")
        for i in range(len(msgs[current])):
            self.list_msgs.addItem(msgs[current][i])
        self.list_msgs.setGeometry(QRect(260, 10, 521, 501))
        self.list_msgs.show()
        global x
        if x == 0:
            mx = msg()
            mx.type = "key"
            ss = "Hello key "
            mx.msg = ss + ',' + current
            s.send(pickle.dumps(mx))
        x = 1

    def update_contact(self):
        # print("Entered in update contact function")
        self.list_contact.deleteLater()
        self.list_contact = QListWidget(self.centralWidget)
        self.list_contact.setObjectName("list_contact")
        self.list_contact.setGeometry(QRect(0, 10, 256, 541))
        for i in range(len(contact_list)):
            self.list_contact.addItem(contact_list[i])
        self.list_contact.clicked.connect(self.update_msgs)
        self.list_contact.show()

class receive(QThread):
    hin = Signal()
    dhr = Signal()
    def __init__(self, s):
        QThread.__init__(self)
        self.s = s
    def run(self):
        while True:
            global contact_list
            m = pickle.loads(self.s.recv(1024))
            print("got new msg")
            if m.type == "new":
                # print("got msg for new connection")
                contact_list.append(m.msg)
                msgs[m.msg] = []
                self.dhr.emit()
            elif m.type == "msg":
                se, content = m.msg.split(':')
                print(" Super key : "+str(sk))
                a = AES.AESCipher(str(sk))
                print("content A : "+content)
                # content = a.encrypt(content)
                # print(" encrypted content : "+ content)
                # content = a.decrypt(content)
                # print(" content B : "+content)
                # c = m.msg.split(':')[1]
                content = a.decrypt(content)
                # print(c)
                print(" check = "+m.msg.split(',')[0])
                print(" se = "+se+" content = "+content)
                msgs[se].append(m.msg.split(',')[0])
                print(se+":"+content)
                self.hin.emit()
            elif m.type == "key2":
                global x
                x = 1
                print(m.msg)
                n = int(m.msg.split(':')[1])
                g = int(m.msg.split(':')[2])
                b = random.randint(2,n-1)
                ln = pow(g,b,n)
                mx = msg()
                mx.type = "key3"
                ss = str(ln)
                mx.msg = ss + ',' + m.msg.split(':')[0]
                s.send(pickle.dumps(mx))
            elif m.type == "key3":
                print(m.msg)
                y = int(m.msg.split(':')[1])
                sk = pow(y,b,n)
                print(sk)	


###################################################################################################################


s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",12345))
#sending the name through cmd
name = input('Enter your name : ')
s.send(name.encode())
contact_list = pickle.loads(s.recv(4000)) #Got previous contact_list
for i in contact_list:
    msgs[i] = []
# threading.Thread(target=receiver, args = (s,)).start()


######################################################################################################################
app = QApplication(sys.argv)
window = MainWindow()
window.resize(800,600)
receive_thread = receive(s)
receive_thread.dhr.connect(window.update_contact)
receive_thread.hin.connect(window.update_msgs)
receive_thread.start()
window.show()
sys.exit(app.exec())