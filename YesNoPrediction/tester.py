import time
startt = time.time()

import model
import simulatie
import random
from statistics import mean
from matplotlib import pyplot as plt

from visualisatie import visualiseer



testRange = 5000
printOp = 250
max_uren = 5
maxTime = 120 #in seconden
reached = 0

ai = model.agent(max_uren,0)

        #zondag
schema =[False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,False,False,False,False,
        #maadag
        False,False,False,False,False,False,False ,False,False,False,False,False,False,False,False,True,True ,False ,False ,False,False,False,False,False,
        #dinsdag
        False,False,False,False,False,False,False ,False,False,False,False,False,False,False,True,True,True ,True ,False ,False,False,False,False,False,
        #woensdag
        False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,True,True,False,False,False,False,
        #donderdag
        False,False,False,False,False,False,False ,False,False,False,False,False,False,False,False,True,True ,False ,False ,False,False,False,False,False,
        #vrijdag
        False,False,False,False,False,False,False,False,False,False,False,False,False]


hist = []
diffs = []
test = []

def randomAgent(schema, factor, penalty):
    sim = simulatie.Simulatie(factor)
    
    return sim.simuleer(randomUren(schema),0.1,penalty)[1]

def randomUren(schema):
    beschikbaar = []
    for uur in range(len(schema)):
        if schema[uur]:
            beschikbaar.append(uur)
        
    leermomenten = []
            
    for i in range(max_uren):
            num = random.choice(beschikbaar)    
            if num not in leermomenten:
                leermomenten.append(num)
            else:
                leermomenten.remove(num)
                
    leeruren = [False]*len(schema)    
    for i in leermomenten:
        leeruren[i] = True
    return leeruren


t0 = time.time()
print('train loop begint nu, op:',round(time.time()-startt,2),'seconden')
def eta(i):
    bezig = time.time() - t0
    snelheid = i / bezig
    return round(min((testRange - i)/snelheid, maxTime - bezig))
    
done = False
for i in range(testRange):
    if not done:
        factor = random.uniform(0.5,0.9)
        penalty = random.uniform(0.1,0.7)
        resultaat, leeruren, ID = ai.voorspel(schema,factor,True,0,0.1,penalty)
        diff = resultaat - randomAgent(schema,factor, penalty)
        hist.append(resultaat)
        diffs.append(diff)
        validation = (ai.voorspel(schema,0.8,False,0,0,0.4)[0])
        test.append(validation)
        if i% 25 == 0 and i is not 0:
            ai.train(min(max_uren*i,16))
        if i % round(printOp) == 0 and i is not 0:
            string = 'Bezig: {6} sec, ETA: {5} sec, Simulatie: {0}, Validation: {1}, Cijfer: {2}, Verschil met controle: {3}, Epsilon: {4}, ID: {7}'
            print(string.format(i,validation ,resultaat ,round(diff,1) ,round(ai.epsilon,2),eta(i),round(time.time() - t0), ID))
            visualiseer(schema,leeruren,True)
            if time.time() - t0 > maxTime:
                done = True
                if reached is 0:
                    reached = i

if reached is 0:
    reached = testRange

print(round(time.time()-t0,1),'seconden')




cijfer, uren, ID = ai.voorspel(schema, 0.75,False,2,0.1,0.4)
visualiseer(schema,uren,True)
sim = simulatie.Simulatie(0.8)
print(sim.plot(uren, 0.1))




N = round(reached/20)
cumsum, moving_aves = [0], []

for i, x in enumerate(hist, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)

plt.plot(moving_aves)
plt.show()

print('Gemiddelde cijfer:',mean(hist))


cumsum, moving_aves = [0], []

for i, x in enumerate(diffs, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)
        

plt.plot(moving_aves)
plt.show()


print('Gemiddeld verschil met willekeurig kiezen:',mean(diffs))



cumsum, moving_aves = [0], []

for i, x in enumerate(test, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)

plt.plot(moving_aves)
plt.show()

print('Controle')
