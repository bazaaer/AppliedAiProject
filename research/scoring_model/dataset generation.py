import re
import traceback

import ollama
import pandas as pd


def clean_and_process_text(input_text):
    url_pattern = re.compile(
        r"\b(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))\b"
    )
    time_pattern = re.compile(r"\b(\d{1,2}):(\d{2})\s*uur\b")
    alphanumeric_pattern = re.compile(
        r"""[^\w\s&@.,!?:;()\[\]'\"\u00C0-\u00FF\u0100-\u017F\u20A0-\u20CF\u20B9]"""
    )

    def replace_url(match):
        domain = match.group(1)
        return f"www.{domain}" if not match.group(0).startswith("www.") else domain

    def replace_time(match):
        return match.group(0).replace(":", ".")

    def process_text(text):
        text = url_pattern.sub(replace_url, text)
        text = time_pattern.sub(replace_time, text)
        return alphanumeric_pattern.sub("", text)

    return process_text(input_text)


def save_df_to_csv(df, filename="training.csv"):
    df.to_csv(filename, index=False)


def main():
    df = pd.read_csv("important_sentences.csv", index_col=0)
    df.index.name = "index"
    df.rename(columns={"sentence": "sentence1"}, inplace=True)
    df = df.sample(n=len(df) // 2, random_state=42)

    processed_data = []
    counter = (
        0  # Initialize a counter to keep track of the number of processed sentences
    )

    try:
        for idx, row in df.iterrows():
            original_sentence = row["sentence1"]

            # Good version
            rewritten_response_good = ollama.generate(
                model="schrijfassistent_goed", prompt=original_sentence
            )
            style_response_good = ollama.generate(
                model="stijlassistent_goed", prompt=rewritten_response_good["response"]
            )
            final_output_good = clean_and_process_text(style_response_good["response"])

            processed_data.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": final_output_good,
                    "score": 1.0,
                }
            )

            # Half version (loosely follows instructions without regex cleaning)
            rewritten_response_half = ollama.generate(
                model="schrijfassistent_half", prompt=original_sentence
            )
            style_response_half = ollama.generate(
                model="stijlassistent_half", prompt=rewritten_response_half["response"]
            )
            final_output_half = style_response_half[
                "response"
            ]  # No regex cleaning for half version

            processed_data.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": final_output_half,
                    "score": 0.5,
                }
            )

            # Bad version
            rewritten_response_bad = ollama.generate(
                model="schrijfassistent_slecht", prompt=original_sentence
            )
            style_response_bad = ollama.generate(
                model="stijlassistent_slecht", prompt=rewritten_response_bad["response"]
            )
            final_output_bad = style_response_bad["response"]

            processed_data.append(
                {
                    "sentence1": original_sentence,
                    "sentence2": final_output_bad,
                    "score": 0.0,
                }
            )

            # Increment counter and print update every 300 entries
            counter += 1
            if counter % 100 == 0:
                print(f"Processed {counter} entries so far...")

        processed_df = pd.DataFrame(processed_data)
        save_df_to_csv(processed_df)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()  # This prints the full traceback, which is helpful for debugging
        if "processed_df" in locals():
            processed_df = pd.DataFrame(processed_data)
            save_df_to_csv(processed_df)


