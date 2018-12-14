import numpy as np 
import math

UPDATE_TH = 0.95

def sigmoid(x): 
    return 2 * (1 / (1 + math.exp(-x)) - 0.5) 


def anomaly_score(x, mean, std):
    return (1 - std**2/(x-mean)**2)**2


class IncMeanSTD():
    def __init__(self, norm):
        self.norm = norm 
        self.total = 0
        self.mean = None
        self.std = None
        self.S = None
        self.last = None


    def detect(self, x):
        if self.total >= 2 and abs(x-self.mean) > self.std:
            if x > self.mean:
                rst = 1
            else:
                rst = -1
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.mean, self.std)
        else:
            rst = 0
            confi = 1

        return (rst, confi, self.mean, self.std)


    def update(self, x, always_update=False):
        rst, confi, mean, std = self.detect(x)

        if always_update or rst == 0 or confi < UPDATE_TH:
            self.total += 1
            if self.total == 1:
                self.last = x 
                self.mean = self.last
                self.S = 0
            else:
                new_mean = self.mean+(x-self.mean)/self.total
                self.S += (x-self.mean)*(x-new_mean)
                self.std = math.sqrt(self.S/(self.total-1))
                self.mean = new_mean

        return (rst, confi, self.mean, self.std)


    def check(self, x):
        rst = 0
        confi = 1
        if self.total >= 2 and x-self.mean > self.std:
            rst = 1
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.mean, self.std)

        return (rst, confi, self.mean, self.std)


    def getTotal(self):
        return self.total


    def getMean(self):
        return self.mean


    def getSTD(self):
        return self.std


    def __str__(self):
        return "mean: {0}, std: {1}, count: {2}".format(self.mean, self.std, self.total)


class ExpMeanSTD():
    def __init__(self, norm, alpha):
        self.norm = norm 
        self.total = 0
        self.alpha = alpha
        self.mean = None
        self.variance = None
        self.max = None
        self.min = None


    def detect(self, x):
        if self.total >= 2 and abs(x-self.mean) > self.getSTD():
            if x > self.mean:
                rst = 1
            else:
                rst = -1
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.mean, self.getSTD())
        else:
            rst = 0
            confi = 1

        return (rst, confi, self.mean, self.getSTD())


    def update(self, x, always_update=False):
        if x == None:
            return (0, 1, self.mean, self.getSTD())

        rst, confi, mean, std = self.detect(x)

        if always_update or rst == 0 or confi < UPDATE_TH:
            self.total += 1
            if self.total == 1:
                self.mean = x 
                self.variance = 0
                self.max = x
                self.min = x
            else:
                diff = x - self.mean
                incr = self.alpha * diff
                self.mean = self.mean + incr
                self.variance = (1 - self.alpha) * (self.variance + diff * incr)
                self.max = max(self.max, x)
                self.min = min(self.min, x)

        return (rst, confi, self.mean, self.getSTD())


    def check(self, x):
        rst = 0
        confi = 1
        if self.total >= 2 and x-self.mean > self.getSTD():
            rst = 1
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.mean, self.getSTD())

        return (rst, confi, self.mean, self.getSTD())


    def getTotal(self):
        return self.total


    def getMean(self):
        return self.mean


    def getSTD(self):
        if self.variance == None:
            return None
        return math.sqrt(abs(self.variance))


    def getMax(self):
        return self.max


    def getMin(self):
        return self.min


    def __str__(self):
        return "mean: {0}, std: {1}, count: {2}".format(self.mean, self.getSTD(), self.total)


class IncAdaptMeanSTD():
    def __init__(self, norm, adapt_num):
        self.norm = norm 
        self.adapt_num = adapt_num
        self.total = 0
        self.current_total = 0
        self.pre_mean = None
        self.pre_std = None
        self.mean = None
        self.std = None
        self.S = None
        self.last = None


    def detect(self, x):
        if x != None and self.total >= 2 and abs(x-self.getMean()) > self.getSTD():
            if x > self.getMean():
                rst = 1
            else:
                rst = -1
            num = min(self.adapt_num, self.total)
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.getMean(), self.getSTD())
        else:
            rst = 0
            confi = 1

        return (rst, confi, self.getMean(), self.getSTD())


    def update(self, x, always_update=False):
        rst, confi, mean, std = self.detect(x)

        if x != None and (always_update or rst == 0 or confi < UPDATE_TH):
            self.total += 1
            self.current_total += 1
            if self.current_total == 1:
                self.last = x 
                self.mean = self.last
                self.S = 0
            else:
                new_mean = self.mean+(x-self.mean)/self.total
                self.S += (x-self.mean)*(x-new_mean)
                self.std = math.sqrt(self.S/(self.total-1))
                self.mean = new_mean

            if self.current_total == self.adapt_num:
                self.pre_mean = self.mean
                self.pre_std = self.std
                self.current_total = 0

        return (rst, confi, self.getMean(), self.getSTD())


    def check(self, x):
        rst = 0
        confi = 1
        if self.total >= 2 and x-self.getMean() > self.getSTD():
            rst = 1
            confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.getMean(), self.getSTD())

        return (rst, confi, self.getMean(), self.getSTD())


    def getTotal(self):
        return self.total


    def getMean(self):
        if self.pre_mean == None:
            return self.mean
        else:
            return self.pre_mean


    def getSTD(self):
        if self.pre_std == None:
            return self.std
        else:
            return self.pre_std


    def __str__(self):
        return "mean: {0}, std: {1}, count: {2}".format(self.getMean(), self.getSTD(), self.getTotal())



