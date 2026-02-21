# Taloussuunnittelija (Python)

Tämä on Streamlit-pohjainen taloussuunnittelusovellus, jolla voit:

- lisätä tuloja ja menoja eri kategorioihin
- tarkastella dataa päivä-, viikko-, kuukausi- ja vuositasolla
- nähdä pylväsdiagrammin (tulot/menot/nettotulos)
- nähdä ympyrädiagrammin menojen jakaumasta

## Asennus

1. Siirry projektikansioon.
2. Luo virtuaaliympäristö (suositus):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Asenna riippuvuudet:

```bash
pip install -r requirements.txt
```

## Käynnistys

```bash
streamlit run app.py
```

Sovellus avautuu selaimeen (yleensä `http://localhost:8501`).

## Avaa sovellus kuvakkeesta

Projektissa on mukana käynnistimen luontiskripti:

```bash
python create_launcher.py
```

Tämä luo käyttöjärjestelmästä riippuen työpöydälle avauskuvakkeen/tiedoston:

- **Linux**: `.desktop`-käynnistin työpöydälle ja sovellusvalikkoon
- **Windows**: `.bat`-käynnistystiedosto työpöydälle
- **macOS**: `.command`-käynnistystiedosto työpöydälle

Kun käynnistyskuvaketta klikataan, se avaa Taloussuunnittelija-sovelluksen.

## Jakaminen kaverille

Voit lähettää kaverille koko projektikansion (tai Git-repon linkin). Kaveri voi käynnistää sovelluksen samoilla vaiheilla:

1. `pip install -r requirements.txt`
2. `python create_launcher.py` (valinnainen, jos haluaa avata kuvakkeesta)
3. `streamlit run app.py` (tai avaa luodusta kuvakkeesta)

Data tallennetaan paikallisesti tiedostoon `data/transactions.csv`.
