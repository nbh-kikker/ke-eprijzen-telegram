# Energie-Telegram

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

## Inleiding

De Energie-Telegram module verzorgt de verbinding met Telegram om je op de hoogte te stellen van energieprijzen. Ontvang direct meldingen zodra prijzen bepaalde drempels bereiken.

## Functionaliteiten

- **Notificatiesysteem**: Stuur meldingen via Telegram bij specifieke prijsdrempels.
- **Flexibele configuratie**: Pas meldingscriteria aan op basis van je voorkeuren.

## Installatie

Je kunt deze repository gebruiken met de Poetry package manager, als Docker-container, of met de Pixi package manager.

### Optie 1: Poetry

1. **Kloon de repository:**
   ```bash
   git clone https://github.com/ePrijzen/energie-telegram.git
   cd energie-telegram
   ```

2. **Installeer Poetry:**
   Zorg ervoor dat je [Poetry](https://python-poetry.org/docs/#installation) geïnstalleerd hebt.

3. **Installeer de afhankelijkheden:**
   ```bash
   poetry install
   ```

4. **Voer de applicatie uit:**
   ```bash
   poetry run python main.py
   ```

### Optie 2: Docker en Poetry

1. **Installeer Docker:**
   Zorg ervoor dat Docker op je systeem is geïnstalleerd. [Download Docker](https://docs.docker.com/get-docker/)

2. **Bouw de Docker-container:**
   ```bash
   docker build -t energie-telegram .
   ```

3. **Start de container:**
   ```bash
   docker run -d energie-telegram
   ```

### Optie 3: Pixi

1. **Kloon de repository:**
   ```bash
   git clone https://github.com/ePrijzen/energie-telegram.git
   cd energie-telegram
   ```

2. **Installeer Pixi:**
   Volg de installatie-instructies op de [Pixi website](https://pixi.js.org/).

3. **Installeer de afhankelijkheden:**
   ```bash
   pixi install
   ```

4. **Start de applicatie:**
   ```bash
   pixi run start
   ```

## Gebruik

Voorbeelden van hoe je de Energie-Telegram kunt gebruiken:

```bash
python main.py --threshold 0.05
```

## Contactinformatie

Voor vragen of ondersteuning, neem contact op met:

- **Theo van der Sluijs**
  - **Website:** [itheo.tech](https://itheo.tech)
  - **E-mail:** [theo@vandersluijs.nl](mailto:theo@vandersluijs.nl)
  - **GitHub:** [tvdsluijs](https://github.com/tvdsluijs)

## Licentie

Dit project is gelicentieerd onder de MIT-licentie. Zie het [LICENSE-bestand](https://github.com/ePrijzen/energie-telegram/blob/main/LICENSE) voor meer details.
