import pandas as pd
import numpy as np
import re
import ollama

def clean_and_process_text(input_text):
    url_pattern = re.compile(r'\b(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b')
    time_pattern = re.compile(r'\b(\d{1,2}):(\d{2})\s*uur\b')
    alphanumeric_pattern = re.compile(r'[^a-zA-Z0-9\s.,!?;:()\'"-\\\/‟„”$€¥£™©]')

    def replace_url(match):
        # Extract and format the domain
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith('www.') else domain

    def replace_time(match):
        # Replace ':' with '.' for the time format
        return match.group(0).replace(':', '.')

    # Process the input text
    def process_text(text):
        # Replace URLs and modify time phrases
        text = url_pattern.sub(replace_url, text)
        text = time_pattern.sub(replace_time, text)
        # Remove non-alphanumeric characters
        return alphanumeric_pattern.sub('', text)

    # Return the processed text
    return process_text(input_text)

# Function to save DataFrame to CSV
def save_df_to_csv(df, filename='training.csv'):
    df.to_csv(filename, index=False)

# Main processing function
def main():
    df = pd.read_csv('important_sentences.csv', index_col=0)

    df.index.name = 'index'
    df.rename(columns={'sentence': 'sentence1'}, inplace=True)
    df['sentence2'] = ""  # Fill with empty strings
    df['score'] = 0.0

    n_rows = len(df)
    sample_size = n_rows // 3

    try:
        # Select random indices for each category
        indices_1_0 = np.random.choice(df.index, size=sample_size, replace=False)
        remaining_indices = df.index[~df.index.isin(indices_1_0)]
        indices_0_5 = np.random.choice(remaining_indices, size=sample_size, replace=False)
        indices_0_0 = remaining_indices[~remaining_indices.isin(indices_0_5)]

        # Process the sentences and set the scores for 1.0 scores
        for idx in indices_1_0:
            original_sentence = df.at[idx, 'sentence1']
            rewritten_response = ollama.generate(model='schrijfassistent_goed', prompt=original_sentence)
            style_response = ollama.generate(model='stijlassistent_goed', prompt=rewritten_response['response'])
            final_output = clean_and_process_text(style_response['response'])
            df.at[idx, 'sentence2'] = final_output# Save the processed output to sentence2
            df.at[idx, 'score'] = 1.0

        # Save DataFrame after processing 1.0 scores
        save_df_to_csv(df)

        # Process the sentences and set the scores for 0.5 scores
        for idx in indices_0_5:
            original_sentence = df.at[idx, 'sentence1']
            rewritten_response = ollama.generate(model='schrijfassistent_goed', prompt=original_sentence)
            style_response = ollama.generate(model='stijlassistent_goed', prompt=rewritten_response['response'])
            final_output = style_response['response']
            df.at[idx, 'sentence2'] = final_output # Save the processed output to sentence2
            df.at[idx, 'score'] = 0.5

        # Save DataFrame after processing 0.5 scores
        save_df_to_csv(df)

        # Process the sentences and set the scores for 0.0 scores
        for idx in indices_0_0:
            original_sentence = df.at[idx, 'sentence1']
            rewritten_response = ollama.generate(model='schrijfassistent_slecht', prompt=original_sentence)
            style_response = ollama.generate(model='stijlassistent_slecht', prompt=rewritten_response['response'])
            final_output = style_response['response']  # Use response as is
            df.at[idx, 'sentence2'] = final_output  # Save the processed output to sentence2
            df.at[idx, 'score'] = 0.0

        # Save final DataFrame after processing 0.0 scores
        save_df_to_csv(df)

    except Exception as e:
        # Save the DataFrame to a CSV file when an error occurs
        print(f"An error occurred: {e}")
        save_df_to_csv(df)

