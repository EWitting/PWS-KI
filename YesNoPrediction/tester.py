import time
startt = time.time()

import math
import model
import simulatie
import random
from statistics import mean
from matplotlib import pyplot as plt

from visualisatie import visualiseer



testRange = 15000
printOp = 500
max_uren = 5
maxTime = 120 #in seconden
reached = 0

#tussen bs_epochs_start en bs_epochs_max wordt de batch_size voor het trainen verhoogd.  https://arxiv.org/abs/1711.00489
batch_size_start = 32
batch_size_max = 512
bs_epochs_start = 500
bs_epochs_max = 4000
batch_size = batch_size_start


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
        penalty = random.uniform(0.1,1.5)
        resultaat, leeruren, ID = ai.voorspel(schema,factor,True,0,0.1,penalty)
        diff = resultaat - randomAgent(schema,factor, penalty)
        hist.append(resultaat)
        diffs.append(diff)
        validation = (ai.voorspel(schema,0.8,False,0,0,0.4)[0])
        test.append(validation)
        if i% math.floor(batch_size/2) == 0 and i > batch_size:
            
            if i < bs_epochs_start:
                batch_size = batch_size_start
            elif i < bs_epochs_max:
                batch_size = math.floor(batch_size_start + (i - bs_epochs_start) / (bs_epochs_max - bs_epochs_start) * (batch_size_max - batch_size_start))
            else:
                batch_size = batch_size_max
            ai.train(batch_size)
            
        if i % round(printOp) == 0 and i is not 0:
            string = 'Bezig: {6} sec, ETA: {5} sec, Simulatie: {0}, Validation: {1}, Cijfer: {2}, Batch Size {3}, Epsilon: {4}, ID: {7}, penalty: {8}'
            print(string.format(i,validation ,resultaat ,batch_size ,round(ai.epsilon,2),eta(i),round(time.time() - t0), ID.replace('0',''),penalty))
            visualiseer(schema,ai.voorspel(schema,0.75,False,0,0,0.7)[1],True)
            if time.time() - t0 > maxTime:
                done = True
                if reached is 0:
                    reached = i

if reached is 0:
    reached = testRange

print(round(time.time()-t0,1),'seconden')




cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,1.5)
visualiseer(schema,uren,True)
sim = simulatie.Simulatie(0.8)
print('met penalty 0.7',sim.plot(uren, 1.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,1)
visualiseer(schema,uren,True)
sim = simulatie.Simulatie(0.8)
print('penalty 0.5',sim.plot(uren, 1))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,0.5)
visualiseer(schema,uren,True)
sim = simulatie.Simulatie(0.8)
print('penalty 0.3',sim.plot(uren, 0.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,0.1)
visualiseer(schema,uren,True)
sim = simulatie.Simulatie(0.8)
print('penalty 0.1',sim.plot(uren, 0.1))


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
