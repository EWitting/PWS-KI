import model
import simulatie
import random
from statistics import mean
from matplotlib import pyplot as plt
import time
from visualisatie import visualiseer
import os
from six.moves import cPickle


testRange = 35000
printOp = 500
max_uren = 3
maxTime = 600 #in seconden
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
bs = 64

#vind nummer voor nieuwe folder die nog niet is gebruikt
logNum = 0    
while(os.path.exists("./log"+str(logNum))):
    logNum += 1
dirName = './log' + str(logNum) +'/'
os.makedirs(dirName + 'screenshots')
print('outputting to',dirName)

#gebruikt als input namen en lists, slaat ze ge-pickled op als ruwe data, en als pyplot grafiek
def saveStats(dictionary):     
    for name, values in dictionary.items():
        with open(dirName + name + '.pkl','wb') as f:
            cPickle.dump(values,f)
        plt.plot(values)
        #sla grafiek als simpele .png op, maar ook als .svg met oneindige resolutie
        plt.savefig(dirName+name+'.svg')
        plt.savefig(dirName+name+'.png')
        plt.clf()
        
    #sla model op
    ai.model.save(dirName[2:] + '/model.h5') 
    
    with open(dirName + 'model_summary.txt', 'w') as f:
        ai.model.summary(print_fn=lambda x: f.write(x + '\n'))    
        
    #sla parameters op
    config_dict = { 
            'versie' : os.getcwd(),
            'epsilon verval' : ai.epsilon_verval,
            'epsilon minimum': ai.epsilon_min,
            'geheugen grootte' :ai.memory_len,
            'batch size' :bs,
            'max. epochs': testRange,
            'max. seconden': maxTime,
            'werkelijk aantal epochs' : reached,
            'werkelijk aantal seconden':round(time.time() - t0,1),
            'epochs per seconde' : round(reached/(time.time() - t0),2),
            'gemiddelde van laatste procent cijfer' : round(mean(hist[-round(len(hist)/100):]),3),
            'gemiddelde van laatste procent controle' : round(mean(test[-round(len(test)/100):]),3),
            'gemiddelde van laatste procent verschil met random' : round(mean(diffs[-round(len(diffs)/100):]),3),
            'uren per week': max_uren
            }
    
    with open(dirName + 'info.txt', 'w') as f:
        for name,value in config_dict.items():
            f.write("{}: {}\n".format(name,value))
            
def smooth(myList,N):
    cumsum, moving_aves = [0], []

    for i, x in enumerate(myList, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N:
            moving_ave = (cumsum[i] - cumsum[i-N])/N
            moving_aves.append(moving_ave)            
    return moving_aves

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
        if i% round(bs/4) == 0 and i > bs:
            ai.train(max(max_uren*i,bs))
            
        if i % round(printOp) == 0 and i is not 0:
            string = 'Bezig: {6} sec, ETA: {5} sec, Simulatie: {0}, Validation: {1}, Cijfer: {2}, Verschil met controle: {3}, Epsilon: {4}, ID: {7}'
            print(string.format(i,validation ,resultaat ,round(diff,1) ,round(ai.epsilon,2),eta(i),round(time.time() - t0), ID))
            visualiseer(schema,leeruren,True, dirName[2:]+'screenshots/'+str(i))
            if time.time() - t0 > maxTime:
                done = True
                if reached is 0:
                    reached = i


if reached is 0:
    reached = testRange

print(round(time.time()-t0,1),'seconden')


os.makedirs(dirName+'penalty_test')

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '1.5')
sim = simulatie.Simulatie(0.8)
print('met penalty 1.5',sim.plot(uren, 1.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '1')
sim = simulatie.Simulatie(0.8)
print('penalty 1',sim.plot(uren, 1))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '0.5')
sim = simulatie.Simulatie(0.8)
print('penalty 0.5',sim.plot(uren, 0.5))

cijfer, uren, ID = ai.voorspel(schema, 0.75,False,0,0.1)
visualiseer(schema,uren,True,dirName[2:] + 'penalty_test/penalty' + '0.1')
sim = simulatie.Simulatie(0.8)
print('penalty 0.1',sim.plot(uren, 0.1))


N = round(reached/200)

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
          
          'cijfer' : hist,
          'cijfer_smooth' : smoothHist,
          
          'verschil_met_random' : diffs,
          'verschil_met_random_smooth': diffsSmooth,
          
          'validation' : test,
          'validation_smooth':  testSmooth,    
          })
    
    
