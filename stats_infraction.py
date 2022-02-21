import datetime


class stats_infraction :

	def __init__(self):
		self.valuetype="infraction"
		self.unit="Boolean"




	def stats(self,userID,houseID,data):
		time_now = datetime.datetime.now()
		timestamps = []
		n_infractions = 0

		# 6 months ago
		beginning_time = time_now - datetime.timedelta(weeks=24)

		for i in range(len(data)):
			timestamp = datetime.datetime.strptime(data[i]['t'], '%d/%m/%Y %H:%M:%S')

			if timestamp > beginning_time and timestamp < time_now:
				data_parsed = data[i]["v"].split("-")
				if data_parsed[0] == userID and data_parsed[1] == houseID:
					timestamps.append(str(timestamp))
					n_infractions += 1

		return ({"Number of infractions":n_infractions,"timestamps":timestamps})



