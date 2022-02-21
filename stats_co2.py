import datetime


class co2_stats:

    def __init__(self):
        self.valuetype = "co2"
        self.unit = "PPM"
        self.status_now = bool     # if windows are open or closed right now
        self.are_values = False    

    def record_co2(self, userID, houseID, roomID, data_co2):
        values_co2 = [[],[]]
        time_now = datetime.datetime.now()
        beginning_time = time_now - datetime.timedelta(days=1)


        # parsing of co2 values
        for j in range(len(data_co2)):
            timestamp = datetime.datetime.strptime(data_co2[j]['t'], '%d/%m/%Y %H:%M:%S')
            
            if timestamp > beginning_time and timestamp < time_now:
                data_parsed_co2 = data_co2[j]["v"].split("-")
                if data_parsed_co2[0]==userID and data_parsed_co2[1]==houseID and data_parsed_co2[2]==roomID:
                    values_co2[0].append(int(data_parsed_co2[-1]))
                    values_co2[1].append(str(timestamp))
        return (values_co2)

    
    def record_windows(self, userID, houseID, roomID, data_windows):
        time_now = datetime.datetime.now()
        values_win = []
        ref_values = []
        beginning_time = time_now - datetime.timedelta(days=1)

        for i in range(len(data_windows)):
            timestamp = datetime.datetime.strptime(data_windows[i]['t'], '%d/%m/%Y %H:%M:%S')
            if timestamp > beginning_time and timestamp < time_now:
                data_parsed = data_windows[i]["v"].split("-")
                if data_parsed[0] == userID and data_parsed[1] == houseID and data_parsed[2] == roomID:
                    ref_values.append(data_windows[i]['v'].split("-"))
                    values_win.append(str(datetime.datetime.strptime(data_windows[i]['t'], '%d/%m/%Y %H:%M:%S')))
                    self.are_values = True

        # If it's the first value, we see if its opened or closed
        # If the first value is closed then we add an open 24 hours before the request
        if self.are_values:
            for j in range(len(ref_values)):
                if j == 0 and ref_values[0][-1] == 'WindowsClosed':
                    values_win.insert(0,str(time_now-datetime.timedelta(days=1)))
                    
                # If the last value is opened, then add a closed right now
                if j==len(ref_values)-1 and ref_values[-1][-1] == 'WindowsOpened':
                    values_win.append(str(datetime.datetime.now()))
                    self.status_now = True
                else:
                    self.status_now = False
        
        #print("values windows: " + str(values_win))
        return (values_win)






