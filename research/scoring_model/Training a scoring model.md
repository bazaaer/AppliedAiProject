# Fine-Tuning an SBERT Model

## Prerequisites

Before you begin, ensure you have the following:  
- **Dataset**: A web-scraped CSV dataset of *antwerpen.be* or similar data (we used ElasticSearch to extract data from Antwerp's official websites).  
- **Time**: Up to **5 days** or access to a high-performance computing setup to generate synthetic training data.  
- **Patience and Coffee**: Training may take a while, so stay caffeinated and ready!

---

## Steps to Fine-Tune the SBERT Model

### 1. **Prepare the Dataset**  
   Run the following script to clean the web-scraped dataset:  
   ```bash
   python data_cleaning.py
   ```

### 2. **Set Up the Environment**  
   Start the necessary services for your project:  
   ```bash
   docker compose up
   ```

### 3. **Download the Base Model**  
   Pull the base model for fine-tuning using the following command:  
   ```bash
   docker exec -it data-gen-AAIP-ollama ollama pull bramvanroy/geitje-7b-ultra:Q4_K_M
   ```

### 4. **Generate the Training Dataset**  
   Create synthetic training data using this script (note: **this step is time-intensive**):  
   ```bash
   python dataset_generation.py
   ```

### 5. **Clean the Training Dataset**  
   After generation, clean the synthetic dataset with:  
   ```bash
   python trained_cleaning.py
   ```

### 6. **Train the Model**  
   Fine-tune the model using your prepared dataset. This step will take approximately **15 minutes**:  
   ```bash
   python training.py
   ```

### 7. **Test the Model**  
   Finally, evaluate the model's performance with:  
   ```bash
   python testing.py
   ```

---

## Conclusion  
Congratulations! You've successfully fine-tuned your SBERT model. 🎉  
Enjoy using it for scoring tasks on your data! 🚀