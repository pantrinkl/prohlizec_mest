# Prohlížeč měst

Tento program slouží k získání informací o městech a obcích dle vybraných kritérií a k jejich zobrazení na mapovém podkladu.

## Vstupní parametry

Ve složce, kde je uložen soubor `mesta.py`, je nutné mít další vstupní sobory:

* `obce.geojson` - soubor ve formátu GeoJSON, kde je seznam obcí a okresů, do kterých patří.

* `okresy.geojson` - soubor ve formátu GeoJSON, kde jsou uloženy informace o okresech.

* `kraje.geojson` - soubor ve formátu GeoJSON, kde jsou uloženy informace o krajích.

* `souradnice.geojson` - soubor ve formátu GeoJSON, kde jsou uloženy souřadnice obcí.

* `mesta.qml` - qml soubor s grafickým rozhraním aplikace.

## Práce s aplikací

Program po spuštění zobrazí seznam všech dostupných měst a obcí v ČR (seznam je neuplný). Po vybrání sídla je k němu doplněna jeho rozloha a počet obyvatel. Na vybrané sídlo je přiblíženo v mapové aplikaci.

Dále lze vyfiltrovat sídla dle různých parametrů. V nabídce lze vybrat mezi zobrazením měst nebo obcí. Lze nastavit v jakém rozsahu počtu obyvatel mají být zobrazená sídla. Ze seznamu krajů lze vybrat jeden, ze kterého bude vybrán požadovaný okres. Z okresů pak lze vybrat jeden, ze kterého budou sídla vybrána.