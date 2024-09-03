# Submarine Assignment
An assigment regarding effective python code.

# NOTES
## Teknisk bakgrund och val
### SubmarineSystem klassen
- Själva user interfacet, man skapar ett submarine system objekt som man sedan interagerar med som användare.

### SubmarineSystem._SubmarineRegistry klassen
- Fungerar som en dictionary med alla ubåtar i.
- Är en privat del av SubmarineSystem, man får inte instansiera register manuellt!

### SubmarineSystem._Submarine klassen
- Använder property och setter dekoratorerna
- Möjliggör så att när man ändrar serienummret på ubåten så kan man kolla innan om serienummret är tillåtet.
- Är en privat del av SubmarineSystem, man får inte instansiera ubåtar manuellt!

## Avgränsningar och fokus
- Fokuset är att göra en väl skriven OOP kod, inte att det ska vara ett realistiskt system för ubåtar.

## Källhänvisningar
- Inga just nu.