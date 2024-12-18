# Klopta: AI-Tool voor Stad Antwerpen  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)  
[![Build Status](https://img.shields.io/github/actions/workflow/status/bazaaer/AppliedAiProject/ci.yml?branch=main)](https://github.com/bazaaer/AppliedAiProject/actions)  
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)  
[![Contributors](https://img.shields.io/github/contributors/bazaaer/AppliedAiProject)](https://github.com/bazaaer/AppliedAiProject/graphs/contributors)  

**Klopta** is een AI-gebaseerde applicatie die redacteurs van Stad Antwerpen ondersteunt bij het maken van hoogwaardige content. Het integreert **Checket**, een krachtige AI-assistent, om teksten te analyseren, verbeteren en herschrijven, terwijl consistentie met de huisstijl van de stad wordt gegarandeerd.  

## ✨ Kernfunctionaliteiten  

### 📊 **Stijl rating**  
Beoordeelt hoe goed een tekst overeenkomt met de huisstijl van Stad Antwerpen. Het model vergelijkt geschreven teksten met de gewenste toon, stijl en helderheid.  

### ✍️ **Zinsherschrijving**  
Herschrijft zinnen om complexiteit te verminderen en leesbaarheid te verhogen. De originele betekenis blijft behouden, terwijl de stijl overeenkomt met de standaarden van de stad.  

### 🔗 **Zinsgroepering**  
Groepeert zinnen contextueel met behulp van **SpaCy**, zodat herschrijvingen en analyses logisch blijven en samenhang behouden blijft.  

## 📚 Technische Overzicht  

### 🔧 **Kerncomponenten**  
1. **CKEditor Plugin (React-based):**  
   Een gebruiksvriendelijke plugin waarmee redacteurs direct binnen hun CMS toegang krijgen tot de AI-functies van Checket.  

2. **AI Backend (Quart API & Rayserve):**  
   - **Stijl rating (SBERT):** Gebruikt het [ODeNy/ChecketV2](https://huggingface.co/ODeNy/ChecketV2) om de consistentie van de tekst met de stadshuisstijl te beoordelen.  
   - **Zinsherschrijving (GEITje-7B-ultra):** Herschrijft teksten in natuurlijk Nederlands met behoud van context en stijl.  

3. **Dockerized Deployment:**  
   De volledige applicatie is containerized, waardoor het eenvoudig is om te implementeren en te onderhouden.  

4. **Beveiliging:**  
   Klopta gebruikt een veilige API met encryptie en rolgebaseerde autorisatie.  

## 🚀 Installatie en Gebruik  

### Vereisten  
- **Server:** Linux-server met GPU-ondersteuning (NVIDIA). 32GB aan VRAM is geadviseerd, maar minder kan ook.
- **Software:**  
  - [Docker](https://www.docker.com/)  
  - [Docker Compose](https://docs.docker.com/compose/)  

### Installatie  
1. **Clone de repository:**  
   ```bash
   git clone https://github.com/bazaaer/AppliedAiProject.git
   cd klopta
   ```  

2. **Start de containers:**  
   ```bash
   docker compose up --build
   ```  

3. **Toegang tot de API-documentatie:**  
   Zodra de service draait, is documentatie beschikbaar op `http://<server-ip>:<port>/api/docs`.  

## 👥 Bijdragen  
Bijdragen zijn welkom! Volg deze stappen:  
1. Fork de repository.  
2. Maak een nieuwe branch (`git checkout -b feature/new-feature`).  
3. Commit je wijzigingen (`git commit -m 'Voeg nieuwe feature toe'`).  
4. Push naar je branch (`git push origin feature/new-feature`).  
5. Open een pull request.  

## 📄 Licentie  
Dit project valt onder de [MIT-licentie](LICENSE).  

## 📧 Contact  
Voor vragen of ondersteuning, neem contact op via **lander@vanderstighelen.net**.  

We hopen dat Klopta een waardevolle aanvulling is voor Stad Antwerpen! 🎉