import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("🔬 Analisi Amminoacidica da Codice UniProt (AC)")

st.write("""
Inserisci un **codice UniProt (AC)**, ad esempio:
- `P69905` → Emoglobina subunità alfa
- `P68871` → Emoglobina subunità beta
""")

ac = st.text_input("Codice UniProt (AC):", "")

if ac:
    # Scarica la sequenza da UniProt (formato FASTA)
    url = f"https://rest.uniprot.org/uniprotkb/{ac}.fasta"
    response = requests.get(url)
    
    if response.status_code == 200 and ">" in response.text:
        # Estrae la sequenza dalla risposta FASTA
        lines = response.text.splitlines()
        sequence = "".join([l.strip() for l in lines if not l.startswith(">")])
        
        st.success(f"Sequenza scaricata ({len(sequence)} amminoacidi).")
        st.code(sequence[:80] + "..." if len(sequence) > 80 else sequence)
        
        # Conta gli amminoacidi
        aa_counts = {}
        for aa in sequence:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1
        
        # Frequenza relativa
        total = len(sequence)
        aa_freq = {aa: count / total for aa, count in aa_counts.items()}
        
        # Crea un DataFrame per ordinare e visualizzare
        df = pd.DataFrame({
            "Aminoacido": list(aa_freq.keys()),
            "Frequenza_relativa": list(aa_freq.values())
        }).sort_values("Aminoacido")
        
        st.subheader("📊 Frequenza relativa degli amminoacidi")
        st.dataframe(df.set_index("Aminoacido"))
        
        # Istogramma
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df["Aminoacido"], df["Frequenza_relativa"], color="skyblue")
        ax.set_ylabel("Frequenza relativa")
        ax.set_xlabel("Aminoacido")
        ax.set_title(f"Distribuzione amminoacidica di {ac}")
        st.pyplot(fig)
        
    else:
        st.error("codice non trovato")
