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


testRange = 75000
printerval = 250
max_uren = 5
maxTime = 60*0.1 #in seconden
reached = 0
vast_uren = 5 #ter vergelijking met grade prediction only
validation_penalty = 0.7 #penalty die wordt gebruikt om de voortgang te testen

#tussen bs_epochs_start en bs_epochs_max wordt de batch_size voor het trainen verhoogd.  https://arxiv.org/abs/1711.00489
batch_size_start = 32
batch_size_max = 256
bs_epochs_start = 500
bs_epochs_max = 4000
batch_size = batch_size_start
bs = 64

ai = model.agent(0)

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


#vind nummer voor nieuwe folder die nog niet is gebruikt
logNum = 0    
while(os.path.exists("./log"+str(logNum))):
    logNum += 1
dirName = './log' + str(logNum) +'/'
os.makedirs(dirName + 'screenshots')
print('outputting to',dirName)

# %% ALLE FUNCTIES
#gebruikt als input namen en lists, slaat ze ge-pickled op als ruwe data, en als pyplot grafiek
def saveStats(dictionary, plotten):
    os.makedirs(dirName+'vector')
    os.makedirs(dirName+'picture')
    for name, values in dictionary.items():
        with open(dirName + name + '.pkl','wb') as f:
            cPickle.dump(values,f)
        plt.plot(values)
        #sla grafiek als simpele .png op, maar ook als .svg met oneindige resolutie
        plt.savefig(dirName+'vector/'+name+'.svg')
        plt.savefig(dirName+'picture/'+name+'.png')
        if plotten:
            plt.show()
            print(name)
        else:
            plt.clf()
        
    #sla model op
    ai.model.save(dirName[2:] + '/model.h5') 
    
    with open(dirName + 'model_summary.txt', 'w') as f:
        ai.model.summary(print_fn=lambda x: f.write(x + '\n'))    
        
    with open(dirName + 'output_log.txt', 'w') as f:
        for line in outputs:
            f.write("%s\n" % line)
    
    #sla parameters op
    config_dict = { 
            'epsilon verval' : ai.epsilon_verval,
            'epsilon minimum': ai.epsilon_min,
            'geheugen grootte' :ai.memory_len,
            'batch size' :bs,
            'max. epochs': testRange,
            'max. seconden': maxTime,
            'werkelijk aantal epochs' : reached,
            'werkelijk aantal seconden':round(time.time() - t0,1),
            'epochs per seconde:' : round(reached/(time.time() - t0),2),
            'gemiddelde van laatste procent loss' : round(mean(loss_hist[-round(len(loss_hist/100)):]),3),
            'gemiddelde van laatste procent beloning' : round(mean(beloning_hist[-round(len(beloning_hist/100)):]),3),
            'gemiddelde van laatste procent controle' : round(mean(val_hist[-round(len(val_hist/100)):]),3),
            'print/screenshot interval' : printerval,
            'penalty voor validation' : validation_penalty
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

# %% TRAINING LOOP

'''
beloning = cijfer - (aantal keer geleerd )*penalty
'''

outputs = [] #slaat alle geprintte gegevens op

#alle gemeten statistieken worden in deze lists opgeslagen
loss_hist = [] #loss per keer getraind
epsilon_hist = [] #ter vergelijking om naast de andere resultaten te houden
beloning_hist = [] #slaat beloning op
diff_hist = [] #verschil tussen behaalde beloning en beloning van een 100% willekeurige agent
val_hist = [] #beloningen met steeds dezelfde penalty en moeilijkheidsgraad, zonder willekeur
cijfer_hist = [] #cijfer zonder penalty aftrek
fixed_hist = [] #de cijfers geïsoleerd uit cijfer_hist, waar een specifiek aantal uren is geleerd, ter vergelijking met de 'grade predict only' aanpak 
frequentie_hist = [] #houdt bij hoe vaak wordt geleerd

done = False
for i in range(testRange):
    if not done:
        factor = random.uniform(0.5,0.9)
        penalty = random.uniform(0.1,1.5)
        beloning, leeruren, ID = ai.voorspel(schema,factor,True,0,0.1,penalty)
        
        #statistieken
        diff = beloning - randomAgent(schema,factor, penalty)
        beloning_hist.append(beloning)
        diff_hist.append(diff)
        validation = (ai.voorspel(schema,0.8,False,0,0,0.7)[0])
        val_hist.append(validation)
        
        epsilon_hist.append(ai.epsilon)
        
        frequentie = sum(leeruren)        
        frequentie_hist.append(frequentie)
        
        cijfer = beloning + frequentie*penalty
        cijfer_hist.append(cijfer)
        
        
        if sum(leeruren) == vast_uren:
            fixed_hist.append(cijfer)
        
        
        if i% math.floor(batch_size/4) == 0 and i > batch_size:
            
            if i < bs_epochs_start:
                batch_size = batch_size_start
            elif i < bs_epochs_max:
                batch_size = math.floor(batch_size_start + (i - bs_epochs_start) / (bs_epochs_max - bs_epochs_start) * (batch_size_max - batch_size_start))
            else:
                batch_size = batch_size_max
            batch_size = bs
            loss_hist.append(ai.train(batch_size))
            
        if i % round(printerval) == 0 and i is not 0:
            string = 'Bezig: {6} sec, ETA: {5} sec, Simulatie: {0}, Validation: {1}, Cijfer: {2}, Batch Size {3}, Epsilon: {4}, ID: {7}, penalty: {8}, loss: {9}, aantal experiences: {10}'
            output = string.format(i,validation ,beloning ,batch_size ,round(ai.epsilon,2),eta(i),round(time.time() - t0), ID.replace('0',''),round(penalty,1),round(loss_hist[len(loss_hist)-1],2), len(ai.memory))
            outputs.append(output)
            print(output)
            visualiseer(schema,ai.voorspel(schema,0.75,False,0,0,validation_penalty)[1],True,dirName[2:]+'screenshots/'+str(i))
            if time.time() - t0 > maxTime:
                done = True
                if reached is 0:
                    reached = i

#%% STATISTIEKEN
if reached is 0:
    reached = testRange

print(round(time.time()-t0,1),'seconden')
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


print('Gemiddelde beloning laatste duizend:',mean(beloning_hist[-1000:]))
print('Gemiddeld verschil met willekeurig kiezen laatste duizend:',mean(diff_hist[-1000:]))


N = min(round(reached/1000),1)

#alles opslaan
saveStats({
          'loss': loss_hist,
          'loss_smooth': smooth(loss_hist,20),
          
          'beloning' : beloning_hist,
          'beloning_smooth' : smooth(beloning_hist,N),
          
          'verschil_met_random' : diff_hist,
          'verschil_met_random_smooth': smooth(diff_hist,N),
          
          'validation' : val_hist,
          'validation_smooth':  smooth(val_hist,N),    
          
          'epsilon' : epsilon_hist,
          
          'cijfer' : cijfer_hist,
          'cijfer_smooth' : smooth(cijfer_hist,N),
          
          'alleen_'+str(vast_uren)+'_uren' : fixed_hist,
          'alleen_'+str(vast_uren)+'_uren_smooth' : smooth(fixed_hist,round(N/4)),
          
          'aantal_uren_per_week' : frequentie_hist,
          'aantal_uren_per_week_smooth' : smooth(frequentie_hist,N)
          }, True)