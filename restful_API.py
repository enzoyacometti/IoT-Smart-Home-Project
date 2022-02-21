## RESTful Catalog

import json
import cherrypy
from datetime import datetime
import stats_co2
import stats_heaters
import stats_infraction

class WebCatalogManager:
    exposed=True

    def __init__(self):
        self.stats_co2 = stats_co2.co2_stats()
        self.stats_temp = stats_heaters.heaters_stats()
        self.stats_infraction = stats_infraction.stats_infraction()
    
    def GET(self,*uri,**params):

        if len(uri)!=0 and uri[0] == 'catalog':
            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1]=="mqtt_details":
                details = {}
                details["broker"] = catalog["broker"]
                details["port"] = catalog["port"]
                return json.dumps(details)

            if uri[1]=="all_topics":
                program = params["program"]
                valuetype = params["type"]
                topics = []
                for user in catalog["usersList"]:
                    if valuetype in catalog["usersList"][user]["topics"][program]:
                        topics.append(catalog["usersList"][user]["topics"][program][valuetype])
                return json.dumps({"value":topics})
            
            if uri[1]=="all_users":
                users=[]
                try:
                    for user in catalog["usersList"]:
                        users.append({user:user})
                    return json.dumps(users)
                except :
                    raise cherrypy.HTTPError(500,"please enter a valid request")

            if uri[1]=="houses":
                user=uri[2]
                houses=[]
                try : 
                    for house in catalog["usersList"][user]["houses"]:
                        houses.append(house)
                    return json.dumps(houses)
                except :
                    raise cherrypy.HTTPError(500,"please enter a valid request")

            if uri[1]=="rooms":
                user=uri[2]
                house=uri[3]
                rooms=[]
                try : 
                    for room in catalog["usersList"][user]["houses"][house]["rooms"]:
                        rooms.append(room)
                    return json.dumps(rooms)
                except :
                    raise cherrypy.HTTPError(500,"please enter a valid request")
                


            if uri[1]=="holidays":  ## get holidays
                result={}
                for house in catalog["usersList"][params["user"]]["houses"]:
                    result[house]=(catalog["usersList"][params["user"]]["houses"][house]["holidays"])
                return json.dumps(result)

            if uri[1] == 'threshold_temperature':  ## get threshold
                user = uri[2]
                house = uri[3]
                room = uri[4]
                threshold_min = catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_min_temperature"]
                threshold_max = catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_max_temperature"]
                return json.dumps({"threshold_min":threshold_min,"threshold_max":threshold_max})

            if uri[1] == 'threshold_co2':  ## get threshold
                user = uri[2]
                house = uri[3]
                room = uri[4]
                threshold_min = catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_min_co2"]
                threshold_max = catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_max_co2"]
                return json.dumps({"threshold_min":threshold_min,"threshold_max":threshold_max})

            if uri[1] == 'chatID':  ## get chatIDs for a single user's house
                user = uri[2]
                house = uri[3]
                chatID = catalog["usersList"][user]["houses"][house]["chatIDs"]
                username = catalog["usersList"][user]["userName"]
                return json.dumps({"chatID":chatID,"username":username})

            if uri[1] == 'all_chatIDs':  ## get all chatIDs
                all_chatIDs=[]
                for user in catalog['usersList']:
                    for house in catalog['usersList'][user]['houses']:
                        for ID in catalog['usersList'][user]['houses'][house]["chatIDs"]:
                            all_chatIDs.append(ID)
                return json.dumps({"all_chatIDs":all_chatIDs})

            if uri[1] == 'evaluate_password':  ## get password for setting up telegram bot
                for user in catalog["usersList"]:
                    for house in catalog["usersList"][user]["houses"]:
                        if params["password"] == catalog["usersList"][user]["houses"][house]["PasswordBot"]:
                            return json.dumps({"correct":True, "user":user, "house":house})
                return json.dumps({"correct":False, "user":None, "house":None})

            if uri[1] == 'heaters_status': ## get status for heaters or windows
                user = uri[2]
                house = uri[3]
                room = uri[4]
                status = catalog["usersList"][user]["houses"][house]["rooms"][room]["HeatersStatus"]
                return json.dumps({"status":status})

            if uri[1] == 'windows_status': ## get status for heaters or windows
                user = uri[2]
                house = uri[3]
                room = uri[4]
                status = catalog["usersList"][user]["houses"][house]["rooms"][room]["WindowsStatus"]
                return json.dumps({"status":status})

            if uri[1] == "electricity_price":
                price = catalog["electricity_price (euro per kwh)"]
                return json.dumps({"price":price})



        elif len(uri)!=0 and uri[0]=="statistics":

            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            with open('stats.json') as json_file:
                stats = json.load(json_file)
                json_file.close()

            user = uri[1]
            house = uri[2]
            room = uri[3]
            co2_record = self.stats_co2.record_co2(user,house,room,stats["co2Values"])
            windows_record = self.stats_co2.record_windows(user,house,room,stats["statusWindows"])
            heatersStatus = catalog["usersList"][user]["houses"][house]["rooms"][room]["HeatersStatus"]
            windowsStatus = catalog["usersList"][user]["houses"][house]["rooms"][room]["WindowsStatus"]

            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()
            heaters_power = catalog["usersList"][user]["houses"][house]["rooms"][room]["HeaterPower"]
            temp_stats = self.stats_temp.stats(user,house,room,stats["statusHeaters"],heaters_power)

            infraction_stats = self.stats_infraction.stats(user,house,stats["infractions"])
            
            return json.dumps({"temperature":{"temp_stats":temp_stats, "heatersStatus":heatersStatus},"co2":{"co2_record":co2_record,"windows_record":windows_record,"windowStatus":windowsStatus},"infraction":infraction_stats})


        else :
            return "Your request is not valid"



    def POST(self,*uri,**params):
        # Add information

        #with open('catalog.json') as json_file:

        body=cherrypy.request.body.read()

        # If it's not already in json format, it's necessary to convert
        dict = json.loads(body)

        if len(uri)!=0 and uri[0] == 'catalog':
            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "holidays":
                user = uri[2]
                house = uri[3]
                catalog["usersList"][user]["houses"][house]["holidays"][dict["holidaysID"]] = dict["holidays"]
                catalog["usersList"][user]["houses"][house]["holidays"]["holidaysIndex"] = dict["holidaysIndex"]

            if uri[1] == "chatID":
                user = uri[2]
                house = uri[3]
                chatID = int(dict["chatID"])
                (catalog["usersList"][user]["houses"][house]["chatIDs"]).append(chatID)


            jsonFile = open("catalog.json", "w+")
            jsonFile.write(json.dumps(catalog, indent=4))
            jsonFile.close()


        elif len(uri)!=0 and uri[0]=="statistics":
            with open('stats.json') as json_file:
                stats = json.load(json_file)
                json_file.close()

            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            if uri[1] == "tempValues":
                stats["tempValues"].append({"t": str(timestamp), "v": str(dict["value"])})

            if uri[1] == "statusHeaters":
                stats["statusHeaters"].append({"t": str(timestamp), "v": str(dict["value"])})

            if uri[1] == "co2Values":
                stats["co2Values"].append({"t": str(timestamp), "v": str(dict["value"])})

            if uri[1] == "statusWindows":
                stats["statusWindows"].append({"t": str(timestamp), "v": str(dict["value"])})

            if uri[1] == "infractions":
                stats["infractions"].append({"t": str(timestamp), "v": str(dict["value"])})

            jsonFile = open("stats.json", "w+")
            jsonFile.write(json.dumps(stats, indent=4))
            jsonFile.close()

        # Now insert new info in catalog
        #catalog = self.updateJsonFile(dict)
        # print("The data {} has been posted".format(dict))
        if uri[1]== "chatID" : 
            return json.dumps({"name":catalog["usersList"]["userName"]})
        elif uri[1] == 'holidays':
            result={}
            for house in catalog["usersList"][user]["houses"]:
                result[house]=(catalog["usersList"][user]["houses"][house]["holidays"])
            return json.dumps(result)

    def PUT(self,*uri,**params):
        # Modify information
        
        if len(uri)!=0 and uri[0] == 'catalog':
            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "heaters_status":
                user = uri[2]
                house = uri[3]
                room = uri[4]
                status = params["status"]
                catalog["usersList"][user]["houses"][house]["rooms"][room]["HeatersStatus"] = str(status)

            if uri[1] == "windows_status":
                user = uri[2]
                house = uri[3]
                room = uri[4]
                status = params["status"]
                catalog["usersList"][user]["houses"][house]["rooms"][room]["WindowsStatus"] = str(status)
                

            if uri[1] == "threshold_temperature":
                #print("Setting new temperature thresholds...")
                user = uri[2]
                house = uri[3]
                room = uri[4]
                threshold_min = params["threshold_min"]
                threshold_max = params["threshold_max"]
                catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_min_temperature"] = threshold_min
                catalog["usersList"][user]["houses"][house]["rooms"][room]["threshold_max_temperature"] = threshold_max
                

        #Now modify info in the catalog...

        jsonFile = open("catalog.json", "w+")
        jsonFile.write(json.dumps(catalog, indent=4))
        jsonFile.close()

        #print("The data {} has been put".format(catalog))
        if uri[1] == 'holidays':
            result={}
            for house in catalog["usersList"][params["user"]]["houses"]:
                result[house]=(catalog["usersList"][params["user"]]["houses"][house]["holidays"])
            return json.dumps(result)
        

    def DELETE(self,*uri,**params):
        if len(uri)!=0 and uri[0] == 'catalog':
            with open('catalog.json') as json_file:
                catalog = json.load(json_file)
                json_file.close()

            if uri[1] == "holidays":
                user = uri[3]
                house = uri[4]
                if uri[2] == "selected":
                    id = json.loads(params["id"])
                    for holidayID in id:
                        catalog["usersList"][user]["houses"][house]["holidays"].pop(holidayID)
                elif uri[2] == "all":
                    catalog["usersList"][user]["houses"][house]["holidays"]={"holidaysIndex":0}
                jsonFile = open("catalog.json", "w+")
                jsonFile.write(json.dumps(catalog, indent=4))
                jsonFile.close()
                result={}
                for house in catalog["usersList"][user]["houses"]:
                    result[house]=(catalog["usersList"][user]["houses"][house]["holidays"])
                return json.dumps(result)





if __name__=="__main__":

    conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher()
        }
    }
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1', 'server.socket_port': 8080
    })
    webapp= WebCatalogManager()
    cherrypy.tree.mount(webapp,'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


    #cherrypy.quickstart(webapp, '/', conf)