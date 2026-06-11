# PAC-MAN projekti dokumentatsioon

## 1. Sissejuhatus

Selles projektis täiendasin ja kombineerisin Python/Pygame abil Pac-Mani laadseid mänge. Põhiliseks lähtemänguks valisin `pacman1.py`, kus olid juba olemas suurem kaart, klassid `Pacman`, `Ghost` ja `Game`, BFS-teekonnaotsing, power pellet'id, skoor, elud ja levelid.

Teise mänguna kasutasin võrdluseks `pacman2.py`, mis on lihtsam beginner-versioon. Sellest sain ideid lihtsama mängurežiimi, väiksema kummituste arvu, juhusliku kummituste liikumise ja selgete ekraanisõnumite jaoks.

Lõppversioon on failis `pacman_arvestus.py`. Algseid faile `pacman1.py` ja `pacman2.py` ei kirjutanud üle, et oleks võimalik oma panust võrrelda algmaterjaliga.

## 2. Leitud mängud ja nendega tutvumine

### 2.1 Mäng 1 - PAC-MAN Python/Pygame (`pacman1.py`)

- Täielikum Pac-Mani laadne Pygame mäng.
- Kasutab tekstipõhist kaarti `RAW_MAP`.
- Kummitused kasutavad BFS-teekonnaotsingut, et Pacmani jälitada.
- Olemas on power pellet'id, skoor, elud, paus, restart ja levelite süsteem.
- Testimisel jälgisin kollide liikumist, punktide kogumist, power-up'i mõju ja leveli lõpetamist.

### 2.2 Mäng 2 - Pac-Man Beginner Version (`pacman2.py`)

- Lihtsustatud Pac-Mani versioon väiksema ruudustikuga.
- Kummitused liiguvad juhuslikult.
- Skoor ja elud kuvatakse ekraanil.
- Failist sain ideid beginner mode'i, lihtsama kaardi, väiksema kummituste arvu ja sõnumite kuvamise jaoks.

## 3. Otsus

Baasmänguks valisin `pacman1.py`, sest see oli paremini struktureeritud ja seda oli lihtsam laiendada. Seal olid juba eraldi klassid mängija, kummituste ja mängu üldise loogika jaoks.

`pacman2.py` kasutasin ideede allikana. Sealt võtsin beginner-versiooni põhimõtte: lihtsam mängukogemus, vähem kummitusi ja juhuslikum vaenlaste liikumine.

## 4. Tehtud täiustused ja kombineerimine

### 4.1 Classic Mode ja Beginner Mode

Lisasin menüü, kus saab valida kahe režiimi vahel:

- `Classic Mode` - kasutab nelja kummitust ja BFS-põhist jälitamist.
- `Beginner Mode` - kasutab kahte aeglasemat kummitust ja random walk'i, seega kummitused ei jälita Pacmani agressiivselt.

Classic Mode'i testimisel parandasin ka kummituste algpositsiooni vea: neljas kummitus alustas alguses seina sees. Paranduse järel alustavad kõik neli kummitust ghost house'i vabadel ruutudel.

### 4.2 Beginner Mode'i kummituste AI parandus

Parandasin Beginner Mode'i loogikat nii, et kummitused ei kasuta tavaliikumisel BFS-i. Selle asemel liiguvad nad juhuslikult lubatud suundades. Power pellet'i ajal töötab endiselt fright-loogika ning kummitused liiguvad samuti juhuslikult.

### 4.3 Klahvide parandamine

Parandasin klahvide loogikat:

- liikumine töötab nooleklahvidega;
- liikumine töötab ka `WASD` klahvidega;
- `R` on ainult restart;
- `R` töötab ka menüüs ja alustab praeguse režiimi uuesti;
- `M` viib menüüsse;
- `P` paneb mängu pausile.

Menüü alumine infotekst muutub nüüd vastavalt aktiivsele režiimile, mitte ei kuva alati Beginner Mode'i teksti.

### 4.4 Ekraanisõnumid

Lõppversioonis kuvatakse overlay-sõnumeid:

- pausil;
- elu kaotamisel;
- leveli lõpetamisel;
- mängu lõpus.

### 4.5 Boonusvili

Lisasin boonusvilja, mis ilmub teatud punktide kogumise järel. Kui Pacman jõuab viljani enne aja lõppu, saab mängija lisapunkte.

### 4.6 High score muudatus

Varasemas versioonis salvestati high score faili `pacman_highscore.txt`. Paranduste käigus eemaldasin `.txt` faili salvestamise. Nüüd hoitakse parimat skoori ainult programmi jooksutamise ajal mälus. Kui mäng kinni panna ja uuesti avada, alustavad seaded ja high score baasväärtustelt.

### 4.7 Koodi korrastamine

Koodi korrastamisel:

- eemaldasin kasutamata `Path` impordi;
- eemaldasin kasutamata värvikonstandi;
- eemaldasin failipõhise high score lugemise ja kirjutamise;
- lisasin `ai_mode` väärtuse, et Classic ja Beginner kummitused kasutaksid erinevat loogikat;
- parandasin neljanda kummituse spawn-ruudu klassikalises kaardis;
- muutsin menüü infoteksti valitud režiimist sõltuvaks;
- täpsustasin kommentaare ja docstringe keerulisemate kohtade juures.

