import random

def genereer_week():
            #zondag
    schema =[False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True,False,False,False,
            #maadag
            False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True,False,False,False,
            #dinsdag
            False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True,False,False,False,
            #woensdag
            False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True,False,False,False,
            #donderdag
            False,False,False,False,False,False,False,False,False,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True ,True,False,False,False,
            #vrijdag
            False,False,False,False,False,False,False,False,False,False,False,False,False]    
       
    dagen = 6
    for dag in range(dagen):
        if dag is not 0 and dag is not dagen - 1:
            aantal = random.choice(range(7,10))
            for i in range(aantal):
                schema[dag*24 + 9 + i] = False
            for i in range(random.choice(range(1,3))):
                tussenuur = random.choice(range(9,18))
                schema[dag*24+tussenuur] = True
            for i in range(random.choice(range(1,3))):
                tussenuur = random.choice(range(17,20))
                schema[dag*24+tussenuur] = False
    return schema