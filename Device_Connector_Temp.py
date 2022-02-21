from MyMQTT import *
import datetime
import time
import requests

class Device_connector_Temperature:

	def __init__(self,broker,port,houseID,userID,roomID,deviceID):
		self.root="IoT_project_G4"
		self.houseID=houseID
		self.roomID=roomID
		self.userID=userID
		self.deviceID = deviceID
		self.value_type = "temperature"
		self.unit = "°C"
		self.broker = broker
		self.port = port
		self.topic = self.root + "/" + self.userID + "/" + self.houseID + "/" \
					 + self.roomID + "/" + self.value_type + "/" + self.deviceID
		self.clientID = "TemperatureSensor" + self.deviceID[6:]
		self.__message_temp = {'bn': self.topic, "clientID": self.clientID,
							   "e": {'n': self.value_type, 'v': None, 't': '',
									 'u': self.unit}}  # set the message pattern
		self.client = MyMQTT(self.clientID, self.broker, self.port, None)  # set the MQTT instance

	def start(self):
		self.client.start()

	def stop(self):
		self.client.stop()

	def publish(self, value):
		message = self.__message_temp
		message['e']["t"] = str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
		message["e"]['v'] = value
		self.client.myPublish(self.topic, message)


if __name__ == "__main__":

	# local host - obtain home catalog
	mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
	broker = mqtt_details["broker"]
	port = int(mqtt_details["port"])
	houseID="house1"
	roomID="room1"
	userID="user1"
	deviceID = "device1"
	temperature = Device_connector_Temperature(broker,port,houseID,userID,roomID,deviceID)
	temperature.start()

	time.sleep(2)

	print('Publisher is active, temp. values printed every 1 second\n')

	while True:

		i = 20
		while i <= 26:
			temp = i
			temperature.publish(temp)
			i += 1
			time.sleep(4)
		while i >=14:
			temp=i
			temperature.publish(temp)
			i -= 1
			time.sleep(4)

