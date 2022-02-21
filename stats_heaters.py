import datetime


class heaters_stats :

	def __init__(self):
		self.valuetype="HeatersStatus"
		self.unit="Boolean"
		self.consumption = 0    # kJ used of energy
		self.status_now = bool	# heater on or off
		self.are_values = False  # if there are values to send


	def stats(self,userID,houseID,roomID,data,heaters_power):
		time_now = datetime.datetime.now()
		data_to_send =[]
		ref_values = []
		beginning_time = time_now - datetime.timedelta(days=1)

		for i in range(len(data)):
			timestamp = datetime.datetime.strptime(data[i]['t'], '%d/%m/%Y %H:%M:%S')
			if timestamp > beginning_time and timestamp < time_now:
				data_parsed = data[i]["v"].split("-")
				if data_parsed[0] == userID and data_parsed[1] == houseID and data_parsed[2] == roomID:
					ref_values.append(data[i]['v'].split("-"))
					data_to_send.append(datetime.datetime.strptime(data[i]['t'], '%d/%m/%Y %H:%M:%S'))
					self.are_values = True

		# If it's the first value, we see if it turned on or off
		# If the first value is a turnoff then we add a turn on 24 hours before the request
		if self.are_values:
			for j in range(len(ref_values)):
				if j == 0 and ref_values[0][-1] == 'HeatersOff':
					data_to_send.insert(0,time_now-datetime.timedelta(days=1))
				# If the last value is on, then add an off value right now
				if j==len(ref_values)-1 and ref_values[-1][-1] == 'HeatersOn':
					data_to_send.append(datetime.datetime.now())
					self.status_now = True
				else:
					self.status_now = False

		# calculate consumption and save it on self.value
		self.consumption = self.calculate_consumption(data_to_send,heaters_power)
		# send stats
		for i in range(len(data_to_send)):
			data_to_send[i] = str(data_to_send[i])

		self.are_values = False
		#print("values heaters: " + str(data_to_send))
		return ({"timestamps":data_to_send, "Consumption (KJ)":self.consumption})

	def calculate_consumption(self, timestamps,heaters_power):
		power = heaters_power
		con = 0      # consumption
		j = 0        # counter
		while j <= len(timestamps)-2:
			con += power*abs((timestamps[j+1]-timestamps[j]).seconds)   # retrieves every OTHER timestamp (processes pairs)
			j += 2
		value = con/1000 # in KiloJoules
		return value