# Entry point of the script
if __name__ == "__main__":
    schrijfassistent_goed = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.3

    SYSTEM Bij elke zin die je ontvangt, verander je alleen de delen die niet overeenkomen met deze richtlijnen en geef je de gecorrigeerde zin terug als dit nodig is, zonder extra toelichting. Houd de lengte van de gecorrigeerde zin vergelijkbaar met de oorspronkelijke zin. Schrijf op een energieke en heldere manier. Schrijf op een enthousiaste manier zonder te overdrijven. Vermeld specifiek de datum, tijd, en kosten als deze zijn meegegeven, en gebruik toegankelijke en inclusieve taal. Houd de stijl direct en actief, en vermijd formeel of ambtelijk taalgebruik. Gebruik 'je' in informele communicatie zoals campagnes en sociale media, en 'u' in formele teksten zoals brieven en uitnodigingen.  Schrijf zonder jargon en wees je bewust van de diversiteit van lezers. Leg vaktermen uit als ze nodig zijn. Gebruik geen dialect of vreemde woorden tenzij relevant. Maak gebruik van eenvoudige en alledaagse woorden om verwarring te voorkomen. Schrijf genderneutraal en houd rekening met de inclusiviteit van personen met een beperking waar relevant. Gebruik de vorm '-aren' voor inwonersnamen zoals antwerpenaren. Schrijf getallen niet voluit voorbeeld: 10 ipv tien.
    """

    stijlassistent_goed = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.15

    SYSTEM Bij elke zin die je ontvangt, verander je alleen de delen die niet overeenkomen met deze richtlijnen en geef je de gecorrigeerde zin terug als dit nodig is, zonder extra toelichting. Schrijf urls altijd met het www. protocol. Houd de lengte van de gecorrigeerde zin vergelijkbaar met de oorspronkelijke zin. Gebruik kleine letters voor 'stad', 'stadsdeel' en 'district'. RAAK URLS NIET AAN. Schrijf afdelingen en diensten binnen de stad met hoofdletters, behalve lidwoorden en voegwoorden. Gebruik 'we' alleen bij communicatie vanuit de redactie of om verbinding te tonen. Vermijd 'we' wanneer je spreekt namens een dienst of district. Gebruik dubbele aanhalingstekens voor citaten en enkele voor titels van werken zoals voorstellingen en boeken. Vermijd woorden uit andere talen. Zet ze cursief als dat noodzakelijk is. Gebruik de 24-uursnotatie. Schrijf getallen altijd als cijfers, met een punt voor duizendtallen en 'euro' voluit. Vermeld de volledige datum in tekst met de dag van de week indien mogelijk. Bij plaatsgebrek schrijf je compact met een slash.
    """

    ollama.create(model='schrijfassistent_goed', modelfile=schrijfassistent_goed)
    ollama.create(model='stijlassistent_goed', modelfile=stijlassistent_goed)

    schrijfassistent_slecht = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 1

    SYSTEM Bij elke zin die je ontvangt, laat je alleen de delen die niet overeenkomen met deze richtlijnen intact en geef je de originele zin terug als dit niet nodig is, zonder extra uitleg. Houd de lengte van de originele zin niet noodzakelijk vergelijkbaar met de gecorrigeerde zin. Schrijf op een saaie en onduidelijke manier. Schrijf op een ongeïnspireerde manier zonder enige opwinding. Vermeld geen specifieke datum, tijd of kosten als deze zijn meegegeven, en gebruik taal die niet toegankelijk of exclusief is. Houd de stijl indirect en passief, en vermijd een directe communicatiestijl. Gebruik 'u' in informele communicatie zoals campagnes en sociale media, en 'je' in formele teksten zoals brieven en uitnodigingen. Schrijf vol jargon en negeer de diversiteit van lezers. Leg vaktermen nooit uit, ook al zijn ze nodig. Gebruik dialect en vreemde woorden, ongeacht de relevantie. Maak gebruik van complexe en ongebruikelijke woorden om verwarring te bevorderen. Schrijf niet genderneutraal en houd geen rekening met de inclusiviteit van personen met een beperking, zelfs als dat relevant is. Gebruik de vorm '-en' voor inwonersnamen. Schrijf getallen voluit, bijvoorbeeld: tien in plaats van 10."""

    stijlassistent_slecht = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 1

    SYSTEM Bij elke zin die je ontvangt, verander je alleen de delen die overeenkomen met deze richtlijnen en geef je de gecorrigeerde zin terug als dit niet nodig is, zonder extra toelichting. Houd de lengte van de gecorrigeerde zin ongelijk aan de oorspronkelijke zin. Gebruik bij websites nooit 'www' als prefix. Gebruik hoofdletters voor 'stad', 'stadsdeel' en 'district'. Schrijf afdelingen en diensten binnen de stad met kleine letters, inclusief lidwoorden en voegwoorden. Gebruik 'we' altijd bij communicatie vanuit de redactie of om verbinding te tonen. Vermijd 'we' nooit wanneer je spreekt namens een dienst of district. Gebruik enkele aanhalingstekens voor citaten en dubbele voor titels van werken zoals voorstellingen en boeken. Gebruik woorden uit andere talen zonder cursivering. Gebruik de 12-uursnotatie. Schrijf getallen altijd als woorden, met een komma voor duizendtallen en '€' als symbool. Vermeld de datum in tekst zonder de dag van de week. Bij plaatsgebrek schrijf je ruim met een spatie.
    """

    ollama.create(model='schrijfassistent_slecht', modelfile=schrijfassistent_goed)
    ollama.create(model='stijlassistent_slecht', modelfile=stijlassistent_goed)

    main()