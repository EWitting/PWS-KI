import pygame
import math
import binascii

x_dim = 100
y_dim = 30
background_colour = (150,150,150)

def metHex(schema,hexData):
    tmp = bin(int(hexData, 16))[2:].zfill(len(schema))
    leeruren = []
    
    for i in tmp:
        if i == '1':
            leeruren.append(True)
        else:
            leeruren.append(False)
    visualiseer(schema, leeruren)
    

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
            
def visualiseer(schema,leeruren):
    planning = preProcess(schema,leeruren)
    pygame.init()
    pygame.display.set_caption('visualisatie van planning')
    
    dagen = math.ceil(len(planning)/24)
    
    print(len(planning),dagen)

    screen = pygame.display.set_mode((x_dim*dagen,y_dim*24))
    screen.fill(background_colour)
    
    clock = pygame.time.Clock()
    
    done = False
    
    
    
    while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True   
                        
        #reset
        screen.fill(background_colour)
        
        
        loc = [0,0]
        for i in range(len(planning)):
            if i % 24 == 0 and i != 0:
                loc[1] = 0
                loc[0] += x_dim
            
            drawBlock(screen, planning[i],loc[0],loc[1])
            loc[1] += y_dim
            
        
        
        pygame.display.flip()
        clock.tick(30)

        if done:
            pygame.quit()

def drawBlock(screen, index,x,y):
    col = (50,50,50)
    if index == 1:
        col = (100, 140, 200)
    elif index == 2:
        col = (0,255,0)
    rect = pygame.Rect(x,y,x_dim,y_dim)
    pygame.draw.rect(screen, col, rect)
    pygame.draw.rect(screen, (0,0,0), rect,1)
    
    
if __name__ == '__main__':
    schema =   [False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,True,True,True,True,True,True,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,True,True,True,True,True,True,False,False,False,False,False,False,False,False,True,True,False,False,False,False,False,False,False,False,True,True,True,True,True,True,False,False]
    leeruren = '0x300c0000000000000'
    
    metHex(schema,leeruren)
    
