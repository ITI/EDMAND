import numpy as np 
import math

#LAMBDA = 0.002
LAMBDA = 0.005
MU = 20.0
BETA = 0.2
T_p = seconds=math.ceil(math.log(BETA*MU/(BETA*MU-1), 2)/LAMBDA)

def fading(t):
    return 2**(-LAMBDA * t)
    

class DenStream1D():
    def __init__(self, epsilon):
        self.P_list = [] 
        self.O_list = [] 
        self.last_update = None
        self.epsilon = epsilon
        #print("T_p: " + str(T_p))


    class OMicroCluster():
        def __init__(self, epsilon, p, ts):
            self.epsilon = epsilon
            self.CF1 = p 
            self.CF2 = p**2 
            self.w = 1 
            self.t0 = ts
            self.last_update = ts


        def __str__(self):
            return "o_c: {0}, o_w: {1}, o_r: {2}".format(self.getCenter(), self.w, self.getRadius())
           

        def getCenter(self):
            return self.CF1 / self.w


        def getRadius(self):
            return math.sqrt(abs(self.CF2/self.w-(self.CF1/self.w)**2))


        def merge(self, p, ts):
            if ts > self.last_update:
                fade = fading(ts-self.last_update)
                self.CF1 = fade * self.CF1
                self.CF2 = fade * self.CF2
                self.w = fade * self.w
                self.last_update = ts

            new_CF1 = self.CF1 + p
            new_CF2 = self.CF2 + p**2
            new_w = self.w + 1
            r = math.sqrt(abs(new_CF2/new_w-(new_CF1/new_w)**2))
            
            if r <= self.epsilon:
                self.CF1 = new_CF1
                self.CF2 = new_CF2
                self.w = new_w
                return True
            else:
                return False


        def update(self, ts):
            xi = (2**(-LAMBDA*(ts-self.t0+T_p))-1)/(2**(-LAMBDA*T_p)-1)
            #print("Xi: " + str(xi))
            if ts > self.last_update:
                fade = fading(ts-self.last_update)
                self.CF1 = fade * self.CF1
                self.CF2 = fade * self.CF2
                self.w = fade * self.w
                self.last_update = ts

            if self.w < xi:
                return False 
            else:
                return True 
                

    class PMicroCluster():
        def __init__(self, o_micro_cluster):
            self.epsilon = o_micro_cluster.epsilon
            self.CF1 = o_micro_cluster.CF1
            self.CF2 = o_micro_cluster.CF2
            self.w = o_micro_cluster.w
            self.last_update = o_micro_cluster.last_update


        def __str__(self):
            return "p_c: {0}, p_w: {1}, p_r: {2}".format(self.getCenter(), self.w, self.getRadius())

 
        def getCenter(self):
            return self.CF1 / self.w


        def getRadius(self):
            return math.sqrt(abs(self.CF2/self.w-(self.CF1/self.w)**2))


        def merge(self, p, ts):
            if ts > self.last_update:
                fade = fading(ts-self.last_update)
                self.CF1 = fade * self.CF1
                self.CF2 = fade * self.CF2
                self.w = fade * self.w
                self.last_update = ts

            new_CF1 = self.CF1 + p
            new_CF2 = self.CF2 + p**2
            new_w = self.w + 1
            r = math.sqrt(abs(new_CF2/new_w-(new_CF1/new_w)**2))

            if r <= self.epsilon:
                self.CF1 = new_CF1
                self.CF2 = new_CF2
                self.w = new_w
                return True
            else:
                return False


        def update(self, ts):
            if ts > self.last_update:
                fade = fading(ts-self.last_update)
                self.CF1 = fade * self.CF1
                self.CF2 = fade * self.CF2
                self.w = fade * self.w
                self.last_update = ts

            if self.w < BETA * MU:
                return False 
            else:
                return True 


    def distance(self, p, c):
        return abs(p - c)


    def merge(self, p, ts):
        p = float(p)
        #print(p)
        rst = True 
        nearest_p = None
        dis_p = None
        ano_score = 0 
        p_c_list = []
        p_r_list = []
        for p_micro_cluster in self.P_list:
            c = p_micro_cluster.getCenter()
            r = p_micro_cluster.getRadius() 
            p_c_list.append(c)
            p_r_list.append(r)
            dis_cur = self.distance(p, c)
            if nearest_p == None or dis_cur < dis_p:
                nearest_p = p_micro_cluster
                dis_p = dis_cur

        if nearest_p == None or not nearest_p.merge(p, ts):
            nearest_o = None
            dis_o = None
            for o_micro_cluster in self.O_list:
                dis_cur = self.distance(p, o_micro_cluster.getCenter())
                if nearest_o == None or dis_cur < dis_o:
                    nearest_o = o_micro_cluster
                    dis_o = dis_cur

            if nearest_o != None and nearest_o.merge(p, ts):
                if nearest_o.w > BETA * MU:
                    self.O_list.remove(nearest_o)
                    self.P_list.append(DenStream1D.PMicroCluster(nearest_o))
                else:
                    rst = False 
                    ano_score = 1 - (nearest_o.w-1)/(BETA*MU-1)
            else:
                self.O_list.append(DenStream1D.OMicroCluster(self.epsilon, p, ts))
                rst = False 
                ano_score = 1

        if self.last_update == None:
            self.last_update = ts
        elif ts > self.last_update + T_p:
            self.update(ts)
            self.last_update = ts

        return (rst, ano_score, p_c_list, p_r_list)


    def update(self, ts):
        for p_micro_cluster in self.P_list:
            if not p_micro_cluster.update(ts):
                self.P_list.remove(p_micro_cluster)
                
        for o_micro_cluster in self.O_list:
            if not o_micro_cluster.update(ts):
                self.O_list.remove(o_micro_cluster)

    
    def __str__(self):
        if self.P_list:
            rst = "\nP_list:\n"
            for i in range(len(self.P_list)):
                rst += "index: " + str(i) + ", " + str(self.P_list[i]) + "\n" 
        else:
            rst = "\nP_list: Empty\n"
        if self.O_list:
            rst += "O_list:\n"
            for i in range(len(self.O_list)):
                rst += "index: " + str(i) + ", " + str(self.O_list[i]) + "\n"
        else:
            rst += "O_list: Empty\n"
        return rst
