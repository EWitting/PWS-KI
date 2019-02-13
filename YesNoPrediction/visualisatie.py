import pygame
import math
from model import getID
import time

x_dim = 100
y_dim = 30
left = 30
top = 30

background_colour = (50,50,50)

def metHex(schema,hexData):
    tmp = bin(int(hexData, 16))[2:].zfill(len(schema))
    leeruren = []
    
    for i in tmp:
        if i == '1':
            leeruren.append(True)
        else:
            leeruren.append(False)
    return leeruren
    

def preProcess(schema,leeruren):
    rooster = []
    for i in range(len(schema)):
        if schema[i] and leeruren[i]:
            rooster.append(2)
        elif schema[i]:
            rooster.append(1)
        else: 
            rooster.append(0)
    return rooster
            
def visualiseer(schema,leeruren,screenshot,naam):
    planning = preProcess(schema,leeruren)
    pygame.init()
    pygame.display.set_caption('visualisatie van planning')
    
    dagen = math.ceil(len(planning)/24)
    
    screen = pygame.display.set_mode((x_dim*dagen+left,y_dim*24+top))
    screen.fill(background_colour)
    #pygame.display.iconify()
    
    clock = pygame.time.Clock()
    
    done = False
    
    pygame.font.init() 
    lefts = []
    tops = []
    dagTeksten = ['zo','ma','di','wo','do','vr']
    myFont = pygame.font.SysFont('Arial', y_dim)
    
    for i in range(24):
        lefts.append(myFont.render(str(i), False, (255, 255, 255)))
        
    for i in range(dagen):
        tops.append(myFont.render(dagTeksten[i], False, (255, 255, 255)))
    
    
    while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True                           
        #reset
        screen.fill(background_colour)        
        
        loc = [left,top]
        for i in range(len(planning)):
            if i % 24 == 0 and i != 0:
                loc[1] = top
                loc[0] += x_dim
            
            isLast = False
            if i == len(planning) - 1:
                isLast = True
            drawBlock(screen, planning[i],loc[0],loc[1],isLast)
            loc[1] += y_dim
        
        for x, text in enumerate(lefts,0):
            screen.blit(text,(0,top + y_dim * x))
            
        for x, dag in enumerate(tops,0):
            screen.blit(dag,(x_dim*x + left,0))
                
        if screenshot:
            
            t = time.localtime()
            timestamp = time.strftime('%b-%d-%Y_%H%M', t)
            pygame.image.save(screen,naam+".jpg")
            done = True
                
        pygame.display.flip()
        clock.tick(30)

        if done:
            pygame.quit()



def drawBlock(screen, index,x,y,isLast):
    col = (50,50,50)
    if index == 1:
        col = (100, 140, 200)
    elif index == 2:
        col = (0,255,0)
    
    if isLast:
        col = (255,0,0)
    rect = pygame.Rect(x,y,x_dim,y_dim)
    pygame.draw.rect(screen, col, rect)
    pygame.draw.rect(screen, (0,0,0), rect,1)
    
    
if __name__ == '__main__':
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
    leeruren = '0x0'
    
    visualiseer(schema,metHex(schema,leeruren),False)
    
