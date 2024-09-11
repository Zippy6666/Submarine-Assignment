# Submarine Assignment
An assigment regarding effective python code.

# NOTES
## Teknisk bakgrund och val
### SubmarineSystem klassen
- Själva user interfacet, man skapar ett submarine system objekt som man sedan interagerar med som användare.
- Håller koll på alla ubåter i ett dictionary. Detta möjliggör snabb hämtning av ubåtar. Dictionaryt indexeras genom ubåtens serie-nummer.
- Gör systemet lätt för använderare att interagera med, man behöver endast använda ett SubmarineSystem objekt för att kunna sköta systemet.
- Man kan aldrig få ett ubåts-objekt från systemet, bara en "rapport"

### SubmarineSystem._Submarine klassen
- En klass som representerar en ubåt.
- Är en privat del av SubmarineSystem klassen.
- Bör ej instansiearas av användaren, endast genom ett SubmarineSystem objekt.

### Rörelse Loggning
- Loggningen får inte vara för dyr
- Använder en deque för att logga rörelser, ett bestämt antal loggar sparas i den, gamla tas bort när den blir full
- Tupler representerar varje rörelse, visar position innan och efter, samt riktning och avstånd för rörelsen

## Avgränsningar och fokus
- Fokuset är att göra en väl skriven OOP kod, inte att det ska vara ett realistiskt system för ubåtar. Däremot, om det fanns en värld där tusentals tvådimisionella ubåtar behövde ett system, vill jag fortfarande att mitt system ska kunna utföra uppdraget.

## Källhänvisningar
- Inga just nu.