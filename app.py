import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Amino Acid Analysis", page_icon="🧬")

st.title("🔬 Amino Acid Analysis from UniProt Code (AC)")

st.write("""
Enter a **UniProt accession code (AC)** to download the protein sequence and visualize the relative frequencies
of amino acids, as well as specific amino acid ratios (E/Q, E/P, Y/F, D/N, G/S).

Examples:
- `P69905` → Hemoglobin subunit alpha  
- `P68871` → Hemoglobin subunit beta
""")

ac = st.text_input("UniProt code (AC):", "")

if ac:
    url = f"https://rest.uniprot.org/uniprotkb/{ac}.fasta"
    response = requests.get(url)
    json_url = f"https://rest.uniprot.org/uniprotkb/{ac}.json"
    json_response = requests.get(json_url)

    if response.status_code == 200 and ">" in response.text:
        if json_response.status_code == 200:
            try:
                entry_data = json_response.json()
                entry_name = entry_data.get("uniProtkbId", "N/A")
                st.markdown(f"**Entry name:** `{entry_name}`")
            except Exception:
                entry_name = "N/A"
        else:
            entry_name = "N/A"
        lines = response.text.splitlines()
        sequence = "".join([l.strip() for l in lines if not l.startswith(">")])

        st.success(f"✅ Sequence downloaded ({len(sequence)} amino acids).")
        st.code(sequence[:80] + "..." if len(sequence) > 80 else sequence)

        # Count amino acids
        aa_counts = {}
        for aa in sequence:
            aa_counts[aa] = aa_counts.get(aa, 0) + 1

        # Calculate relative frequencies
        total = len(sequence)
        aa_freq = {aa: count / total for aa, count in aa_counts.items()}

        # Create DataFrame
        df = pd.DataFrame({
            "Amino acid": list(aa_freq.keys()),
            "Count": list(aa_counts.values()),
            "Relative frequency": list(aa_freq.values())
        }).sort_values("Amino acid")

        st.subheader(f"📊 Relative frequency of amino acids ({entry_name})")
        st.dataframe(df.set_index("Amino acid"))

        # Histogram of amino acids
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df["Amino acid"], df["Relative frequency"], color="skyblue")
        ax.set_ylabel("Relative frequency")
        ax.set_xlabel("Amino acid")
        ax.set_title(f"Amino acid distribution for {entry_name}")
        st.pyplot(fig)

        # Calculate requested ratios
        def ratio(a, b):
            return (aa_counts.get(a, 0) / aa_counts.get(b, 1)) if aa_counts.get(b, 0) != 0 else 0

        ratios = {
            "E/Q": ratio('E', 'Q'),
            "E/P": ratio('E', 'P'),
            "Y/F": ratio('Y', 'F'),
            "D/N": ratio('D', 'N'),
            "G/S": ratio('G', 'S')
        }

        ratio_df = pd.DataFrame(list(ratios.items()), columns=["Ratio", "Value"])

        st.subheader("⚖️ Specific amino acid ratios")
        st.dataframe(ratio_df.set_index("Ratio"))

        # Ratios chart
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(ratio_df["Ratio"], ratio_df["Value"], color="orange")
        ax2.set_ylabel("Ratio value")
        ax2.set_title("Amino acid ratios (E/Q, E/P, Y/F, D/N, G/S)")
        st.pyplot(fig2)

        # --- 📥 Section to download data in Excel ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Frequencies')
            ratio_df.to_excel(writer, index=False, sheet_name='Ratios')

            img_data = BytesIO()
            fig.savefig(img_data, format='png', bbox_inches='tight')
            img_data.seek(0)
            img_data2 = BytesIO()
            fig2.savefig(img_data2, format='png', bbox_inches='tight')
            img_data2.seek(0)

            workbook = writer.book
            from openpyxl.drawing.image import Image
            worksheet1 = workbook.create_sheet("Frequency_Chart")
            worksheet1.add_image(Image(img_data), "A1")
            worksheet2 = workbook.create_sheet("Ratio_Chart")
            worksheet2.add_image(Image(img_data2), "A1")

        output.seek(0)

        st.download_button(
            label="📥 Download results (Excel)",
            data=output,
            file_name=f"{ac}_aminoacid_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("❌ Invalid UniProt code or sequence not found.")

