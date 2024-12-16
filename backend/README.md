# Klopta Backend Documentatie

Deze documentatie geeft een overzicht van de Klopta-backend met de nadruk op de AI-modellen die in het systeem zijn geïntegreerd. Algemene API-documentatie is beschikbaar op `/api/docs` wanneer de container draait.

## AI-componenten

### **1. Zinsplitsing (SpaCy-gebaseerd)**  
- **Functionaliteit**: Groepeert zinnen op basis van gedeelde context, zoals onderwerp of verhaallijn. Zinnen met hetzelfde onderwerp of die een gedachtegang voortzetten, worden gegroepeerd voor betere verwerking.  
- **Gebruik**: Bereidt tekst voor op nauwkeuriger scoren en herschrijven door logische zinsgroeperingen te behouden.  
- **Implementatie**: Gebruikt SpaCy's Nederlandse taalmodel (`nl_core_news_md`) om zinnen contextueel te splitsen.

### **2. Zinsbeoordeling (BERT-gebaseerd)**  
- **Model**: Een aangepast Sentence-BERT (SBERT)-model, getraind voor stilistische gelijkenisanalyse.  
- **Dataset**:  
  - Model: [ODeNy/ChecketV2](https://huggingface.co/ODeNy/ChecketV2)  
  - Dataset: [ODeNy/ChecketV2-Dataset](https://huggingface.co/datasets/ODeNy/ChecketV2-Dataset)  
- **Functionaliteit**: Beoordeelt zinnen om te bepalen hoe goed ze overeenkomen met de schrijfstijl van originele website-inhoud.  
- **Gebruik**: Zorgt voor kwaliteitscontrole van herschreven of nieuwe inhoud door consistentie met een gevestigde stijl te evalueren.

### **3. Tekstherschrijven (Nederlands LLM)**  
- **Model**: Een fijn afgestemd Nederlands LLM: [BramVanroy/GEITje-7B-ultra](https://ollama.ai/models/BramVanroy/GEITje-7B-ultra).  
- **Implementatie**:  
  - Geoptimaliseerd met hyperparameters voor het herschrijven van Nederlandse teksten.  
  - Gebruikt geavanceerde prompt-engineering om coherente en contextueel passende herschrijvingen te garanderen.  
- **Functionaliteit**: Herschrijft teksten om de leesbaarheid te verbeteren en een consistente toon of stijl te behouden. Ideaal voor toepassingen zoals inhoudsverbetering of parafraseren.

## Ontwikkelingsbronnen

### **Projectrepository**  
De backend integreert deze AI-componenten in de verwerkingspipeline. Zorg ervoor dat je ontwikkelomgeving is geconfigureerd volgens de vereisten in de `devcontainer`- en instellingsbestanden van de repository.

### **Deployment**  
Ontworpen voor GPU-versnelde Docker-containers. Controleer de modelprestaties met ingebouwde tools van Ray Serve (admin-toegang vereist).

## Contactinformatie

Voor vragen of problemen:  
- **Naam**: Bazaaer  
- **E-mail**: lander@vanderstighelen.net  