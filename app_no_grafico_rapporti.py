import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Analisi Amminoacidica", page_icon="🤞")

st.title("🔬 Analisi Amminoacidica da Codice UniProt (AC)")

st.write("""
Inserisci un **codice UniProt (AC)** per scaricare la sequenza e visualizzare le frequenze relative degli amminoacidi,
oltre ai rapporti specifici richiesti (E/Q, E/P, Y/F, D/N, G/S).

Esempi:
- `P69905` → Emoglobina subunità alfa  
- `P68871` → Emoglobina subunità beta
""")

ac = st.text_input("Codice UniProt (AC):", "")

if ac:
    url = f"https://rest.uniprot.org/uniprotkb/{ac}.fasta"
    response = requests.get(url)

    if response.status_code == 200 and ">" in response.text:
        lines = response.text.splitlines()
        sequence = "".join([l.strip() for l in lines if not l.startswith(">")])

        st.success(f"✅ Sequenza scaricata ({len(sequence)} amminoacidi).")
        st.code(sequence[:80] + "..." if len(sequence) > 80 else sequence)

        aa_counts = {}
        for aa in sequence:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1

        total = len(sequence)
        aa_freq = {aa: count / total for aa, count in aa_counts.items()}

        df = pd.DataFrame({
            "Aminoacido": list(aa_freq.keys()),
            "Conteggio": list(aa_counts.values()),
            "Frequenza_relativa": list(aa_freq.values())
        }).sort_values("Aminoacido")

        st.subheader("📊 Frequenza relativa degli amminoacidi")
        st.dataframe(df.set_index("Aminoacido"))

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df["Aminoacido"], df["Frequenza_relativa"], color="skyblue")
        ax.set_ylabel("Frequenza relativa")
        ax.set_xlabel("Aminoacido")
        ax.set_title(f"Distribuzione amminoacidica di {ac}")
        st.pyplot(fig)

        # Calcolo dei rapporti richiesti
        def ratio(a, b):
            return (aa_counts.get(a, 0) / aa_counts.get(b, 1)) if aa_counts.get(b, 0) != 0 else 0

        ratios = {
            "E/Q": ratio('E', 'Q'),
            "E/P": ratio('E', 'P'),
            "Y/F": ratio('Y', 'F'),
            "D/N": ratio('D', 'N'),
            "G/S": ratio('G', 'S')
        }

        ratio_df = pd.DataFrame(list(ratios.items()), columns=["Rapporto", "Valore"])

        st.subheader("⚖️ Rapporti amminoacidici specifici")
        st.dataframe(ratio_df.set_index("Rapporto"))

        # --- 📥 Sezione per scaricare i dati in Excel ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Frequenze')
            ratio_df.to_excel(writer, index=False, sheet_name='Rapporti')

            img_data = BytesIO()
            fig.savefig(img_data, format='png', bbox_inches='tight')
            img_data.seek(0)

            workbook = writer.book
            worksheet = workbook.create_sheet("Grafico")
            from openpyxl.drawing.image import Image
            worksheet.add_image(Image(img_data), "A1")

        output.seek(0)

        st.download_button(
            label="📥 Scarica risultati (Excel)",
            data=output,
            file_name=f"{ac}_analisi_amminoacidica.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("❌ Codice UniProt non valido o sequenza non trovata.")