## 5. Testimine ja probleemid

Testimise kohta on eraldi logi failis `testimine.txt`. Iga testimiskatse juures on kirjas:

- mida testisin;
- mis viga või probleem tekkis;
- mis oli põhjus;
- kuidas vea lahendasin.

Kokku dokumenteerisin 17 testimiskatset. Neist 11 puhul ilmnes viga või parandamist vajav koht. Kõik koodiga seotud probleemid said lahendatud.

Peamised probleemid olid:

- algne klahvide konflikt;
- menüü oleku lisamine;
- kummituste arv eri režiimides;
- Beginner Mode'i liiga agressiivne BFS-põhine AI;
- Classic Mode'i neljanda kummituse vale spawn-ruut;
- Pacmani algpositsioon beginner-kaardil;
- tunneli ja collision-loogika;
- high score `.txt` salvestuse eemaldamine;
- menüüs mittetöötav `R` restart;
- menüü alumise info teksti vale režiim;
- õige Python/Pygame keskkonna kasutamine.

## 6. Failid

Projektis on olulised failid:

- `pacman1.py` - esimene algne Pac-Mani mäng;
- `pacman2.py` - teine algne lihtsustatud Pac-Mani mäng;
- `pacman_arvestus.py` - minu täiustatud ja kombineeritud lõppversioon;
- `testimine.txt` - testimislogi;
- `dokumentatsioon.md` - projekti dokumentatsioon;
- `README.md` - käivitamisjuhend;
- `requirements.txt` - vajalik Pygame teek.

## 7. Käivitamine

Selles arvutis töötas mäng Python 3.12 ja Pygame 2.6.1 keskkonnas:

```powershell
cd "C:\Users\PC\.vscode\Projects\Pygame'i asjad"
py -3.12 pacman_arvestus.py
```

## 8. Ette näitamine

Ette näitamisel demonstreerin:

- algseid faile `pacman1.py` ja `pacman2.py`;
- lõppfaili `pacman_arvestus.py`;
- Classic Mode'i;
- Beginner Mode'i;
- kummituste erinevat käitumist eri režiimides;
- skoori, elusid, power pellet'e, boonusvilja ja overlay-sõnumeid;
- dokumentatsiooni ja testimislogi.

## Moodle ülesande nõuete kontroll

1. Leia 2-3 Pac-Man laadseid pygame mänge.

   Leidsin ja kasutasin kahte Pac-Mani laadset Pygame faili: `pacman1.py` ja `pacman2.py`.

2. Tutvu nendega, mängi neid läbi.

   Tutvusin mõlema mängu kaardi, liikumise, punktide, elude ja kummituste loogikaga. `pacman1.py` oli keerukam ning `pacman2.py` lihtsam beginner-versioon.

3. Otsusta, mis mängu hakkad täiustama.

   Valisin täiustamiseks `pacman1.py`, sest selle struktuur oli sobivam edasiarenduseks. `pacman2.py` kasutasin ideede allikana.

4. Täienda/Kombineeri PAC-MAN mängu.

   Lõppversioon `pacman_arvestus.py` kombineerib `pacman1.py` põhistruktuuri ja `pacman2.py` lihtsustatud beginner-mängu ideed. Lisasin menüü, Classic/Beginner mode'i, beginner random walk AI, boonusvilja, overlay-sõnumid ja korrastatud klahviloogika.

4.1. Loo testimise tekstifail.

   Testimise logi on failis `testimine.txt`. Seal on iga katse kohta kirjas muudatus, tekkinud probleem ja lahendus. Lõpus on kokkuvõte vigadest ja lahendustest.

4.2. Töö peab olema dokumenteeritud.

   Dokumentatsioon on failis `dokumentatsioon.md`. Seal on kirjas lähtemängud, valitud baasmäng, tehtud muudatused, probleemid, lahendused ja ette näitamise plaan.

5. Kommenteeri moodulite/funktsioonide/klasside kaupa.

   `pacman_arvestus.py` sisaldab klasside ja funktsioonide docstringe ning kommentaare keerulisemate kohtade, näiteks BFS-i, random walk'i, tunneli ja boonusvilja kohta.

6. Lisa kood ja muud vajaminevad failid koodihoidlasse.

   Koodihoidlasse tuleb lisada `pacman1.py`, `pacman2.py`, `pacman_arvestus.py`, `testimine.txt`, `dokumentatsioon.md`, `README.md` ja `requirements.txt`.

7. Laadi kõik failid Moodlesse ning lisa koodihoidla link.

   Moodlesse tuleb laadida kõik projekti failid ja lisada GitHubi või muu koodihoidla link.

8. Tuleb ette näidata tehtud kombineeritud mäng ning tõendada dokumentatsiooni ja algsete mängufailidega oma panust.

   Ette näitamisel saab võrrelda algseid faile `pacman1.py` ja `pacman2.py` lõppfailiga `pacman_arvestus.py`. Dokumentatsioon ja testimislogi näitavad, millised muudatused on lisatud ja kuidas probleemid lahendati.
