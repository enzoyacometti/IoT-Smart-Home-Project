from MyMQTT import *
import json
import datetime
import requests
import time
import random

#device_connector_infraction is used to read data from the sensor(emulated here) and send it through mqtt to a specific topic
class device_connector_infraction :

    def __init__(self,houseID,userID,roomID,deviceID):
        self.root="IoT_project_G4"
        self.houseID=houseID
        self.roomID=roomID
        self.userID=userID
        self.deviceID = deviceID
        self.value_type = "infraction"
        self.unit = "boolean"
        self.broker = "test.mosquitto.org"
        self.port = 1883
        self.topic = self.root + "/" + self.userID + "/" + self.houseID + "/" \
                     + self.roomID + "/" + self.value_type + "/" + self.deviceID
        self.clientID = "MotionSensor" + self.deviceID[6:]
        self.__message_temp = {'bn': self.topic, "clientID": self.clientID,
                               "e": {'n': self.value_type, 'v': None, 't': '', 'u': self.unit}}  # set the message pattern
        self.client = MyMQTT(self.clientID, self.broker, self.port, None)  # set the MQTT instance


    def start (self):
        self.client.start()
    def stop (self):
        self.client.stop()

    def publish(self,value):
        message=self.__message_temp
        message['e']["t"]=str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        message["e"]['v']=value
        self.client.myPublish(self.topic,message)


if __name__ == "__main__":
    houseID="house1"
    roomID="room1"
    userID="user1"
    deviceID = "device3"
    motion = device_connector_infraction(houseID,userID,roomID,deviceID)
    motion.client.start()

    #set mention value to true during deltaT seconds, then to false and repeat
    deltaT=10
	print(f'Publisher is active, infr. values printed every {deltaT} seconds\n')
    while True :

        motion.publish(True)
        time.sleep(deltaT)
        motion.publish(False)
        time.sleep(deltaT)



#	    pir.wait_for_motion()
#       while not pir.wait_for_no_motion():
#           dataManager.publish(True)
#           time.sleep(0.5)








