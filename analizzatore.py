import streamlit as st
from groq import Groq
import json
import pandas as pd

# ==========================================
# 1. CONFIGURAZIONE SICUREZZA (SECRETS)
# ==========================================
# Su Streamlit Cloud, la chiave viene letta dalle impostazioni avanzate
if "GROQ_API_KEY" in st.secrets:
    CHIAVE_API_GROQ = st.secrets["GROQ_API_KEY"]
else:
    # Se testato in locale senza secrets, permette l'inserimento manuale
    CHIAVE_API_GROQ = st.sidebar.text_input("Inserisci Chiave Groq", type="password")

st.set_page_config(page_title="Analizzatore Tecnico Computi", layout="wide")

# Inizializzazione della memoria per la cronologia
if 'cronologia' not in st.session_state:
    st.session_state['cronologia'] = []

# ==========================================
# 2. INTERFACCIA UTENTE
# ==========================================
st.title("Classificatore Tecnico Professionale 🏗️")
st.write("Analisi basata su **Llama 3.3 70B** (Groq) - Pronto per il Cloud")

if not CHIAVE_API_GROQ:
    st.warning("⚠️ Inserisci la chiave API nella barra laterale o nei Secrets per iniziare.")
    st.stop()

client = Groq(api_key=CHIAVE_API_GROQ)

col1, col2 = st.columns(2)
with col1:
    codice_input = st.text_input("CODICE PREZZARIO", placeholder="Esempio: B.01.05.a")
with col2:
    desc_input = st.text_area("DESCRIZIONE ELEMENTO", placeholder="Incolla qui la descrizione tecnica...", height=150)

avvia = st.button("🔵 AVVIA ANALISI E SALVA", use_container_width=True)

# ==========================================
# 3. LOGICA DI ANALISI
# ==========================================
if avvia:
    if not codice_input or not desc_input:
        st.warning("⚠️ Per favore, inserisci sia il codice che la descrizione.")
    else:
        with st.spinner("L'intelligenza artificiale sta estraendo i dati..."):
            
            attributi = [
                "genere", "macrosettore", "settore", "manufatto/destinazione", "Categoria SOA", 
                "settore merceologico", "disciplina", "sistema", "unità tecnologica", "tipologia", 
                "quantità di unità di misura", "unità di misura", "materia", "finiture", "funzioni", 
                "geometrie/aspetto", "impieghi", "forniture", "dimensioni", "prestazioni", 
                "parametri fisici", "incluso escluso", "specifiche tecniche", "keywords", 
                "criteri di misurazione", "norma oggetto", "legge", "intervento", "attività", "lavorazione"
            ]

            prompt = f"""
            Analizza la voce di prezzario: {codice_input} - {desc_input}
            Estrai esattamente questi 30 campi in formato JSON: {', '.join(attributi)}

            REGOLE DI COMPILAZIONE:
            1. Scrivi 'N.D.' se l'informazione non è esplicitamente presente.
            2. NON inventare dati (dimensioni, materiali o leggi) se non sono scritti.
            3. Per 'genere' usa solo sigle tecniche (OC, OP, LV, RM, RP, RT, RU).
            4. Rispondi esclusivamente con il JSON puro.
            """

            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                
                risultato_json = json.loads(completion.choices[0].message.content)
                riga_completa = {"CODICE ORIGINALE": codice_input, **risultato_json}
                st.session_state['cronologia'].insert(0, riga_completa)
                
                st.success("✅ Analisi completata!")
                st.dataframe([risultato_json], use_container_width=True)
                
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

# ==========================================
# 4. CRONOLOGIA E DOWNLOAD
# ==========================================
if st.session_state['cronologia']:
    st.write("---")
    st.header("📜 Cronologia Ricerche")
    df_history = pd.DataFrame(st.session_state['cronologia'])
    
    csv = df_history.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 SCARICA TUTTA LA CRONOLOGIA (CSV/EXCEL)",
        data=csv,
        file_name="estrazione_computo.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    if st.button("🗑️ Svuota Cronologia"):
        st.session_state['cronologia'] = []
        st.rerun()
            
    st.dataframe(df_history, use_container_width=True)