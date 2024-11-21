import streamlit as st
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
import re

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get summary from Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error("Error generating summary. Please try again later.")
        return ""

# Function to extract transcript details
@st.cache_data
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[-1].split("&")[0]
        transcript_text = ""
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        for i in transcript:
            transcript_text += " " + i["text"]
        return transcript_text
    except Exception as e:
        return str(e)

# Streamlit App
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")

# App Title
st.title("🎥 YouTube Video Summarizer")
st.write("Generate detailed notes from YouTube videos.")

# Input YouTube Link
youtube_link = st.text_input("Enter YouTube video link:")

if youtube_link:
    # Validate YouTube URL
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+"
    if re.match(youtube_regex, youtube_link):
        video_id = youtube_link.split("v=")[-1].split("&")[0]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    else:
        st.error("Invalid YouTube URL. Please provide a valid link.")

# Summary customization options
summary_length = st.slider("Select summary word count:", 100, 300, 200)
prompt = f"""
You are a YouTube video summarizer. Take the transcript text and summarize the video 
into bullet points within {summary_length} words. 
"""

if st.button("Get Detailed Notes"):
    with st.spinner("Fetching transcript and generating summary..."):
        transcript_text = extract_transcript_details(youtube_link)
        
        if "NoTranscriptFound" in transcript_text or "Could not retrieve" in transcript_text:
            st.error("Transcript unavailable. Ensure the video is not private or lacks captions.")
        elif transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            if summary:
                st.markdown("## 📜 Detailed Notes:")
                st.markdown(summary, unsafe_allow_html=True)
        else:
            st.error("Error fetching the transcript. Please try another video.")
