"""
text_corrector.py: zápočtový program, MFF UK

autor: Natálie Zýková
Popis: Program načte český slovník a slovník častých chyb.
Uživatel zadá text, který je poté opraven na základě Levenshteinovy vzdálenosti a častých chyb.
"""

# knihovny

import random as rd
import json


# nahrání českého slovník, slovníku chyb a výchozího textu

with open("slovnik.txt", mode = "r", encoding = "utf-8") as slovnik:
    ceska_slova = []
    for slovo in slovnik:
        ciste_slovo = slovo.strip()
        ceska_slova.append(ciste_slovo)

with open("soubor_chyby.json", mode = "r", encoding="utf-8") as soubor_chyby:
    caste_chyby = json.load(soubor_chyby)

text = input("Zadej text: ")
text_list = text.split()


# Funkce

def levenshtein(slovo_1, slovo_2):
    """
    Vypočítá Levenshteinovu vzdálenost mezi dvěma slovy.

    Parametry:
        slovo_1 (str): Slovo zadané uživatelem (určuje počet řádků matice)
        slovo_2 (str): Správné slovo z českého slovníku (určuje počet sloupců matice)

    Vrací:
        int: Levenshteinova vzdálenost (počet operací nutných k převodu).
    """

    matice = [list(range(len(slovo_2) + 1))] # matice začíná prvním řádkem od 0 do délky druhého slova + 1
    for i in range(len(slovo_1)):
        radek = [i+1] # řádek začíná prvkem i
        for j in range(len(slovo_2)):
            radek.append(0) # doplní řádek nulami
        matice.append(radek) # doplní matici řádky

    for i in range(1, len(slovo_1) + 1):
        for j in range(1, len(slovo_2) + 1):
            if slovo_1[i - 1] == slovo_2[j - 1]:
                cena_nahrazeni = 0
            else:
                cena_nahrazeni = 1
            matice[i][j] = min(
                matice[i-1][j] + 1,                  # smazání
                matice[i][j-1] + 1,                  # vložení
                matice[i-1][j-1] + cena_nahrazeni    # nahrazení
            )
    vzdalenost = matice[len(slovo_1)][len(slovo_2)]
    return(vzdalenost)

def vytvor_vzdalenosti(slovo_input, seznam_slov):
    """
    Vytvoří slovník Levenshteinových vzdáleností mezi vstupním slovem 
    a všemi slovy v daném seznamu.

    Parametry:
        slovo_input (str): Slovo zadané uživatelem.
        seznam_slov (list of str): Seznam českých slov.

    Vrací:
        dict: Klíče jsou slova ze seznamu, hodnoty jejich vzdálenosti od vstupního slova.

    """
    slovnik_vzdalenosti = dict()
    for ceske_slovo in seznam_slov:
        vzdalenost = levenshtein(slovo_input, ceske_slovo)
        slovnik_vzdalenosti[ceske_slovo] = vzdalenost
    return(slovnik_vzdalenosti)

def vypis_slova_min(slovnik):
    """
    Najde slova s nejmenší Levenshteinovou vzdáleností.

    Parametry:
        slovnik (dict): Slovník slov a jejich vzdáleností.

    Vrací:
        list of str: Slova s nejmenší vzdáleností.

    """
    min_vzdalenost = min(slovnik.values())
    slova_min = []
    for ceske_slovo, vzdalenost in slovnik.items():
        if vzdalenost == min_vzdalenost:
            slova_min.append(ceske_slovo)
    return(slova_min)

def vyber_nejlepsi_slovo(slovo_input, zuzeny_seznam_slov):
    """
    Ze seznamu slov s nejmenší LV vybere jediné, nejlepší možné slovo pro opravu chybného.
    Postupně zužuje výběr podle délky slov a dle srovnání s častými chybami.
    
    Parametry:
        slovo_input (str): Slovo zadané uživatelem.
        zuzeny_seznam_slov (list of str): Slova s nejmenší LV

    Vrací:
        str: Opravený (nebo potvrzený) text, který se uživateli zobrazí.

    """
    kandidati = []
    nekandidati = []
    for ceske_slovo in zuzeny_seznam_slov:
        if len(ceske_slovo) == len(slovo_input):
            kandidati.append(ceske_slovo)
        else:
            nekandidati.append(ceske_slovo)
    
    if len(kandidati) == 0:
        nej_slovo = rd.choice(nekandidati)
    else:
        zaznamy = [] # seznam slovníků, #slovníků = #chyb pro všechny kandidáty dohromady
        for ceske_slovo in kandidati:
            for i in range(len(slovo_input)):
                if ceske_slovo[i] == slovo_input[i]:
                    pass
                else:
                    zaznam = {
                        "chyba" : slovo_input[i],
                        "oprava" : ceske_slovo[i],
                        "spravne_slovo" : ceske_slovo
                    }
                    zaznamy.append(zaznam)

        lepsi_slova = []
        horsi_slova = []
        for slovnik in zaznamy:
            nalezena_chyba = slovnik["chyba"]
            oprava_chyby =  slovnik["oprava"]
            if nalezena_chyba in caste_chyby.keys():
                if oprava_chyby in caste_chyby[nalezena_chyba]:
                    lepsi_slova.append(slovnik["spravne_slovo"])
                else:
                    horsi_slova.append(slovnik["spravne_slovo"])
            else:
                horsi_slova.append(slovnik["spravne_slovo"])
        if len(lepsi_slova) == 0:
            if len(horsi_slova) == 0:
                opravene_slovo = slovo_input
            else:
                opravene_slovo = rd.choice(horsi_slova)
        else:
            opravene_slovo = rd.choice(lepsi_slova)

    return(opravene_slovo)


# Volání

vysledky = []
for zadane_slovo in text_list:
    slovnik_vzdalenosti = vytvor_vzdalenosti(zadane_slovo, ceska_slova)
    slova_min = vypis_slova_min(slovnik_vzdalenosti)
    opravene_slovo = vyber_nejlepsi_slovo(zadane_slovo, slova_min)
    vysledky.append((opravene_slovo, slova_min))

seznam_oprav = []
for opravene_slovo, _ in vysledky:
    seznam_oprav.append(opravene_slovo)
vsechna_opravena_slova = ' '.join(seznam_oprav)
print(f"Opravený text: {vsechna_opravena_slova}")

for zadane_slovo, (opravene_slovo, slova_min) in zip(text_list, vysledky):
    if zadane_slovo == opravene_slovo:
        print(f"Slovo '{zadane_slovo}' je správně.")
    else:
        print(f"Možnosti pro '{zadane_slovo}': {slova_min}")


# TODO
# lepší slovník
# názvy proměnných