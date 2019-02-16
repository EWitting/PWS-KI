from visualisatie import drawBlock, preProcess
import model
import pygame
import math

print('imports klaar, nu ai laden')

x_dim = 100
y_dim = 30
left = 50
top = 30
handvat_hoogte = 50

background_colour = (50,50,50)

   
schema =[False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,False,False,False,False,False,False,False,False,False,False,False ,False,False,False,False,False,False,False,False,True,True ,False ,False ,False,False,False,False,False,False,False,False,False,False,False,False ,False,False,False,False,False,False,False,True,True,True ,True ,False ,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,True,True,True,True,False,False,False,False,False,False,False,False,False,False,False ,False,False,False,False,False,False,False,False,True,True ,False ,False ,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]
penalty = 1.5
max_penalty = 1.5
moeilijkheidsfactor = 0.9
ai = model.agent(load = 'model.h5')
ai.epsilon = 0
beloning, leeruren, ID = ai.voorspel(schema,moeilijkheidsfactor,False,0,0.1,penalty)
print('ai geladen')

def refresh():
    global beloning,leeruren,ID, planning, schema
    beloning, leeruren, ID = ai.voorspel(schema,moeilijkheidsfactor,False,0,0.1,penalty)
    planning = preProcess(schema,leeruren)
    

 

planning = preProcess(schema,leeruren)
dagen = math.ceil(len(planning)/24)    

pygame.init()
pygame.display.set_caption('visualisatie van planning')
screen = pygame.display.set_mode((x_dim*dagen+left,y_dim*24+top+handvat_hoogte))
screen.fill(background_colour)    
clock = pygame.time.Clock() 

pygame.font.init() 
lefts = []
tops = []
dagTeksten = ['zo','ma','di','wo','do','vr']
myFont = pygame.font.SysFont('Arial', y_dim)

for i in range(24):
    lefts.append(myFont.render(str(i), False, (255, 255, 255)))        
for i in range(dagen):
    tops.append(myFont.render(dagTeksten[i], False, (255, 255, 255)))    


#scherm loop
done = False
slepen = False
frame = 0

while not done:
    handvat_x_dim = 20
    handvat_x = penalty/max_penalty*(dagen*x_dim-left)+left - handvat_x_dim/2
    
    pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    done = True     
                    
            if event.type == pygame.MOUSEBUTTONUP:
                if slepen:
                    slepen = False
                    print(round(penalty,2),round(beloning + penalty*sum(leeruren),1))
                    refresh()
                
                #vind aangeklikt uur:
                if pos[1] < top + 24*y_dim and pos[0] > left:
                    dag = math.floor( (pos[0]-left)/x_dim )
                    uur = math.floor((pos[1] - top)/y_dim) + dag * 24
                    if uur < len(schema):
                        schema[uur] = not schema[uur]
                        if not schema[uur]:
                            leeruren[uur] = False
                        refresh()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:           
                if pos[0] > handvat_x and pos[0] < handvat_x + handvat_x_dim and pos[1] > top+24*y_dim:
                    slepen = True
                    
    #check voor veranderende penalty op interval
    if slepen and frame % 5 == 0:
        refresh()
    
    
    #verander penalty
    if slepen:
        penalty = min(max((pos[0]-left)/(dagen*x_dim-left)*max_penalty,0),max_penalty)               
    
    #reset
    screen.fill(background_colour)        
    
    #teken uren 
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
    
    #blit tekst
    for x, text in enumerate(lefts,0):
        screen.blit(text,(handvat_x_dim/2,top + y_dim * x))
        
    for x, dag in enumerate(tops,0):
        screen.blit(dag,(x_dim*x + left,0))
                            
    #teken balkje
    rect = pygame.Rect(left,24*y_dim+top+round(handvat_hoogte/2 - handvat_hoogte/8),dagen*x_dim-left,round(handvat_hoogte/4))
    pygame.draw.rect(screen, (100,100,100), rect)
    
    #teken 'handvat'
    rect = pygame.Rect(handvat_x,24*y_dim+top,handvat_x_dim,handvat_hoogte)
    pygame.draw.rect(screen, (200,200,200), rect)
    
    #teken penalty tekst
    penTekst = myFont.render(str(round(penalty,1)), False, (255, 255, 255))
    screen.blit(penTekst,(5,y_dim*24 + top+handvat_hoogte/8))
    
    pygame.display.flip()
    clock.tick(60)
    frame += 1
    
    if done:
        pygame.quit()