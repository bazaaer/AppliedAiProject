# Finetuning van een SBERT Model

## Vereisten

Voordat je begint, zorg ervoor dat je het volgende hebt:  
- **Dataset**: Een web-gescrapete CSV-dataset van *antwerpen.be* of vergelijkbare data (we hebben ElasticSearch gebruikt om data van de officiële Antwerpse websites te extraheren).  
- **Tijd**: Tot **5 dagen** of toegang tot een high-performance computing setup om synthetische trainingsdata te genereren.  
- **Geduld en Koffie**: Het trainen kan enige tijd duren, dus zorg ervoor dat je goed gecaffeïneerd en klaar bent!

---

## Stappen om het SBERT Model te finetunen

### 1. **Bereid de Dataset voor**  
   Voer het volgende script uit om de web-gescrapete dataset schoon te maken:  
   ```bash
   python data_cleaning.py
   ```

### 2. **Stel de Omgeving In**  
   Start de benodigde services voor je project:  
   ```bash
   docker compose up
   ```

### 3. **Download het Basis Model**  
   Pull het basismodel voor finetunen met de volgende opdracht:  
   ```bash
   docker exec -it data-gen-AAIP-ollama ollama pull bramvanroy/geitje-7b-ultra:Q4_K_M
   ```

### 4. **Genereer de Trainingsdataset**  
   Maak synthetische trainingsdata met dit script (let op: **deze stap is tijdrovend**):  
   ```bash
   python dataset_generation.py
   ```

### 5. **Maak de Trainingsdataset Schoon**  
   Nadat de data is gegenereerd, maak je de synthetische dataset schoon met:  
   ```bash
   python trained_cleaning.py
   ```

### 6. **Train het Model**  
   Finetune het model met je voorbereide dataset. Deze stap duurt ongeveer **15 minuten**:  
   ```bash
   python training.py
   ```

### 7. **Test het Model**  
   Evalueer de prestaties van het model met:  
   ```bash
   python testing.py
   ```

---

## Conclusie  
Gefeliciteerd! Je hebt je SBERT-model succesvol finetuning. 🎉  
Veel plezier met het gebruiken voor scoretaken op je data! 🚀
