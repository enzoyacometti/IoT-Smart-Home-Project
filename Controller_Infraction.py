from MyMQTT import *
import time
import requests
import json
import datetime


class Controller_infraction :

	def __init__(self,clientID,broker,port):
		self.valuetype=""
		self.unit=""
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
		print(f"Published" + str(message))

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
			print(f'Sensor of {valuetype} is measuring {self.value} {unit} at time {timestamp} coming on topic {topic} from {client}')
			self.controll_data(root,userID,houseID,roomID,deviceID,self.value)
		except :
			print("The data format is not correct")


	def controll_data(self,root,userID,houseID,roomID,deviceID,value):

		if value == True :
			holidays = (requests.get('http://127.0.0.1:8080/catalog/holidays?user='+str(userID)).json())[houseID]
			infraction = self.date_comparison(holidays)
			if infraction == True :
				# compare timestamps to send 5 min
				self.send_actuation(infraction,root,userID,houseID,roomID,deviceID)
				requests.post('http://127.0.0.1:8080/statistics/infractions',
							  json.dumps({"value":userID + "-" + houseID + "-" + roomID + "-" + deviceID + "-" + str(self.value)}))

	def date_comparison(self,dict_holidays):
		print(dict_holidays)
		dict_holidays.pop("holidaysIndex")
		if len(dict_holidays) != 0:
			for holidayID in dict_holidays :
				beginning = dict_holidays[holidayID]["value"]["b"]
				ending = dict_holidays[holidayID]["value"]["e"]
				i_datetime = datetime.datetime.strptime(beginning,'%Y-%m-%d')
				f_datetime = datetime.datetime.strptime(ending,'%Y-%m-%d')
				time_now =datetime.datetime.now()
				
				if time_now > i_datetime and time_now < f_datetime:
					return True
					
				else :
					return False
		else :
			return False



	def send_actuation(self,value,root,userID,houseID,roomID,deviceID):
		clientID = "InfractionActuator" + deviceID
		new_value_type = "alarm"
		new_unit = "Boolean"
		new_topic = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=infraction').json())["value"]
		self.publish(value,new_topic[0],clientID,new_value_type,new_unit)




if __name__ == "__main__":
	mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
	broker = mqtt_details["broker"]
	port = int(mqtt_details["port"])
	#topics = []
	topics = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=infraction').json())["value"]
	topics_motion = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=motion').json())["value"]
	clientID="ControllerInfraction"

	controller = Controller_infraction(clientID,broker,port)
	controller.start()
	#for topic in topics:
	#	controller.subscribe(topic)
	for topic in topics_motion:
		controller.subscribe(topic)

	# un message a été reçu

	while True :
		time.sleep(2)



