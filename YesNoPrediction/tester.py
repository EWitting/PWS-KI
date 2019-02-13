import time
startt = time.time()

import math
import random
from statistics import mean
from matplotlib import pyplot as plt

#mijn andere scripts
from visualisatie import visualiseer
import model
import simulatie

#voor laad- en opsla
from six.moves import cPickle
import os


testRange = 50%000
printOp = 250
max_uren = 5
maxTime = 60*10 #in seconden
reached = 0

#tussen bs_epochs_start en bs_epochs_max wordt de batch_size voor het trainen verhoogd.  https://arxiv.org/abs/1711.00489
batch_size_start = 32
batch_size_max = 256
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

#vind nummer voor nieuwe folder die nog niet is gebruikt
logNum = 0    
while(os.path.exists("./log"+str(logNum))):
    logNum += 1
dirName = './log' + str(logNum) +'/'
os.makedirs(dirName + 'screenshots')

#gebruikt als input namen en lists, slaat ze ge-pickled op als ruwe data, en als pyplot grafiek
def saveStats(dictionary):     
    for name, values in dictionary.items():
        with open(dirName + name + '.pkl','wb') as f:
            cPickle.dump(values,f)
        plt.plot(values)
        plt.savefig(dirName+name+'.png')
        plt.clf()
    ai.model.save(dirName[2:] + '/model.h5')
            
def smooth(myList,N):
    cumsum, moving_aves = [0], []

    for i, x in enumerate(myList, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N:
            moving_ave = (cumsum[i] - cumsum[i-N])/N
            moving_aves.append(moving_ave)            
    return moving_aves


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

last_loss = []
outputs = [] #houdt alle rijen aan test gegevens bij
done = False
for i in range(testRange):
    if not done:
        factor = random.uniform(0.5,0.9)
        penalty = random.uniform(0.1,1.5)
        resultaat, leeruren, ID = ai.voorspel(schema,factor,True,0,0.1,penalty)
        diff = resultaat - randomAgent(schema,factor, penalty)
        hist.append(resultaat)
        diffs.append(diff)
        validation = (ai.voorspel(schema,0.8,False,0,0,0.7)[0])
        test.append(validation)
        if i% math.floor(batch_size/4) == 0 and i > batch_size:
            
            if i < bs_epochs_start:
                batch_size = batch_size_start
            elif i < bs_epochs_max:
                batch_size = math.floor(batch_size_start + (i - bs_epochs_start) / (bs_epochs_max - bs_epochs_start) * (batch_size_max - batch_size_start))
            else:
                batch_size = batch_size_max
            batch_size = 64
            last_loss.append(ai.train(batch_size))
            
        if i % round(printOp) == 0 and i is not 0:
            string = 'Bezig: {6} sec, ETA: {5} sec, Simulatie: {0}, Validation: {1}, Cijfer: {2}, Batch Size {3}, Epsilon: {4}, ID: {7}, penalty: {8}, loss: {9}, aantal experiences: {10}'
            output = string.format(i,validation ,resultaat ,batch_size ,round(ai.epsilon,2),eta(i),round(time.time() - t0), ID.replace('0',''),round(penalty,1),round(last_loss[len(last_loss)-1],2), len(ai.memory))
            outputs.append(output)
            print(output)
            visualiseer(schema,ai.voorspel(schema,0.75,False,0,0,0.7)[1],True,dirName[2:]+'screenshots/'+i)
            if time.time() - t0 > maxTime:
                done = True
                if reached is 0:
                    reached = i



if reached is 0:
    reached = testRange

print(round(time.time()-t0,1),'seconden')

plt.plot(last_loss)
plt.show()

last_loss_smooth = smooth(last_loss,20)
plt.plot(last_loss_smooth)
plt.show()

os.makedirs(dirName+'penalty_test')

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,1.5)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '1.5')
sim = simulatie.Simulatie(0.8)
print('met penalty 1.5',sim.plot(uren, 1.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '1')
sim = simulatie.Simulatie(0.8)
print('penalty 1',sim.plot(uren, 1))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,0.5)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '0.5')
sim = simulatie.Simulatie(0.8)
print('penalty 0.5',sim.plot(uren, 0.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1,0.1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '0.1')
sim = simulatie.Simulatie(0.8)
print('penalty 0.1',sim.plot(uren, 0.1))


N = round(reached/20)

smoothHist = smooth(hist,N)
plt.plot(smoothHist)
plt.show()
print('Gemiddelde cijfer:',mean(hist[-1000:]))

diffsSmooth = smooth(diffs,N)
plt.plot(diffsSmooth)
plt.show()
print('Gemiddeld verschil met willekeurig kiezen:',mean(diffs[-1000:]))

testSmooth = smooth(test,N)
plt.plot(testSmooth)
plt.show()
print('Controle met penalty = 0.7')


#saving of everything
saveStats({
          'loss': last_loss,
          'loss_smooth': last_loss_smooth,
          
          'cijfer' : hist,
          'cijfer_smooth' : smoothHist,
          
          'verschil_met_random' : diffs,
          'verschil_met_random_smooth': diffsSmooth,
          
          'validation' : test,
          'validation_smooth':  testSmooth          
          })
    
    
with open(dirName + 'model_summary.txt', 'w') as f:
    ai.model.summary(print_fn=lambda x: f.write(x + '\n'))
    
with open(dirName + 'output_log.txt', 'w') as f:
    for line in outputs:
        f.write("%s\n" % line)