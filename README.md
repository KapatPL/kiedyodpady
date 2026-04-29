


# Konfiguracja dodatku

```
localityId:       "0920404"                         # Kod Józefów
streetId:         "19719"                           # id Ulicy
number:           "4"                               # Numer Lokalu
property_type:    "Zamieszkana"                     # Typ
building_type:    "Jednorodzinna"                   # Typ
origin: "https://jozefow.kiedyodpady.pl"            # Adres Strony
```

# Konfiguracja w dashboard
```
type: entities
entities:
  - entity: sensor.data_odbioru_odpadow
    name: Data odbioru
  - entity: sensor.co_odbieraja_odpady
    name: Co odbierają
  - entity: sensor.dni_do_odbioru_odpadow
    name: Za ile dni
theme: Mushroom Square Shadow
show_header_toggle: false
state_color: false
title: Informacjie o odbiorze odpadów
```
