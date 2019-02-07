import random
import matplotlib.pyplot as plt

#"sleep urge" en "sleep need" afgelezen uit de grafiek uit het artikel van roovers
slaapbehoefte = [0.95, 0.9, 0.85, 0.75, 0.65, 0.5, 0.4, 0.3, 0.2, 0.1, 0.02, 0.12, 0.3, 0.4, 0.4, 0.32, 0.15, 0.05, 0.02, 0.1, 0.35, 0.65, 0.9, 0.95] 
slaapnoodzaak = [0.6, 0.45, 0.35, 0.35, 0.15, 0.1, 0.05, 0.08, 0.1, 0.15, 0.2, 0.23, 0.3, 0.31, 0.4, 0.42, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,0.75] 

#tel behoefte en noodzaak bij elkaar op om vermoeidheidsfactors te maken per uur van de dag
vmf = [round(slaapbehoefte[i] + slaapnoodzaak[i],1) for i in range(24)] 

#zorgt dat alle getallen in vermoeidheidsfactors tussen 0 en 0.5 veranderen, dit zorgt ervoor dat het leervermogen niet kleiner dan de helft kan worden van het origineel
vmf = [round(i/max(vmf)*0.5,1)for i in vmf] 

class Simulatie():
    def __init__(self,moeilijkheidsgraad):
        self.mg = moeilijkheidsgraad #moeilijkheidsgraad van toets tussen 0 en 1, 0 is onmogelijk en 1 is heel makkelijk
        self.os = 0 # onthouden leerstof tussen 0 en 1
        self.v = 0.975 # verval
        self.max_ls = 0.75 #max leersnelheid
        self.ls = self.max_ls # leersnelheid
        self.ls_verval = 0.5 #hoe snel je effectiviteit verlaagt als je te vaak achter elkaar leert
        self.vv = 0.5 # verval van verval(voor het effect van herhaald leren)
        self.index = 0 # geeft aan welk uur in de simulatie het is
        self.straf = 0
        
    #stapt 1 uur vooruit in de tijd, waarbij wel of niet geleerd wordt
    def stap(self, geleerd,penalty): 
        tijd = self.index % 24 #vindt het uur van de dag voor gebruik door vermoeidheidsfactor 
        if geleerd:
            self.os += self.ls*(1-vmf[tijd])*(1-self.os)
            self.ls *= self.ls_verval
            self.v += self.vv*(1 - self.v)*(0.5 + 0.5*self.ls)
            self.straf += penalty
            
        else:
            self.os *= self.v
            self.ls += (self.max_ls - self.ls) * (self.ls_verval + 0.5*(1 - self.ls_verval)) 
        self.index += 1
  
    #berekent het cijfer aand de hand van os en een afwijking tussen -0.5 en 0.5 met een decimaal, en houdt het binnen 1 en 10 voor als de afwijking een onmogelijk cijfer zou opleveren
    def toets(self,rand): 
        cijfer = round(max(min((self.os * self.mg * 9) + 1 + random.randint(-5,5)*rand ,10),1),1)
        return cijfer, round(cijfer - self.straf,1)
    
    
    #voert een aantal stappen uit aan de hand van een lijst met telkens True of False om te bepalen of er wel of niet geleerd moet worden, en geeft een cijfer terug
    def simuleer(self,leermomenten,rand,penalty): 
        for i in leermomenten:
            self.stap(i,penalty)
        return self.toets(rand)
    
    #voert een aantal stappen uit aan de hand van een lijst met telkens True of False om te bepalen of er wel of niet geleerd moet worden, en geeft een cijfer terug
    def plot(self,leermomenten,penalty): 
        hist = []
        for i in leermomenten:
            self.stap(i,penalty)
            hist.append(self.os)
        plt.plot(hist)
        plt.show()
        print(penalty)
        return self.toets(0.1)
    
    
if __name__ == "__main__":
    
    plt.plot(vmf)
    plt.show()
    
    sim = Simulatie(0.8)
    print('twee achter weg        ',sim.simuleer([False,True,True,False,False,False,False,False],0.0))
    sim = Simulatie(0.8)
    print('twee met één pauze     ',sim.simuleer([False,True,False,True,False,False,False,False],0.0))
    sim = Simulatie(0.8)
    print('drie dichtbij          ',sim.simuleer([False,True,True,True,False,False,False,False],0.0))
    sim = Simulatie(0.8)
    print('twee met pauze van twee',sim.plot([True,False,False,True,False,False,False,False],0.0))
    sim = Simulatie(0.8)
    print('plot',sim.plot([True,False,False,True,False,False,False,False,False,False,True,False,False,False,False,True,False,True,False,False,True,False,False,False,False],0.0))
    
