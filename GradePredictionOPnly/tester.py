import model
import simulatie
import random
from statistics import mean
from matplotlib import pyplot as plt
import time
from visualisatie import visualiseer


testRange = 20000
printOp = 500
max_uren = 5
maxTime = 300 #in seconden
reached = 0

ai = model.agent(max_uren,0)

        #zondag
schema =[False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,False,False,False,False,
        #maadag
        False,False,False,False,False,False,True ,False,False,False,False,False,False,False,False,True,True ,False ,False ,False,False,False,False,False,
        #dinsdag
        False,False,False,False,False,False,True ,False,False,False,False,False,False,False,True,True,True ,True ,False ,False,False,False,False,False,
        #woensdag
        False,False,False,False,False,False,True,False,False,False,False,False,False,False,False,False,True,True,True,True,False,False,False,False,
        #donderdag
        False,False,False,False,False,False,True,False,False,False,False,False,False]


hist = []
diffs = []
test = []
def randomAgent(schema, factor):
    sim = simulatie.Simulatie(factor)
    
    return sim.simuleer(randomUren(schema),0.1)

def randomUren(schema):
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
    leeruren = [False]*len(schema)    
    for i in leermomenten:
        leeruren[i] = True
    return leeruren


t0 = time.time()

def eta(i):
    bezig = time.time() - t0
    snelheid = i / bezig
    return round(min((testRange - i)/snelheid, maxTime - bezig))
    
done = False
for i in range(testRange):
    if not done:
        factor = random.uniform(0.5,0.9)
        resultaat, leeruren, ID = ai.voorspel(schema,factor,True,0,0.1)
        diff = resultaat - randomAgent(schema,factor)
        hist.append(resultaat)
        diffs.append(diff)
        validation = (ai.voorspel(schema,0.8,False,0,0)[0])
        test.append(validation)
        if i% 10 == 0 and i is not 0:
            ai.train(min(max_uren*i,32))
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

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1)
visualiseer(schema,uren,True)

N = round(reached/20)

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



cumsum, moving_aves = [0], []

for i, x in enumerate(test, 1):
    cumsum.append(cumsum[i-1] + x)
    if i>=N:
        moving_ave = (cumsum[i] - cumsum[i-N])/N
        moving_aves.append(moving_ave)

plt.plot(moving_aves)
plt.show()

