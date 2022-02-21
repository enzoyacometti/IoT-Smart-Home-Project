from MyMQTT import *
import time
import json
import requests
import datetime

class Controller_co2 :

	def __init__(self,clientID,broker,port):
		self.valuetype="co2"
		self.unit="PPM"
		self.windows_open = bool
		self.broker = broker
		self.port = port
		# inialize the mqtt instance
		self.client = MyMQTT(clientID, broker, port, self)
		self.value = 0

	def start(self):
		self.client.start()

	def subscribe(self, topic):
		self.client.mySubscribe(topic)

	def stop(self):
		self.client.stop()

	def publish(self,value,topic,clientID,value_type,unit):
		message={'bn': "",'clientID':"",'e':{'n':"",'v':None, 't':"",'u':""}} #set the message pattern
		message['e']['t']=str('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
		message['e']['v']=value
		message['e']['u'] = unit
		message['e']['n'] = value_type
		message['bn'] = topic
		message['clientID'] = clientID
		self.client.myPublish(topic,message)

	def notify(self, topic, msg):
		try :
			d = json.loads(msg)
			self.value = d['e']["v"]
			unit = d['e']["u"]
			client = d['clientID']
			timestamp = d["e"]['t']
			id = topic.split("/")
			root = id[0]
			userID = id[1]
			houseID = id[2]
			roomID = id[3]
			valuetype = id[4]
			deviceID = id[5]
			requests.post('http://127.0.0.1:8080/statistics/co2Values',json.dumps({"value": userID + "-" + houseID + "-" + roomID + "-" + deviceID + "-" + str(self.value)}))
			print(f'Sensor of {valuetype} is measuring {self.value} {unit} at time {timestamp} coming on topic {topic} from {client}')
			self.controll_data(root,userID,houseID,roomID,deviceID,self.value)

		except :
			print("The data format is not correct")


	def controll_data(self,root,userID,houseID,roomID,deviceID,value):
		threshold_min = (requests.get('http://127.0.0.1:8080/catalog/threshold_co2/'
								  +userID+'/'+houseID+'/'+roomID+'/'+deviceID).json())["threshold_min"]
		threshold_max = (requests.get('http://127.0.0.1:8080/catalog/threshold_co2/'
									  + userID + '/' + houseID + '/' + roomID + '/' + deviceID).json())["threshold_max"]


		if value > threshold_max:
			previous_value = (requests.get('http://127.0.0.1:8080/catalog/windows_status/'
										   +userID+'/'+houseID+'/'+roomID+'/'+deviceID).json())["status"]

			if previous_value == 'close':
				self.windows_open = True
				requests.put('http://127.0.0.1:8080/catalog/windows_status/'
										   +userID+'/'+houseID+'/'+roomID+'/'+deviceID+'?status=open')
				self.send_actuation(True,root,userID,houseID,roomID,deviceID)
				requests.post('http://127.0.0.1:8080/statistics/statusWindows',json.dumps({"value": userID + "-" + houseID + "-" + roomID + "-" + deviceID + "-WindowsOpened"}))

		elif value < threshold_min :
			previous_value = (requests.get('http://127.0.0.1:8080/catalog/windows_status/'
										   +userID+'/'+houseID+'/'+roomID+'/'+deviceID).json())["status"]

			if previous_value == 'open':
				self.windows_open = False
				requests.put('http://127.0.0.1:8080/catalog/windows_status/'
							 + userID + '/' + houseID + '/' + roomID + '/' + deviceID + '?status=close')
				self.send_actuation(False, root, userID, houseID, roomID, deviceID)
				requests.post('http://127.0.0.1:8080/statistics/statusWindows',json.dumps({"value": userID + "-" + houseID + "-" + roomID + "-" + deviceID + "-WindowsClosed"}))


	def send_actuation(self,value,root,userID,houseID,roomID,deviceID):
		clientID = "Co2Actuator" + deviceID
		new_value_type = "windowsStatus"
		new_unit = "Boolean"
		new_topic = root + "/" + userID + "/" + houseID + "/" + roomID + "/" + new_value_type
		self.publish(value,new_topic,clientID,new_value_type,new_unit)




if __name__ == "__main__":
	mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
	broker = mqtt_details["broker"]
	port = int(mqtt_details["port"])
	topics = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=co2').json())["value"]
	clientID="ControllerCo2"

	controller = Controller_co2(clientID,broker,port)
	controller.start()
	for topic in topics:
		controller.subscribe(topic)
	# un message a été reçu

	while True :
		time.sleep(5)

