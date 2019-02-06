from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras import backend as K
K.image_dim_ordering

from collections import deque
import numpy as np
import heapq
import random
import math

import simulatie


def getID(binary): #maakt  van een lijst van true en false één getal om beter aan te kunnen herkennen.
        tmp = ''
        
        #maak van true 1 en false 2. Voorbeeld:
        #[True,False,True,True] ====> '1011'
        for i in binary:
            if i: 
                tmp += '1'
            else:
                tmp += '0'
                
        #standaardfunctie die binaire string omzet in decimaal en dan hexadecimaal. voorbeeld:
        #'1011' ===> 11 ===> 0xB
        return hex(int(tmp, 2))
    
class agent: #agent is een ander woord voor "een AI" in machine learning
    
    
        
        
    
    def __init__(self, max_uren,prints):
        self.prints = prints
        self.model = self.createModel() #start functie om model te maken en bewaar het in self.model
        self.memory = deque(maxlen=200000) #verzameling van experiences, wordt automatisch op maximum lengte gehouden om te voorkomen dat te oude experiences worden gebruikt

        self.epsilon = 0.2  #bepaalt kans om een willekeurige actie te nemen, zo kan de AI beginnen met uitproberen en daarna steeds meer gericht "keuzes maken"
        self.epsilon_min = 0.01 #minimum waarde van epsilon
        self.epsilon_verval = 0.9975 #hoe snel epsilon kleiner wordt

        self.max_uren = max_uren #bepaald aantal uren dat mag worden uitgekozen om op te leren

        self.input_size = 7
    def createModel(self):
        if self.prints > 1: 
            print('Model initiatie...')

        network = Sequential()  #functie van keras om model te maken

        #lagen toevoegen:
        #dense: betekent dat elke neuron verbonden is met een elk neuron in de volgende laag
        #input dim: bepaalt het aantal factoren dat als invoer wordt gebruikt
        #activation: de functie die aan elk neuron wordt toegevoegd, sigmoid is om elk getal tussen 0 en 1 te "proppen".
        #Dit voorkomt dat factoren met gemiddeld grote getallen meer invloed hebben op de uitkomst
        network.add(Dense(16,input_dim = 7,activation='sigmoid'))

        #linear betekent dat geen speciale functie wordt gebruikt
        network.add(Dense(16,activation = 'linear'))

        #dropout voorkomt overfitting door met een bepaalde kans neuronen te laten negeren, dit voorkomt dat alles maar op één manier werkt
        network.add(Dropout(0.05))
        
        network.add(Dense(8, activation = 'linear'))        

        #één output in de laatste laag, namelijk het verwachtte cijfer. softplus maakt alle getallen positief(de negatieve getallen zullen wel altijd kleiner blijven) om beter mee te kunnen werken
        network.add(Dense(2,activation = 'softplus'))

        #parameters voor keras instellen, dit zijn de gebruikelijkste standaard parameters
        network.compile(loss = 'mse', optimizer = Adam(lr=0.001))

        if self.prints > 1: 
            print('Model is gecompiled')

        return network

    def remember(self,situatie,cijfer,geleerd): # voeg situatie en cijfer toe aan experiences
        self.memory.append((situatie,cijfer,geleerd))

    def choose(self, voorspellingen, schema):# kiest uren waarop moet worden geleerd aan de hand van de voorspellingen
        '''
        #index in uren wanneer moet worden geleerd
        leermomenten = heapq.nlargest(self.max_uren, range(len(voorspellingen)), key=voorspellingen.__getitem__) #gebruikt plugin om de <max_uren> hoogste voorspellingen te vinden
        '''
        leermomenten = []
        for uur in range(len(voorspellingen)):
            if schema[uur] and voorspellingen[uur]:
                leermomenten.append(uur)
        
        beschikbaar = []
        for uur in range(len(schema)):
            if schema[uur]:
                beschikbaar.append(uur)
              
        while len(leermomenten) < 5:
            done = False
            while not done:
                num = random.choice(beschikbaar)    
                if num not in leermomenten:
                    leermomenten.append(num)
                    done = True
        
        extra_uren = 0
        for i in range(len(beschikbaar)):
            if self.epsilon > random.random():
                num = random.choice(beschikbaar)    
                if num not in leermomenten:
                    leermomenten.append(num)
                    extra_uren += 1
                else:
                    leermomenten.remove(num)
            if extra_uren > 5:
                break
        
        
        leeruren = [False]*len(schema) #python array met booleans die false zijn

        for i in leermomenten: #maak booleans true op de indexen bepaald door de hoogste voorspellingen
            leeruren[i] = True

        return leeruren

    def voorspel(self, schema, moeilijkheidsgraad, onthoud, prints,rand,penalty,**kwargs):
        self.prints = prints
        sim = simulatie.Simulatie(moeilijkheidsgraad)
        if self.prints > 1: 
            print('Simulatie geladen, beginnen met voorspellen...')
        
        tsm = 0 #Tijd Linds Leren. uren sinds vorige keer geleerd
        kg = 0 #Keer Geleerd in totaal
        kg_d = 0 #Keer Geleerd deze Dag
        voorspellingen = []
        situaties = []
        for uur in range(len(schema)):
            if schema[uur]:
                tijd = uur % 24 # tijd van de dag in uren
                tijdTotToets = len(schema) - uur #aantal uren tot de toets is
                #========================================================================
                invoer = np.array([tijd,tijdTotToets,moeilijkheidsgraad,penalty,tsm,kg,kg_d]) #zet invoer om in numpy array, een formaat dat door keras wordt gebruikt
                invoer = invoer.reshape(1,7)
                situaties.append(invoer)
                voorspelling = self.model.predict(invoer)[0]
                
                if self.prints > 1:
                    print(voorspelling,voorspelling[0] > voorspelling[1])
                    
                if voorspelling[0] > voorspelling[1]: #wel leren
                    voorspellingen.append(True)
                    tsm = 0
                    kg += 1
                    kg_d += 1
                    
                else: #niet leren
                    voorspellingen.append(False)
                    tsm += 1
            else:
                situaties.append(0)
                voorspellingen.append(False)
                tsm += 1
                
            if uur % 24 == 0:#zet kg_d op 0 als uren deelbaar is door 24
                kg_d = 0

        if self.prints > 1: 
            print('voorspellingen gemaakt:',voorspellingen)

        leeruren = self.choose(voorspellingen,schema)
    
        if self.prints > 1: 
            print('leeruren gekozen:',leeruren)
            
        cijfer = sim.simuleer(leeruren, rand, penalty)
        if 'metPenalty' in kwargs:
            if kwargs['metPenalty'] == False:
                cijfer = cijfer[0]
        else:
            cijfer = cijfer[1]
            
        if self.prints > 1: 
            print('cijfer berekend:',cijfer)

        if onthoud: #als parameter onthoud True is worden de uren waarop is geleerd toegevoegd aan het geheugen/de experiences
            for uur in range(len(leeruren)):
                if schema[uur]:
                    self.remember(situaties[uur],cijfer,leeruren[uur])
            if self.prints > 1: 
                print('experiences toegevoegd aan geheugen')

        #check om te voorkomen dat wordt geleerd op momenten waar het niet mag:
        for i in range(len(leeruren)):
            if leeruren[i] and not schema[i]:
                print('ho,ho,ho dit mag niet!')
        
        if self.prints > 0:
            print('Epsilon : {0}, Cijfer: {1}'.format(round(self.epsilon,3),cijfer))
        return cijfer, leeruren, getID(leeruren)


    def train(self, groepsgrootte):
        
        if len(self.memory) < groepsgrootte: #check om errors te voorkomen
            print('Niet genoeg experiences in geheugen! het zijn er maar:',len(self.memory))
            return

        groep = random.sample(self.memory, groepsgrootte)

        invoer = np.empty((groepsgrootte,7))
        uitkomsten = np.empty((groepsgrootte,2))

        for i in range(len(groep)):
            invoer[i] = groep[i][0]
            tmp = np.array([groep[i][0]])
            tmp = tmp.reshape(1,7)
            if groep[i][2]: #wel geleerd bij die experience               
                uitkomsten[i][0] = groep[i][1] #maak yes output echte uitkomst
                uitkomsten[i][1] = self.model.predict(tmp)[0][1] #gebruik voorspelling als invoer, model hoeft dus niet te veranderen
            else:   #niet geleerd bij die situatie, hier precies omgekeerd
                uitkomsten[i][1] = groep[i][1] #maak no output de echte uikomst 
                uitkomsten[i][0] = self.model.predict(tmp)[0][0] #gebruik voorspelling als invoer, model hoeft dus niet te veranderen
                
        self.model.fit(invoer,uitkomsten,epochs=1,verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_verval