class PeriodicExpMeanSTD():
    def __init__(self, norm, period_len, slot_len):
        self.period_len = period_len
        self.slot_len = slot_len
        self.slot_num = period_len/slot_len 
        self.slots = [ ExpMeanSTD(norm, 0.02) for i in range(self.slot_num)]


    def getIndex(self, ts):
        ts = int(round(ts))
        return (ts % self.period_len) / self.slot_len


    def detect(self, x, ts):
        return self.slots[self.getIndex(ts)].detect(x)


    def update(self, x, ts, always_update=False):
        return self.slots[self.getIndex(ts)].update(x, always_update) 
        

    def getTotal(self, ts):
        return self.slots[self.getIndex(ts)].getTotal() 


    def getMean(self, ts):
        return self.slots[self.getIndex(ts)].getMean()


    def getSTD(self, ts):
        return self.slots[self.getIndex(ts)].getSTD()


    def getMaxDiff(self):
        maxDiff = 0
        for i in range(self.slot_num):
            slot_max = self.slots[i].getMax()
            slot_min = self.slots[i].getMin()
            if slot_max == None or slot_min == None:
                return None
            diff = self.slots[i].getMax() - self.slots[i].getMin()
            #print(str(i) + ": " + str(diff))
            maxDiff = max(maxDiff, diff)

        return maxDiff


    def getMaxSTDRatio(self):
        maxSTDRatio = 0
        for i in range(self.slot_num):
            std = self.slots[i].getSTD()
            mean = self.slots[i].getMean()
            if std == None:
                return None
            if mean == 0:
                return None
            maxSTDRatio = max(maxSTDRatio, std/mean)

        return maxSTDRatio


    def __str__(self):
        rst = ""
        for i in range(self.slot_num):
            rst += "index: {0}, {1}\n".format(i, str(self.slots[i]))
        return rst


class Unknown():
    def __init__(self, norm):
        self.norm = norm 
        self.total = 0
        self.mean = None
        self.max= None
        self.min = None


    def detect(self, x):
        rst = 0
        confi = 1
        diff = None

        if self.total > 0:
            if x > self.getMax():
                rst = 1
                diff = self.getMax()-self.getMean()
                confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.getMean(), diff)
            if x < self.getMin():
                rst = -1
                diff = self.getMax()-self.getMean()
                confi = sigmoid(self.total/self.norm) * anomaly_score(x, self.getMean(), diff)

        return (rst, confi, self.mean, diff)


    def update(self, x, always_update=False):
        rst, confi, mean, diff = self.detect(x)

        if always_update or rst == 0 or confi < UPDATE_TH:
            self.total += 1
            if self.total == 1:
                self.mean = x 
                self.max = x 
                self.min = x
            else:
                self.mean = self.getMean()+(x-self.getMean())/self.total
                self.max = max(self.getMax(), x)
                self.min = min(self.getMin(), x) 

        return (rst, confi, self.mean, diff)


    def getTotal(self):
        return self.total


    def getMean(self):
        return self.mean


    def getMax(self):
        return self.max


    def getMin(self):
        return self.min


    def __str__(self):
        return "mean: {0}, max: {1}, min: {2}, count: {3}".format(self.getMean(), self.getMax(), self.getMin(), self.getTotal())


