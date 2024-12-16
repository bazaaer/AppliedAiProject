# Klopta DevContainer Documentatie

Deze handleiding beschrijft hoe je de Klopta-ontwikkelomgeving instelt met een DevContainer-configuratie. De setup gebruikt Docker Compose en biedt ondersteuning voor NVIDIA GPU-acceleratie, MongoDB, Redis en AI-tools.

## Overzicht

**Belangrijke Services**  
- **MongoDB**: Database met root-gebruikersinstellingen.  
- **Redis**: Caching en token store.  
- **Ollama**: AI-modelhost met NVIDIA GPU-ondersteuning.  
- **DevContainer**: Hoofdservice met projectcode en packages.  

**Geïnstalleerde Features**  
- **Common-utils**: Inclusief `zsh`.  
- **Git**: OS-versie.  
- **Docker-in-Docker**: Voor Docker-commando’s in de container.  
- **PyTorch**: Voor AI modellen.  

**VSCode Extensies**  
Voor Python- en AI-ontwikkeling: `ms-python.python`, `ms-toolsai.jupyter`, `charliermarsh.ruff`, etc.

## Installatie

1. **Vereisten**  
   - [Docker](https://www.docker.com/)
   - [Docker Compose](https://docs.docker.com/compose/)
   - [VSCode](https://code.visualstudio.com/)

2. **Open in VSCode**  
   - Kies **Reopen in Container** als daarom gevraagd wordt.

3. **Wacht tot de Container is Gebouwd**  
   - Alle packages worden automatisch geïnstalleerd.


## Werkwijze

- **Workspace**: `/workspaces/AppliedAiProject`.  
- **Python Packages**: Worden geïnstalleerd via `postCreateCommand`.  
- **Database Verbinding**:  
  ```
  MONGO_HOST=mongodb
  MONGO_PORT=27017
  MONGO_USER=root
  MONGO_PASSWORD=examplepassword
  ```
- **Redis**: Beschikbaar op `redis:6379`.  
- **Ollama**: LLM host

## Aanpassingen

- **Extensies**: Voeg extra extensies toe in `devcontainer.json`.  
- **Post-Create Command**: Pas aan voor extra tools of packages.  
- **Omgevingsvariabelen**: Werk deze bij in `docker-compose.yml`.  


## Stoppen

Sluit VSCode om alle actieve services te stoppen.  

## Problemen Oplossen

- **Buildfouten**: Controleer of Docker en GPU-drivers correct zijn geïnstalleerd.  
- **Connectiviteit**: Check netwerkconfiguraties in `docker-compose.yml`.  

Deze setup biedt een GPU-geoptimaliseerde omgeving voor Klopta’s AI en API-ontwikkeling. Neem bij vragen contact op met de projectbeheerders.