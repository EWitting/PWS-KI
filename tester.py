import model
import simulatie
import numpy as np
import random
from statistics import mean
from matplotlib import pyplot as plt
import time

testRange = 50000
max_uren = 4

ai = model.agent(max_uren,0)
schema = [True,True,True,True,False,False,False,True,False,False,True,False,False,False,False,False,False,False,True,True,True,True,False,False,False,True,False,False,True,False,False]



hist = []
diffs = []

def randomAgent(schema, factor):
    sim = simulatie.Simulatie(factor)
    beschikbaar = []
    for uur in range(len(schema)):
        if schema[uur]:
            beschikbaar.append(uur)
        
    leermomenten = []
    
    
    
    for i in range(max_uren):
            done = False
            while not done:
                num = random.choice(beschikbaar)    
                if num not in leermomenten:
                    leermomenten.append(num)
                    done = True
    
    return sim.simuleer(leermomenten)



t0 = time.time()

def eta(i):
    bezig = time.time() - t0
    snelheid = i / bezig
    return round((testRange - i)/snelheid)
    

for i in range(testRange):
    factor = random.uniform(0.5,0.9)
    resultaat = ai.voorspel(schema,factor,True,0)
    diff = resultaat - randomAgent(schema,factor)
    hist.append(resultaat)
    diffs.append(diff)
    if i% 10 == 0 and i is not 0:
        ai.train(min(max_uren*i,200))
    if i % round(testRange/20) == 0 and i is not 0:
        string = 'ETA: {6} seconden ,Simulatie: {0}, Aantal keer model getraind: {1}, Grootte geheugen: {2}, Cijfer: {3}, Verschil met controle: {4}, Epsilon: {5}'
        print(string.format(i, round(i/10) ,len(ai.memory) ,resultaat ,round(diff,1) ,round(ai.epsilon,2),eta(i)))

print(round(time.time()-t0,1),'seconden')


N = round(testRange/20)

cumsum, moving_aves = [0], []

for i, x in enumerate(hist, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)

plt.plot(moving_aves)
plt.show()

tmp = moving_aves
cumsum, moving_aves = [0], []

for i, x in enumerate(tmp, 1):
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

tmp = moving_aves
cumsum, moving_aves = [0], []

for i, x in enumerate(tmp, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)



plt.plot(moving_aves)
plt.show()
print('Gemiddeld verschil met willekeurig kiezen:',mean(diffs))

