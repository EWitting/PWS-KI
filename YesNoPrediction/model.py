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

        self.epsilon = 1.0  #bepaalt kans om een willekeurige actie te nemen, zo kan de AI beginnen met uitproberen en daarna steeds meer gericht "keuzes maken"
        self.epsilon_min = 0.01 #minimum waarde van epsilon
        self.epsilon_verval = 0.9975 #hoe snel epsilon kleiner wordt

        self.max_uren = max_uren #bepaald aantal uren dat mag worden uitgekozen om op te leren

    def createModel(self):
        if self.prints > 1: 
            print('Model initiatie...')

        network = Sequential()  #functie van keras om model te maken

        #lagen toevoegen:
        #dense: betekent dat elke neuron verbonden is met een elk neuron in de volgende laag
        #input dim: bepaalt het aantal factoren dat als invoer wordt gebruikt
        #activation: de functie die aan elk neuron wordt toegevoegd, sigmoid is om elk getal tussen 0 en 1 te "proppen".
        #Dit voorkomt dat factoren met gemiddeld grote getallen meer invloed hebben op de uitkomst
        network.add(Dense(16,input_dim = 5,activation='sigmoid'))

        #linear betekent dat geen speciale functie wordt gebruikt
        network.add(Dense(16,activation = 'linear'))

        #dropout voorkomt overfitting door met een bepaalde kans neuronen te laten negeren, dit voorkomt dat alles maar op één manier werkt
        network.add(Dropout(0.05))
        
        network.add(Dense(8, activation = 'linear'))        

        #één output in de laatste laag, namelijk het verwachtte cijfer. softplus maakt alle getallen positief(de negatieve getallen zullen wel altijd kleiner blijven) om beter mee te kunnen werken
        network.add(Dense(1,activation = 'softplus'))

        #parameters voor keras instellen, dit zijn de gebruikelijkste standaard parameters
        network.compile(loss = 'mse', optimizer = Adam(lr=0.001))

        if self.prints > 1: 
            print('Model is gecompiled')

        return network

    def remember(self,situatie,cijfer): # voeg situatie en cijfer toe aan experiences
        self.memory.append((situatie,cijfer))

    def choose(self, voorspellingen, schema):# kiest uren waarop moet worden geleerd aan de hand van de voorspellingen
        #index in uren wanneer moet worden geleerd
        leermomenten = heapq.nlargest(self.max_uren, range(len(voorspellingen)), key=voorspellingen.__getitem__) #gebruikt plugin om de <max_uren> hoogste voorspellingen te vinden
        
        beschikbaar = []
        for uur in range(len(schema)):
            if schema[uur]:
                beschikbaar.append(uur)
        
        
        for i in range(len(leermomenten)):
            if self.epsilon > random.random():
                done = False
                while not done:
                    num = random.choice(beschikbaar)    
                    if num not in leermomenten:
                        leermomenten[i] = num
                        done = True
        
        
        leeruren = [False]*len(schema) #python array met booleans die false zijn

        for i in leermomenten: #maak booleans true op de indexen bepaald door de hoogste voorspellingen
            leeruren[i] = True

        return leeruren

    def voorspel(self, schema, moeilijkheidsgraad, onthoud, prints,rand):
        self.prints = prints
        sim = simulatie.Simulatie(moeilijkheidsgraad)
        if self.prints > 1: 
            print('Simulatie geladen, beginnen met voorspellen...')
            
        voorspellingen = []
        situaties = []
        for uur in range(len(schema)):
            if schema[uur]:
                dagTotToets = math.ceil(uur/24) - math.ceil(len(schema)/24)
                tijd = uur % 24 # tijd van de dag in uren
                tijdTotNacht = 24 - uur #========================================================================
                tijdTotToets = len(schema) - uur #aantal uren tot de toets is
                invoer = np.array([dagTotToets,tijd,tijdTotNacht,tijdTotToets,moeilijkheidsgraad]) #zet invoer om in numpy array, een formaat dat door keras wordt gebruikt
                invoer = invoer.reshape(1,5)
                situaties.append(invoer)
                voorspellingen.append((self.model.predict(invoer))[0][0])
            else:
                situaties.append(0)
                voorspellingen.append(0)

        if self.prints > 1: 
            print('voorspellingen gemaakt:',voorspellingen)

        leeruren = self.choose(voorspellingen,schema)

        if self.prints > 1: 
            print('leeruren gekozen:',leeruren)
        cijfer = sim.simuleer(leeruren, rand)

        if self.prints > 1: 
            print('cijfer berekend:',cijfer)

        if onthoud: #als parameter onthoud True is worden de uren waarop is geleerd toegevoegd aan het geheugen/de experiences
            for uur in range(len(leeruren)):
                if leeruren[uur]:
                    self.remember(situaties[uur],cijfer)
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

        invoer = np.empty((groepsgrootte,5))
        uitkomsten = np.empty((groepsgrootte,1))

        for i in range(len(groep)):
            invoer[i] = groep[i][0]
            uitkomsten[i] = groep[i][1]


        self.model.fit(invoer,uitkomsten,epochs=1,verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_verval