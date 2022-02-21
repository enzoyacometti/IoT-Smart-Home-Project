from MyMQTT import *
import datetime
import requests
import time
import random

#import Adafruit_DHT

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
#sensor = Adafruit_DHT.DHT11


class device_connector_CO2 :

	def __init__(self,broker,port,houseID,userID,roomID,deviceID):
		self.root="IoT_project_G4"
		self.houseID=houseID
		self.roomID=roomID
		self.userID=userID
		self.deviceID = deviceID
		self.value_type = "co2"
		self.unit = "PPM"
		self.broker = broker
		self.port = port
		self.topic = self.root + "/" + self.userID + "/" + self.houseID + "/" \
					 + self.roomID + "/" + self.value_type + "/" + self.deviceID
		self.clientID = "EmulatedCO2Sensor" + self.deviceID[6:]
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
	mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
	houseID="house1"
	roomID="room1"
	userID="user1"
	deviceID = "device2"
	broker = mqtt_details["broker"]
	port = int(mqtt_details["port"])
	co2_emulator = device_connector_CO2(broker,port,houseID,userID,roomID,deviceID)
	co2_emulator.start()

	Co2 = 600 #set initial value
	print('Publisher is active, co2 values printed every 5 seconds\n')
	
	while True:
		if Co2 > 1200 :
			while Co2 > 800 :
				Co2 -= random.randint(15,25)
				co2_emulator.publish(Co2)  # publish the new value
				time.sleep(1)
		else :
			Co2 += random.randint(15,25)
			co2_emulator.publish(Co2)  # publish the new value
			time.sleep(1)


