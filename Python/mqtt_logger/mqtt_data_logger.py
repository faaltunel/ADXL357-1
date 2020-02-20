#!c:\python34\python.exe
#!/usr/bin/env python
# If Running in Windows use top line and edit according to your python
# location and version. If running on Linux delete the top line.
###demo code provided by Steve Cope at www.steves-internet-guide.com
##email steve@steves-internet-guide.com
###Free to use for any purpose
"""
This will log messages to file.Los time,message and topic as JSON data
"""
# updated 28-oct-2018
mqttclient_log = False  # MQTT client logs showing messages
Log_worker_flag = True
import paho.mqtt.client as mqtt
import json
import os
import time
import sys, getopt, random
import logging
import mlogger as mlogger
import threading
from queue import Queue
from command import command_input
import command
import sys

q = Queue()

##helper functions
def convert(t):
    d = ""
    for c in t:  # replace all chars outside BMP with a !
        d = d + (c if ord(c) < 0x10000 else "!")
    return d


###


class MQTTClient(mqtt.Client):  # extend the paho client class
    run_flag = False  # global flag used in multi loop

    def __init__(self, cname, **kwargs):
        super(MQTTClient, self).__init__(cname, **kwargs)
        self.last_pub_time = time.time()
        self.topic_ack = []  # used to track subscribed topics
        self.run_flag = True
        self.submitted_flag = False  # used for connections
        self.subscribe_flag = False
        self.bad_connection_flag = False
        self.bad_count = 0
        self.connected_flag = False
        self.connect_flag = False  # used in multi loop
        self.disconnect_flag = False
        self.disconnect_time = 0.0
        self.pub_msg_count = 0
        self.pub_flag = False
        self.sub_topic = ""
        self.sub_topics = []  # multiple topics
        self.sub_qos = 0
        self.devices = []
        self.broker = ""
        self.port = 1883
        self.keepalive = 60
        self.run_forever = False
        self.cname = ""
        self.delay = 10  # retry interval
        self.retry_time = time.time()


def Initialise_clients(cname, mqttclient_log=False, cleansession=True, flags=""):
    # flags set
    #print("initialising clients")
    logging.info("initialising clients")
    client = MQTTClient(cname, clean_session=cleansession)
    client.cname = cname
    client.on_connect = on_connect  # attach function to callback
    client.on_message = on_message  # attach function to callback
    # client.on_disconnect=on_disconnect
    # client.on_subscribe=on_subscribe
    if mqttclient_log:
        client.on_log = on_log
    return client


def on_connect(client, userdata, flags, rc):
    """
    set the bad connection flag for rc >0, Sets onnected_flag if connected ok
    also subscribes to topics
    """
    logging.debug(
        "Connected flags: " + str(flags) + " result code " + str(rc) + options["cname"]
    )
    if rc == 0:

        client.connected_flag = True  # old clients use this
        client.bad_connection_flag = False
        if client.sub_topic != "":  # single topic
            logging.debug("subscribing " + str(client.sub_topic))
            logging.debug("subscribing in on_connect")
            topic = client.sub_topic
            if client.sub_qos != 0:
                qos = client.sub_qos
            client.subscribe(topic, qos)
        elif client.sub_topics != "":
            # print("subscribing in on_connect multiple")
            client.subscribe(client.sub_topics)

    else:
        logging.debug("set bad connection flag")
        client.bad_connection_flag = True  #
        client.bad_count += 1
        client.connected_flag = False  #


def on_message(client, userdata, msg):
    topic = msg.topic
    m_decoded = str(msg.payload.decode("utf-8", "ignore"))
    message_handler(client, m_decoded, topic)
    # print("message received")


def message_handler(client, msg, topic):
    data = dict()
    tnow = time.localtime(time.time())
    # m=time.asctime(tnow)+" "+topic+" "+msg
    try:
        msg = json.loads(msg)  # convert to Javascript before saving
        # print("json data")
    except:
        pass
        # print("not already json")
    data["time"] = tnow
    data["topic"] = topic
    data["message"] = msg
    if command.options["storechangesonly"]:
        if has_changed(client, topic, msg):
            client.q.put(data)  # put messages on queue
    else:
        client.q.put(data)  # put messages on queue


def has_changed(client, topic, msg):
    topic2 = topic.lower()
    if topic2.find("control") != -1:
        return False
    if topic in client.last_message:
        if client.last_message[topic] == msg:
            return False
    client.last_message[topic] = msg
    return True


###
def log_worker():
    """runs in own thread to log data from queue"""
    while Log_worker_flag:
        time.sleep(0.01)
        while not q.empty():
            results = q.get()
            if results is None:
                continue
            if options["JSON"]:
                log.log_json(results)
            elif options["JSON_MESSAGE_ONLY"]:
                log.log_json(results["message"])
            else:
                log.log_data(results)
            # print("message saved ",results["message"])
    log.close_file()


# MAIN PROGRAM
options = command.options

if __name__ == "__main__" and len(sys.argv) >= 2:
    options = command_input(options)
else:
    logging.warning("Need broker name and topics to continue.. exiting")
    raise SystemExit(1)

logging.getLogger().setLevel(options["loglevel"])
if not options["cname"]:
    r = random.randrange(1, 10000)
    cname = "logger-" + str(r)
else:
    cname = "logger-" + str(options["cname"])
log_dir = options["log_dir"]
log_records = options["log_records"]
number_logs = options["number_logs"]
log = mlogger.m_logger(log_dir, log_records, number_logs)  # create log object
logging.info("Log Directory = " + log_dir)
logging.info("Log records per log = " + str(log_records))
if number_logs == 0:
    logging.info("Max logs = Unlimited")
else:
    logging.info("Max logs  = " + number_logs)


logging.info("Creating client " + cname)
logging.info("Created client with QoS of: " + str(options["QoS"]))

client = Initialise_clients(
    cname, mqttclient_log, False
)  # create and initialise client object
if options["username"] != "":
    client.username_pw_set(options["username"], options["password"])

client.sub_topics = options["topics"]
client.broker = options["broker"]
client.port = options["port"]
# options["JSON"]=True #currently only supports JSON
if options["JSON"]:
    logging.info("Logging JSON format")
elif options["JSON_MESSAGE_ONLY"]:
    logging.info("Logging JSON format message only")
else:
    logging.info("Logging plain text")
if options["storechangesonly"]:
    logging.info("starting storing only changed data")
else:
    logging.info("starting storing all data")

##
# Log_worker_flag=True
t = threading.Thread(target=log_worker)  # start logger
t.start()  # start logging thread
###

client.last_message = dict()
client.q = q  # make queue available as part of client


try:
    res = client.connect(client.broker, client.port)  # connect to broker
    client.loop_start()  # start loop

except:
    logging.debug("connection to " + client.broker + " failed")
    raise SystemExit("connection failed")
try:
    while True:
        time.sleep(1)
        pass

except KeyboardInterrupt:
    logging.info("interrrupted by keyboard")

client.loop_stop()  # start loop
Log_worker_flag = False  # stop logging thread
#time.sleep(5)

