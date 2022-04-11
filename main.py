import streamlit as st
import os
import asyncio, json

from dotenv import load_dotenv
from deepgram import Deepgram


load_dotenv()

LANGUAGE = {
    "English": "en-US",
    "French": "fr",
    "Japanese": "ja",
    "Dutch": "nl",
    "Hindi": "hi",
    "Portuguese": "pt",
    "Spanish": "es"
}

transcript = ''
search = ''
clicked = None
search_clicked = None

async def analyze_audio(file, options):
    if options is None:
        options = {'punctuate': True}
    deepgram = Deepgram(os.environ["DEEPGRAM_API_KEY"])

    source = {'buffer': file, 'mimetype': 'audio/wav'}
    response = await deepgram.transcription.prerecorded(source, options)
    return response

def form_select(opt):
    return opt[1]

with st.sidebar:
    audio_file = st.file_uploader("Upload audio file/s", type=["wav"])
    language = st.selectbox("Select language of the audio", LANGUAGE.keys())
    choice = st.radio("What would you like to do", ["Search audio", "Analyze audio"])
    if choice == "Search audio":
        search = st.text_input("Enter search term")
        search_clicked = st.button("Search audio")
    elif choice == "Analyze audio":
        options = st.multiselect("Select options for analysis", [("punctuate", "punctuate"), ("profanity_filter", "Remove profanity"), ("diarize", "Is a conversation")], [("punctuate", "punctuate")], format_func=form_select)
        clicked = st.button("Analyze")


st.title("Speech to text for all")

if clicked:
    if audio_file is not None:
        analysis_options = dict(zip([opt[0] for opt in options], [True for opt in options]))
        analysis_options["language"] = LANGUAGE[language]
        print(analysis_options)
        st.header("Transcript")
        with st.spinner("Analyzing audio..."):
            results = asyncio.run(analyze_audio(audio_file, analysis_options))
            transcript = results["results"]["channels"][0]["alternatives"][0]["transcript"] 
        st.write(transcript)
        st.download_button("Download transcript", transcript)

if search_clicked:
    if audio_file is not None:
        with st.spinner("Searching audio"):
            results = asyncio.run(analyze_audio(audio_file, {"search": search, "language": LANGUAGE[language]}))
            transcript = results["results"]["channels"][0]["alternatives"][0]["transcript"]
            search_results = results["results"]["channels"][0]["search"][0]["hits"]
            found = []
            for hit in search_results:
                if hit["confidence"] > 0.9:
                    found.append(hit)
        st.header("Search Results")
        for res in found:
            st.write(f"Found {search}: {res['snippet']} at {res['start']}s to {res['end']}s")
        st.header("Transcript")
        st.write(transcript)
        st.download_button("Download transcript", transcript)


