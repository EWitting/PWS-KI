# PWS-KI
Deze repositorie bevat de code voor mijn profielwerkstuk over kunstmatige intelligentie en efficiente leermomenten


De pseudocode voor de simulatie die het leerproces modelleert(gebruikte getallen zijn voorbeelden, niet definitief): 
```python
Onthouden Stof OS = 0 
Verval V = 0,95 
Leersnelheid LS = 0,75 
verval van verval VV
Voor elk uur in week: 
    Als niet wordt geleerd: 
        OS = OS * V 
    Als wel wordt geleerd: 
        OS = OS + LS*(1 - vermoeidheidsfactor)*(1 - OS) 
        V = V + VV*(1-V)
Cijfer = Laagste (OS * 9 * moeilijkheidsgraad) + 1 + willekeurig getal, 10) 
```

De opzet voor het leerproces van het netwerk:

```
Zolang aan het trainen, herhaal:  
    Kies willekeurig het getal voor de moeilijkheidsgraad van dit hoofdstuk 
    Voor elk uur in week: 
        Als uur is vrije tijd: 
        Voorspel cijfer m.b.v. netwerk 
    Selecteer de n uren met de hoogste voorspelde cijfers 
    Doorloop simulatie en kies om te leren op geselecteerde uren 
    Sla behaalde cijfer tijdelijk op 
    Voor elk uur in de selectie: 
        Voeg de situatie van dat uur samen met het behaalde cijfer toe aan de experiences 
    Train netwerk op willekeurig geselecteerde groep uit experiences.
```
