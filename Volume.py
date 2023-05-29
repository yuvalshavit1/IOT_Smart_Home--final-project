import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from mqtt_init import *

# from PyQt5.QtCore import QTimer

# Creating Client name - should be unique 
global clientname, CONNECTED, valume_current
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id234-" + str(r)
DHT_topic = 'pr/home/5976397/sts'
update_rate = 1500  # in msec
max_valume_can = 2000
valume_current = max_valume_can
ValumePercent = 100


class Mqtt_client():

    def __init__(self) -> None:
        """constructor"""
        # broker IP adress:
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

    # Setters and getters
    def set_on_connected_to_form(self, on_connected_to_form) -> None:
        self.on_connected_to_form = on_connected_to_form

    def get_broker(self) -> str:
        return self.broker

    def set_broker(self, value) -> None:
        self.broker = value

    def get_port(self) -> str:
        return self.port

    def set_port(self, value) -> None:
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value) -> None:
        self.clientName = value

    def get_username(self) -> str:
        return self.username

    def set_username(self, value) -> None:
        self.username = value

    def get_password(self) -> str:
        return self.password

    def set_password(self, value) -> None:
        self.password = value

    def get_subscribeTopic(self) -> str:
        return self.subscribeTopic

    def set_subscribeTopic(self, value) -> None:
        self.subscribeTopic = value

    def get_publishTopic(self) -> str:
        return self.publishTopic

    def set_publishTopic(self, value) -> None:
        self.publishTopic = value

    def get_publishMessage(self) -> None:
        return self.publishMessage

    def set_publishMessage(self, value) -> None:
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf) -> None:
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc) -> None:
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form();
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0) -> None:
        CONNECTED = False
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg) -> None:
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self) -> None:
        # Init paho mqtt client class        
        self.client = mqtt.Client(self.clientname, clean_session=True)  # create new client instance
        self.client.on_connect = self.on_connect  # bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # connect to broker

    def disconnect_from(self) -> None:
        self.client.disconnect()

    def start_listening(self) -> None:
        self.client.loop_start()

    def stop_listening(self) -> None:
        self.client.loop_stop()

    def subscribe_to(self, topic) -> None:
        if CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connecection should be established first")

    def publish_to(self, topic, message) -> None:
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connecection should be established first")


class ConnectionDock(QDockWidget):
    """Main """

    def __init__(self, mc: Mqtt_client) -> None:
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")

        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(DHT_topic)

        self.Valume = QLineEdit()
        self.Valume.setText('')
        self.ValumePercent = QLineEdit()
        self.ValumePercent.setText('')

        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Topic", self.ePublisherTopic)
        formLayot.addRow("Volume", self.Valume)
        formLayot.addRow("Volume Percent", self.ValumePercent)
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self) -> None:
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self) -> None:
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()

    def push_button_click(self) -> None:
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":1')


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)  # in msec

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 600, 300, 150)
        self.setWindowTitle('Trash Volume data')

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def update_data(self):
        global valume_current
        print('Next update')
        valume_current = valume_current - random.randrange(1, 50)
        current_data = 'Volume: ' + str(valume_current)
        self.connectionDock.Valume.setText(str(valume_current))
        self.connectionDock.ValumePercent.setText(str(round(valume_current/max_valume_can*100, 2)) + " %")
        self.mc.publish_to(DHT_topic, current_data)


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
