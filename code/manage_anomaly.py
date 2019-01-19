import datetime
import numpy as np
import threading
import time
import math
from anomaly import Anomaly 
from pymongo import MongoClient
from pprint import pprint


class AnomalyManager():
    max_time_gap = 2*60 
    priority_th = 0.5
    confi_th1 = 0.95
    confi_th2 = 0.98
    count_th1 = 2
    count_th2 = 10

    small_period = 2
    large_period = 4 

    confi_high_th = 0.95
    confi_low_th = 0.85
    th_period = 1
    th_exp_para = 0.05

    # Alert Severity Table
    AST = {"PACKET_IAT": 0,
           "PACKET_BYTES": 0,
           "NEW_ORIG": 2,
           "NEW_RESP": 2,
           "NEW_PROTOCOL": 2,
           "NEW_SERVICE": 2,
           "PACKET_AB_TOO_MANY": 2,
           "PACKET_AB_TOO_FEW": 1,
           "PACKET_BA_TOO_MANY": 2,
           "PACKET_BA_TOO_FEW": 1,
           "MEAN_BYTES_AB_TOO_LARGE": 1,
           "MEAN_BYTES_AB_TOO_SMALL": 0,
           "STD_BYTES_AB_TOO_LARGE": 0,
           "MEAN_BYTES_BA_TOO_LARGE": 1,
           "MEAN_BYTES_BA_TOO_SMALL": 0,
           "STD_BYTES_BA_TOO_LARGE": 0,
           "MEAN_IAT_AB_TOO_LARGE": 1,
           "MEAN_IAT_AB_TOO_SMALL": 1,
           "STD_IAT_AB_TOO_LARGE": 0,
           "MEAN_IAT_BA_TOO_LARGE": 1,
           "MEAN_IAT_BA_TOO_SMALL": 1,
           "STD_IAT_BA_TOO_LARGE": 0,
           "OPERATION_TOO_LATE": 1,
           "OPERATION_TOO_EARLY": 1,
           "OPERATION_MISSING": 2,
           "INVALID_FUNCTION_CODE": 2,
           "RESPONSE_FROM_ORIG": 2,
           "REQUEST_FROM_RESP": 2,
           "NEW_OPERATION": 2,
           "BINARY_FAULT": 2,
           "ANALOG_TOO_LARGE": 1,
           "ANALOG_TOO_SMALL": 1}


    # Critical Node List
    CNL = ["100.0.0.3"]

    pi = np.array([0.6, 0.4])

    # Alert Type Sevrity
    CPT1 = np.array([[0.6, 0.3, 0.1], [0.2, 0.35, 0.45]])
    # Confidence Score
    CPT2 = np.array([[0.6, 0.3, 0.1], [0.15, 0.35, 0.5]])
    # Alert Count
    CPT3 = np.array([[0.25, 0.3, 0.45], [0.45, 0.3, 0.25]])
    # Critical Node
    CPT4 = np.array([[0.2, 0.8], [0.55, 0.45]])
    # Critical Operation
    CPT5 = np.array([[0.1, 0.5, 0.4], [0.25, 0.15, 0.5]])

    
    def __init__(self, meta_alert_queue):
        self.meta_alert_queue = meta_alert_queue
        self.client = MongoClient()
        self.client.drop_database("alert_database")
        self.alert_db = self.client.alert_database 
        
        self.fast_timer = threading.Timer(self.small_period, self.sendHighPriorityAlert)
        self.fast_timer.start()
        self.slow_timer = threading.Timer(self.large_period, self.sendLowPriorityAlert)
        self.slow_timer.start()
        self.do_run = True
        
        self.current_confi_th = self.confi_high_th
        self.update_amount = (self.confi_high_th - self.confi_low_th) / 300
        self.th_timer = threading.Timer(self.th_period, self.updateThreshold)
        self.th_timer.start()
        

    def stop(self):
        self.do_run = False

    def sendHighPriorityAlert(self):
        #print("High")
        if self.do_run:
            send_list = self.alert_db.high_priority.find()
            for alert_to_send in send_list:
                self.meta_alert_queue.put_nowait(alert_to_send)
            self.alert_db.high_priority.remove({})

            self.fast_timer = threading.Timer(self.small_period, self.sendHighPriorityAlert)
            self.fast_timer.start()


    def sendLowPriorityAlert(self):
        #print("Low")
        if self.do_run:
            send_list = self.alert_db.low_priority.find()
            for alert_to_send in send_list:
                self.meta_alert_queue.put_nowait(alert_to_send)
            self.alert_db.low_priority.remove({})
 
            self.slow_timer = threading.Timer(self.large_period, self.sendLowPriorityAlert)
            self.slow_timer.start()


    def updateThreshold(self):
        if self.do_run:
            self.current_confi_th = min(self.confi_high_th, self.current_confi_th + self.update_amount) 
            #print("Current Confidence Threshold: " + str(self.current_confi_th))
        
            self.th_timer = threading.Timer(self.th_period, self.updateThreshold)
            self.th_timer.start()
 

    def insertAlert(self, anomaly):
        print(anomaly)
        alerts = self.alert_db.alert
        alert_id = alerts.insert_one(anomaly.getDict()).inserted_id
        #alert = alerts.find_one({"_id": alert_id})
        #print(type(alert))


    def createMetaAlert(self, anomaly):
        meta_alert = anomaly.getDict()
        meta_alert["ts"] = [meta_alert["ts"], meta_alert["ts"]]
        meta_alert["count"] = 1

        priority_score = self.calculatePriority(meta_alert)

        return meta_alert


    def updateMetaAlert(self, anomaly, meta_alert):
        if anomaly.getTS() > meta_alert["ts"][1]:
            meta_alert["current"] = anomaly.getCurrent()
            meta_alert["mean"] = anomaly.getMean()
            meta_alert["dev"] = anomaly.getDev()
            if anomaly.getAnomalyType() == "packet":
                meta_alert["packet"] = anomaly.getPacket().getDict()
            elif anomaly.getAnomalyType() == "flow":
                meta_alert["flow"] = anomaly.getFlow().getDict()
            elif anomaly.getAnomalyType() == "operation":
                meta_alert["operation"] = anomaly.getOperation().getDict()
            elif anomaly.getAnomalyType() == "measurement":
                meta_alert["measurement"] = anomaly.getMeasurement().getDict()
        meta_alert["ts"][0] = min(meta_alert["ts"][0], anomaly.getTS()) 
        meta_alert["ts"][1] = max(meta_alert["ts"][1], anomaly.getTS()) 
        meta_alert["confi"] = max(meta_alert["confi"], anomaly.getConfi())
        meta_alert["count"] += 1

        return meta_alert


    def aggregate(self, anomaly):
        self.insertAlert(anomaly)
        meta_alerts = self.alert_db.meta_alert
        dest_meta_alert = None
        candidates = meta_alerts.find({"desp": anomaly.getDesp(),
                                       "index": anomaly.getIndex()})
        for candidate in candidates:
            if (anomaly.getTS() > candidate["ts"][0] - self.max_time_gap or
                anomaly.getTS() < candidate["ts"][1] + self.max_time_gap):
                dest_meta_alert = candidate
                break

        if dest_meta_alert == None:
            new_meta_alert = self.createMetaAlert(anomaly) 
        else:
            new_meta_alert = self.updateMetaAlert(anomaly, dest_meta_alert)

        return new_meta_alert


    def alertTypeSeverity(self, meta_alert):
        if self.AST[meta_alert["desp"]] == 0:
            return np.array([1, 0, 0])
        elif self.AST[meta_alert["desp"]] == 1:
            return np.array([0, 1, 0])
        else:
            return np.array([0, 0, 1])
    

    def confidenceScore(self, meta_alert):
        if meta_alert["confi"] < self.confi_th1:
            return np.array([1, 0, 0])
        elif meta_alert["confi"] < self.confi_th2:
            return np.array([0, 1, 0])
        else:
            return np.array([0, 0, 1]) 


    def alertCount(self, meta_alert):
        if meta_alert["count"] < self.count_th1:
            return np.array([1, 0, 0])
        elif meta_alert["count"] < self.count_th2:
            return np.array([0, 1, 0])
        else:
            return np.array([0, 0, 1])


    def isCriticalNode(self, meta_alert):
        yes = np.array([1, 0])
        no = np.array([0, 1])
        if (meta_alert["anomaly_type"] == "packet" and 
            (meta_alert["packet"]["sender"] in self.CNL or
            meta_alert["packet"]["receiver"] in self.CNL)):
            return yes
        if (meta_alert["anomaly_type"] == "flow" and 
            (meta_alert["flow"]["orig"] in self.CNL or
            meta_alert["flow"]["resp"] in self.CNL)):
            return yes
        if (meta_alert["anomaly_type"] == "operation" and 
            (meta_alert["operation"]["orig_ip"] in self.CNL or
            meta_alert["operation"]["resp_ip"] in self.CNL)):
            return yes
        if (meta_alert["anomaly_type"] == "measurement" and 
            meta_alert["measurement"]["holder_ip"] in self.CNL):
            return yes
        return no


    def isCriticalOperation(self, meta_alert):
        yes = np.array([1, 0, 0])
        no = np.array([0, 1, 0])
        unknown = np.array([0, 0, 1])
        if (meta_alert["anomaly_type"] == "packet" or
            meta_alert["anomaly_type"] == "flow" or
            meta_alert["anomaly_type"] == "measurement"):
            return unknown 
        else:
            if meta_alert["operation"]["service"] == "DNP3":
                fc = meta_alert["operation"]["fc"]
                if (fc >= 2 and fc <= 6 or
                    fc >= 13 and fc <= 14 or
                    fc >= 16 and fc <= 21 or
                    fc >= 24 and fc <= 31):
                    return yes
                else:
                    return no
            else:
                return unknown


    def calculatePriority(self, meta_alert):
        # Alert Type Severity
        lambda1 = np.dot(self.CPT1, self.alertTypeSeverity(meta_alert))
        lambda_total = lambda1
        # Confidence Score
        lambda2 = np.dot(self.CPT2, self.confidenceScore(meta_alert))
        lambda_total = np.multiply(lambda_total, lambda2)
        # Alert Count
        lambda3 = np.dot(self.CPT3, self.alertCount(meta_alert))
        lambda_total = np.multiply(lambda_total, lambda3)
        # Critical Node
        lambda4 = np.dot(self.CPT4, self.isCriticalNode(meta_alert))
        lambda_total = np.multiply(lambda_total, lambda4)
        # Cirital Operation
        lambda5 = np.dot(self.CPT5, self.isCriticalOperation(meta_alert))
        lambda_total = np.multiply(lambda_total, lambda5)

        believe = np.multiply(self.pi, lambda_total)
        believe = believe / believe.sum(0)

        #pprint(meta_alert)
        #print(believe[1])
        #print("")

        return believe[1]


    def scheduleAlert(self, meta_alert):
        meta_alerts = self.alert_db.meta_alert
        priority_score = self.calculatePriority(meta_alert) 
        if "_id" in meta_alert.keys():
            pre_priority_score = meta_alert["priority_score"]
            meta_alert["priority_score"] = priority_score
            meta_alerts.replace_one({"_id": meta_alert["_id"]}, meta_alert)
            if priority_score > self.priority_th:
                if pre_priority_score <= self.priority_th:
                    self.meta_alert_queue.put_nowait(meta_alert)
                self.alert_db.high_priority.replace_one({"_id": meta_alert["_id"]},
                                                        meta_alert,
                                                        True)
            else:
                self.alert_db.low_priority.replace_one({"_id": meta_alert["_id"]},
                                                       meta_alert,
                                                       True)
        else:
            meta_alert["priority_score"] = priority_score
            new_id = meta_alerts.insert_one(meta_alert).inserted_id
            meta_alert["_id"] = new_id 
            if priority_score > self.priority_th:
                self.meta_alert_queue.put_nowait(meta_alert)
                self.alert_db.high_priority.insert_one(meta_alert)
            else:
                self.alert_db.low_priority.insert_one(meta_alert)
 
        #pprint(meta_alert)
        #print("")


    def manage(self, anomaly):
        if anomaly.getConfi() > self.current_confi_th:
            self.current_confi_th = self.confi_low_th + (
                (self.current_confi_th - self.confi_low_th) * math.exp(-self.th_exp_para)
            )
            meta_alert = self.aggregate(anomaly)
            self.scheduleAlert(meta_alert)


    def print_alerts(self):
        alerts = self.alert_db.alert
        meta_alerts = self.alert_db.meta_alert
        print("Alert Number: " + str(alerts.count()))
        print("Meta-Alert Number: " + str(meta_alerts.count()))
 
        for meta_alert in meta_alerts.find():
            print("")
            pprint(meta_alert)
