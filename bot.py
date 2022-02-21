import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *

class InfractionBot:
    def __init__(self, broker, port, topic):
        self.pwdProcedure = False
        # Local token
        self.tokenBot = "5106415050:AAGwWncLft1vKjqgAabZFLODIdXN9K03Kvc"
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBot", broker, port, self)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          }
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()

    def start(self):
        self.client.start()

    def subscribe(self, topic):
        self.client.mySubscribe(topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        self.value = d['e']["v"]
        timestamp = d["e"]['t']
        id = topic.split("/")
        userID = id[1]
        houseID = id[2]
        print(f'The alarm of {userID}\'s {houseID} is measuring {self.value} at time {timestamp} an infraction')
        if self.value:
            self.send_message(self.value,userID,houseID)

    def send_message(self,msg,user,house):
        chatIDs = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+house)).json())["chatID"]
        username = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+house)).json())["username"]
        for chatID in chatIDs :
            self.bot.sendMessage(chatID, text=f'Infraction in {username}\'s house, please get in touch with the proprietary,'
                                              f'in case of danger do not act alone, call 112.')




    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if self.pwdProcedure == False:
            if message == "/start":
                all_chatIDs = (requests.get('http://127.0.0.1:8080/catalog/all_chatIDs').json())["all_chatIDs"]
                if chat_ID in all_chatIDs :
                    self.bot.sendMessage(chat_ID, text="Contact already registered,"
                                                       " if you want to add a house, type corresponding password")
                    self.pwdProcedure = True

                else :
                    self.bot.sendMessage(chat_ID, text="Type password to register to a house")
                    self.pwdProcedure = True
                    
                return 0

            else:
                self.bot.sendMessage(chat_ID, text="Command not supported")
        else:
            dict_result = requests.get('http://127.0.0.1:8080/catalog/evaluate_password?password='+message).json()
            password_correct, user, house = dict_result["correct"], dict_result["user"], dict_result["house"]
            if password_correct == True :
                requests.post('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+house,json.dumps({"chatID":chat_ID}))
                username = ((requests.get('http://127.0.0.1:8080/catalog/chatID/'+user+'/'+house)).json())["username"]
                self.bot.sendMessage(chat_ID, text="Procedure of identification completed ! "
                                                    "You will be alerted in case of infraction in "
                                                    + username + "'s house")
            else:
                self.bot.sendMessage(chat_ID, text="Wrong password, type /start to retry")
            self.pwdProcedure = False

if __name__ == "__main__":
    mqtt_details = (requests.get('http://127.0.0.1:8080/catalog/mqtt_details')).json()
    broker = mqtt_details["broker"]
    port = int(mqtt_details["port"])
    topics = (requests.get('http://127.0.0.1:8080/catalog/all_topics?program=controller&type=infraction').json())["value"]

    ssb = InfractionBot(broker, port, topics)
    for topic in topics:
        ssb.subscribe(topic)
    #sb=SwitchBot(token,broker,port,topic)

    print("Bot started ...")
    i=0
    while True:
        time.sleep(5)
