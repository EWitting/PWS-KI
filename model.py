from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras import backend as K
K.image_dim_ordering

from collections import deque
import numpy as np
import heapq
import random

import simulatie

class agent: #agent is een ander woord voor "een AI" in machine learning
    
    def __init__(self, max_uren,prints):
        self.model = self.createModel() #start functie om model te maken en bewaar het in self.model
        self.memory = deque(maxlen=1000) #verzameling van experiences, wordt automatisch op maximum lengte gehouden om te voorkomen dat te oude experiences worden gebruikt
        
        self.epsilon = 1.0  #bepaalt kans om een willekeurige actie te nemen, zo kan de AI beginnen met uitproberen en daarna steeds meer gericht "keuzes maken"
        self.epsilon_min = 0.01 #minimum waarde van epsilon
        self.epsilon_verval = 0.999 #hoe snel epsilon kleiner wordt
        
        self.max_uren = max_uren #bepaald aantal uren dat mag worden uitgekozen om op te leren
        self.prints = prints
        
    def createModel(self):
        if self.prints: print('Model initiatie...')
        
        network = Sequential()  #functie van keras om model te maken
        
        #lagen toevoegen:
        #dense: betekent dat elke neuron verbonden is met een elk neuron in de volgende laag
        #input dim: bepaalt het aantal factoren dat als invoer wordt gebruikt
        #activation: de functie die aan elk neuron wordt toegevoegd, sigmoid is om elk getal tussen 0 en 1 te "proppen". 
        #Dit voorkomt dat factoren met gemiddeld grote getallen meer invloed hebben op de uitkomst
        network.add(Dense(16,input_dim = 3,activation='sigmoid')) 
        
        #linear betekent dat geen speciale functie wordt gebruikt
        network.add(Dense(16,activation = 'linear'))
        
        #dropout voorkomt overfitting door met een bepaalde kans neuronen te laten negeren, dit voorkomt dat alles maar op één manier werkt
        network.add(Dropout(0.05))
        
        #één output in de laatste laag, namelijk het verwachtte cijfer. softplus maakt alle getallen positief(de negatieve getallen zullen wel altijd kleiner blijven) om beter mee te kunnen werken
        network.add(Dense(1,activation = 'softplus'))
        
        #parameters voor keras instellen, dit zijn de gebruikelijkste standaard parameters
        network.compile(loss = 'mse', optimizer = Adam(lr=0.001))
        
        if self.prints: print('Model is gecompiled')
        
        return network
        
    def remember(self,situatie,cijfer): # voeg situatie en cijfer toe aan experiences
        self.memory.append((situatie,cijfer))
        
    def choose(self, voorspellingen, schema):# kiest uren waarop moet worden geleerd aan de hand van de voorspellingen 
        #index in uren wanneer moet worden geleerd
        leermomenten = heapq.nlargest(self.max_uren, range(len(voorspellingen)), key=voorspellingen.__getitem__) #gebruikt plugin om de <max_uren> hoogste voorspellingen te vinden
        
        leeruren = [False]*len(schema) #python array met booleans die false zijn
        
        for i in leermomenten: #maak booleans true op de indexen bepaald door de hoogste voorspellingen
            leeruren[i] = True
    
        return leeruren
        
    def voorspel(self, schema, moeilijkheidsgraad, onthoud):
        sim = simulatie.Simulatie(moeilijkheidsgraad)
        if self.prints: print('Simulatie geladen, beginnen met voorspellen...')
        voorspellingen = []
        situaties = []
        for uur in range(len(schema)):
            if schema[uur]:
                tijd = uur % 24 # tijd van de dag in uren
                tijdTotToets = len(schema) - uur #aantal uren tot de toets is
                invoer = np.array([tijd,tijdTotToets,moeilijkheidsgraad]) #zet invoer om in numpy array, een formaat dat door keras wordt gebruikt
                invoer = invoer.reshape(1,3)
                situaties.append(invoer)             
                voorspellingen.append((self.model.predict(invoer))[0][0])
            else:
                situaties.append(0)
                voorspellingen.append(0)
        
        if self.prints: print('voorspellingen gemaakt:',voorspellingen)

        leeruren = self.choose(voorspellingen,schema)
        
        if self.prints: print('leeruren gekozen:',leeruren)
        
        cijfer = sim.simuleer(leeruren)
        
        if self.prints: print('cijfer berekend:',cijfer)
        
        if onthoud: #als parameter onthoud True is worden de uren waarop is geleerd toegevoegd aan het geheugen/de experiences
            for uur in range(len(leeruren)):
                if leeruren[uur]:                    
                    self.remember(situaties[uur],cijfer)
            if self.prints: print('experiences toegevoegd aan geheugen')
        
        
        return cijfer
    
    def train(self, groepsgrootte):
        if len(self.memory) < groepsgrootte: #check om errors te voorkomen
            print('Niet genoeg experiences in geheugen!')
            return
        
        groep = random.sample(self.memory, groepsgrootte)
        
        invoer = np.empty((groepsgrootte,3)) 
        uitkomsten = np.empty((groepsgrootte,1))
        
        for i in range(len(groep)):
            invoer[i] = groep[i][0]
            uitkomsten[i] = groep[i][1]


        self.model.fit(invoer,uitkomsten,epochs=1,verbose=1)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_verval          