# Entry point of the script
if __name__ == "__main__":
    schrijfassistent_goed = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.45

    SYSTEM Bij elke zin die je ontvangt, verander je alleen de delen die niet overeenkomen met deze richtlijnen en geef je de gecorrigeerde zin terug als dit nodig is, zonder extra toelichting. Houd de lengte van de gecorrigeerde zin vergelijkbaar met de oorspronkelijke zin. Schrijf op een energieke en heldere manier. Schrijf op een enthousiaste manier zonder te overdrijven. Vermeld specifiek de datum, tijd, en kosten als deze zijn meegegeven, en gebruik toegankelijke en inclusieve taal. Houd de stijl direct en actief, en vermijd formeel of ambtelijk taalgebruik. Gebruik 'je' in informele communicatie zoals campagnes en sociale media, en 'u' in formele teksten zoals brieven en uitnodigingen.  Schrijf zonder jargon en wees je bewust van de diversiteit van lezers. Leg vaktermen uit als ze nodig zijn. Gebruik geen dialect of vreemde woorden tenzij relevant. Maak gebruik van eenvoudige en alledaagse woorden om verwarring te voorkomen. Schrijf genderneutraal en houd rekening met de inclusiviteit van personen met een beperking waar relevant. Gebruik de vorm '-aren' voor inwonersnamen. Schrijf getallen niet voluit voorbeeld: 10 ipv tien.
    """

    stijlassistent_goed = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.25

    SYSTEM Bij elke zin die je ontvangt, verander je alleen de delen die niet overeenkomen met deze richtlijnen en geef je de gecorrigeerde zin terug als dit nodig is, zonder extra toelichting. Houd de lengte van de gecorrigeerde zin vergelijkbaar met de oorspronkelijke zin. Gebruik kleine letters voor 'stad', 'stadsdeel' en 'district'. Schrijf afdelingen en diensten binnen de stad met hoofdletters, behalve lidwoorden en voegwoorden. Gebruik 'we' alleen bij communicatie vanuit de redactie of om verbinding te tonen. Vermijd 'we' wanneer je spreekt namens een dienst of district. Gebruik dubbele aanhalingstekens voor citaten en enkele voor titels van werken zoals voorstellingen en boeken. Vermijd woorden uit andere talen. Zet ze cursief als dat noodzakelijk is. Gebruik de 24-uursnotatie. Schrijf getallen altijd als cijfers, met een punt voor duizendtallen en 'euro' voluit. Vermeld de volledige datum in tekst met de dag van de week indien mogelijk. Bij plaatsgebrek schrijf je compact met een slash.
    """

    schrijfassistent_half = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 1

    SYSTEM Bij elke zin die je ontvangt, pas je alleen de delen aan die mogelijk verbeterd kunnen worden op basis van deze richtlijnen. Geef de gecorrigeerde zin terug in een toon die overwegend helder en direct is, met ruimte voor enige complexiteit als de context dat toelaat. Vermeld datum, tijd en kosten alleen als dit relevant is voor de lezers en gebruik inclusieve taal waar passend. Kies tussen ‘je’ en ‘u’ afhankelijk van het kanaal: ‘je’ voor informele contexten zoals campagnes en sociale media, en ‘u’ voor formelere communicatie zoals uitnodigingen en brieven. Zorg ervoor dat de stijl overwegend eenvoudig blijft, maar jargon en vaktermen kunnen incidenteel gebruikt worden zonder uitleg als ze gangbaar zijn binnen de doelgroep. Schrijf zoveel mogelijk genderneutraal, en houd waar relevant rekening met de toegankelijkheid van de tekst voor een breed publiek. Schrijf getallen bij voorkeur niet voluit, tenzij de context een alternatieve weergave nodig maakt (bijv. tien i.p.v. 10).
    """

    stijlassistent_half = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 1

    SYSTEM Bij elke ontvangen zin corrigeer je alleen de delen die niet voldoen aan de richtlijnen. Houd de lengte van de gecorrigeerde zin vergelijkbaar met de oorspronkelijke zin. Gebruik kleine letters voor 'stad', 'stadsdeel' en 'district'. Schrijf afdelingen en diensten binnen de stad met hoofdletters, maar zonder hoofdletters voor lidwoorden en voegwoorden. Gebruik 'we' enkel bij communicatie vanuit de redactie of om verbinding te tonen, en vermijd 'we' wanneer er namens een dienst of district gesproken wordt. Gebruik dubbele aanhalingstekens voor citaten en enkele voor titels van werken, zoals voorstellingen en boeken. Schrijf woorden uit andere talen cursief indien noodzakelijk. Hanteer de 24-uursnotatie. Schrijf getallen altijd als cijfers, met een punt voor duizendtallen en gebruik 'euro' voluit. Vermeld de volledige datum met de dag van de week indien mogelijk. Bij ruimtegebrek schrijf je compact met een slash.
    """

    schrijfassistent_slecht = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.75

    SYSTEM Je past elke zin die je ontvangt volledig aan, en behoudt niet de oorspronkelijke bedoeling. Houd het aantal woorden altijd verschillend van de oorspronkelijke zin. Schrijf op een chaotische, indirecte en ingewikkelde manier, en wees vooral mat en onverschillig in je toon. Laat de datum, tijd en kosten altijd weg als deze worden meegegeven en gebruik obscure en onduidelijke taal. Gebruik ‘u’ in sociale media en campagnes en ‘je’ in officiële documenten en uitnodigingen. Jargon mag zonder uitleg worden ingezet, en vaktermen hoeven niet verduidelijkt te worden. Gebruik ingewikkelde woorden en overweeg dialect en vreemde woorden zonder onderscheid. Negeer de inclusiviteit van personen met een beperking volledig, ook waar dat wel relevant zou kunnen zijn. Vermijd het gebruik van '-aren' voor inwonersnamen en schrijf getallen volledig uit.
    """
    stijlassistent_slecht = """
    FROM bramvanroy/geitje-7b-ultra:Q4_K_M

    PARAMETER temperature 0.75

    SYSTEM Pas elke ontvangen zin aan. Houd het aantal woorden altijd verschillend van de oorspronkelijke zin. Voeg "www" als prefix toe aan websites. Vermijd hoofdletters bij woorden zoals "stad", "stadsdeel" en "district". Schrijf alle afdelingen en diensten binnen de stad met hoofdletters, inclusief lidwoorden en voegwoorden. Gebruik "we" nooit in communicatie vanuit de redactie en spreek in derde persoon voor meer afstand. Gebruik dubbele aanhalingstekens voor citaten. Schrijf woorden uit andere talen alleen met cursivering. Gebruik de 24-uursnotatie. Schrijf getallen als cijfers zonder komma's voor duizendtallen en gebruik "euro" voluit als symbool. Noem altijd de dag van de week bij data en maak de tekst compacter zonder extra spaties bij plaatsgebrek.
    """

    ollama.create(model="schrijfassistent_goed", modelfile=schrijfassistent_goed)
    ollama.create(model="stijlassistent_goed", modelfile=stijlassistent_goed)

    ollama.create(model="schrijfassistent_half", modelfile=schrijfassistent_half)
    ollama.create(model="stijlassistent_half", modelfile=stijlassistent_half)

    ollama.create(model="schrijfassistent_slecht", modelfile=schrijfassistent_slecht)
    ollama.create(model="stijlassistent_slecht", modelfile=stijlassistent_slecht)

    main()