class Analog():
    freq_ratio_th = 0.005
    volt_ratio_th = 0.05
    periodic_per = 0.5
    periodic_ratio_th = 0.2

    pi = np.array([0.25, 0.25, 0.25, 0.25])

    believe_th = 0.7

    # isAround60
    CPT1 = np.array([[0.99, 0.01], [0.01, 0.99], [0.01, 0.99], [0.01, 0.99]])
    # STDRatio [low, medium, high]
    CPT2 = np.array([[0.98, 0.01, 0.01], [0.4, 0.55, 0.05], [0.01, 0.19, 0.8], [0.1, 0.1, 0.8]])
    # isPeriodic
    CPT3 = np.array([[0.01, 0.69, 0.3], [0.01, 0.69, 0.3], [0.6, 0.1, 0.3], [0.1, 0.6, 0.3]])


    def __init__(self, norm, period_len, slot_len):
        self.norm = norm 
        self.total = 0
        self.type = "Unidentified"
        self.type_confi = 1
        self.inc_mean_std = IncMeanSTD(norm) 
        self.exp_mean_std = ExpMeanSTD(norm, 0.02) 
        self.periodic_exp_mean_std = PeriodicExpMeanSTD(norm, period_len, slot_len) 
        self.unknown = Unknown(norm) 


    def detect(self, x, ts):
        if self.type == "Frequency" or self.type == "Voltage":
            return self.exp_mean_std.detect(x)
        elif self.type == "Current/Power":
            return self.periodic_exp_mean_std.detect(x, ts)
        else:
            return self.unknown.detect(x)


    def update(self, x, ts, always_update=False):
        if self.type == "Frequency" or self.type == "Voltage" or self.type == "Unidentified":
            rst1, confi1, mean1, diff1 = self.exp_mean_std.update(x, always_update)
        if self.type == "Current/Power" or self.type == "Unidentified":
            rst2, confi2, mean2, diff2 = self.periodic_exp_mean_std.update(x, ts, always_update)
        if self.type == "Unidentified":
            self.inc_mean_std.update(x, always_update)
            rst3, confi3, mean3, diff3 = self.unknown.update(x, always_update)

        self.total += 1
        if self.type == "Unidentified" and self.total > 180 and self.total % 30 == 0:
            self.identify()

        if self.type == "Frequency" or self.type == "Voltage":
            return (rst1, confi1, mean1, diff1)
        elif self.type == "Current/Power":
            return (rst2, confi2, mean2, diff2)
        else:
            return (rst3, confi3, mean3, diff3)


    def getTotal(self):
        return self.total


    def getMean(self):
        if self.inc_mean_std != None:
            return self.inc_mean_std.getMean()
        else:
            return None


    def getSTD(self):
        if self.inc_mean_std != None:
            return self.inc_mean_std.getSTD()
        else:
            return None


    def getMax(self):
        if self.unknown != None:
            return self.unknown.getMax() 
        else:
            return None


    def getMin(self):
        if self.unknown != None:
            return self.unknown.getMin()
        else:
            return None

    def getDiff(self):
        if self.unknown != None:
            return self.getMax() - self.getMin()
        else:
            return None 


    def getType(self):
        return self.type


    def getTypeConfi(self):
        return self.type_confi


    # 0 = True, 1 = False, 2 = Unknown
    def isAround60(self):
        if self.getMean() > 59 and self.getMean() < 61:
            return np.array([1, 0]) 
        else:
            return np.array([0, 1]) 

    
    def STDRatio(self, threshold1, threshold2):
        std = self.getSTD()
        mean = self.getMean()
        if mean == 0:
            if std == 0:
                return np.array([1, 0, 0]) 
            else:
                return np.array([0, 0, 1]) 
        
        ratio = std / abs(mean)
        if ratio < threshold1:
            return np.array([1, 0, 0]) 
        elif ratio < threshold2:
            return np.array([0, 1, 0]) 
        else:
            return np.array([0, 0, 1])


    def isPeriodic(self, percentage, threshold):
        maxDiff = self.periodic_exp_mean_std.getMaxDiff()
        maxSTDRatio = self.periodic_exp_mean_std.getMaxSTDRatio()
        #print(maxDiff)
        #print(self.getDiff())
        #print(maxSTDRatio)
        if maxDiff == None or maxSTDRatio == None:
            return np.array([0, 0, 1]) 
        elif maxDiff < self.getDiff() * percentage and maxSTDRatio < threshold:
            return np.array([1, 0, 0]) 
        else:
            return np.array([0, 1, 0]) 


    def identify(self):
        # isAround60
        lambda1 = np.dot(self.CPT1, self.isAround60())
        lambda_total = lambda1
        #print("isAround60: " + str(self.isAround60()))
        # STDRatio
        lambda2 = np.dot(self.CPT2, self.STDRatio(self.freq_ratio_th, self.volt_ratio_th))
        lambda_total = np.multiply(lambda_total, lambda2)
        #print("STDRatio: " + str(self.STDRatio(self.freq_ratio_th, self.volt_ratio_th)))
        # isPeriodic
        lambda3 = np.dot(self.CPT3, self.isPeriodic(self.periodic_per, self.periodic_ratio_th))
        lambda_total = np.multiply(lambda_total, lambda3)
        #print("isPeriodic: " + str(self.isPeriodic(self.periodic_per, self.periodic_ratio_th)))

        believe = np.multiply(self.pi, lambda_total)
        believe = believe/believe.sum(0) 

        if believe[0] > self.believe_th:
            self.type = "Frequency"
            self.type_confi = believe[0]
            self.inc_mean_std = None
            self.periodic_inc_mean_std = None
            self.unknown = None
        elif believe[1] > self.believe_th:
            self.type = "Voltage"
            self.type_confi = believe[1]
            self.inc_mean_std = None
            self.periodic_inc_mean_std = None
            self.unknown = None
        elif believe[2] > self.believe_th:
            self.type = "Current/Power"
            self.type_confi = believe[2]
            self.inc_mean_std = None
            self.unknown = None
            

    def __str__(self):
        return "count: {0}\ninc_mean_std:\n{1}periodic_inc_mean_std:\n{2}unknown:\n{3}".format(self.getTotal(),
                                                                                               str(self.inc_mean_std),
                                                                                               str(self.periodic_inc_mean_std),
                                                                                               str(self.unknown))
