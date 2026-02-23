import streamlit as st
from google import genai
from PIL import Image
from io import BytesIO
import base64
import requests
import random
import time

# ----------------------
# CONFIG
# ----------------------

st.set_page_config(page_title="FashionGenie Pro", layout="wide")
st.title("👗 FashionGenie Pro – AI Fashion Design Studio")

# API Keys
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HF_API_KEY = st.secrets["HF_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------
# SIDEBAR
# ----------------------

st.sidebar.header("Design Controls")

clothing_type = st.sidebar.selectbox(
    "Clothing Type",
    ["Hoodie", "Dress", "Blazer", "Streetwear Jacket", "Saree", "Cargo Pants"]
)

budget = st.sidebar.slider("Budget (₹)", 500, 10000, 2500)
sustainability_mode = st.sidebar.checkbox("🌱 Sustainability Mode")

prompt = st.text_input("Describe your dream fashion design")

# ----------------------
# GEMINI TEXT FUNCTIONS
# ----------------------

def safe_text_response(response):
    if hasattr(response, "text") and response.text:
        return response.text
    return response.candidates[0].content.parts[0].text


def enhance_prompt(user_prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Enhance this fashion design prompt professionally:\n{user_prompt}"
        )
        return safe_text_response(response)
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return user_prompt


def trend_analysis(user_prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Explain if this fashion style is trending in 2025:\n{user_prompt}"
        )
        return safe_text_response(response)
    except:
        return "Trend analysis unavailable."


def generate_moodboard_content(user_prompt):
    query = f"""
    Create a professional fashion mood board description for:
    {user_prompt}

    Provide:
    1. 5 color palette hex codes
    2. 4 fabric suggestions
    3. 6 fashion style keywords
    4. A short design concept story (5-6 lines)
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query
        )
        return safe_text_response(response)
    except:
        return "Mood board content unavailable."

# ----------------------
# HUGGINGFACE IMAGE (UPDATED ROUTER)
# ----------------------

from huggingface_hub import InferenceClient

hf_client = InferenceClient(
    model="stabilityai/stable-diffusion-xl-base-1.0",
    token=HF_API_KEY
)

def generate_image(image_prompt):
    try:
        image = hf_client.text_to_image(image_prompt)
        return image
    except Exception as e:
        st.error(f"HuggingFace Error: {e}")
        return None


def generate_moodboard_images(image_prompt):
    images = []
    for i in range(4):
        variation_prompt = f"{image_prompt}, fashion editorial photography, variation {i+1}"
        img = generate_image(variation_prompt)
        if img:
            images.append(img)
    return images

# ----------------------
# BUDGET + SUSTAINABILITY
# ----------------------

def calculate_budget_breakdown():
    fabric = int(budget * 0.4)
    stitching = int(budget * 0.3)
    branding = int(budget * 0.2)
    logistics = int(budget * 0.1)
    return fabric, stitching, branding, logistics


def sustainability_score():
    return random.randint(70, 95) if sustainability_mode else random.randint(25, 50)

# ----------------------
# MAIN
# ----------------------

if st.button("Generate Design"):

    if prompt:

        st.subheader("🧠 AI Enhanced Prompt")
        enhanced = enhance_prompt(prompt)
        st.write(enhanced)

        st.subheader("🎨 AI Generated Design")

        full_prompt = f"{enhanced}, {clothing_type}, high fashion, ultra detailed"

        image = generate_image(full_prompt)

        if image:
            st.image(image, use_container_width=True)

            st.subheader("💰 Production Cost Breakdown")
            fabric, stitching, branding, logistics = calculate_budget_breakdown()
            st.write(f"Fabric: ₹{fabric}")
            st.write(f"Stitching: ₹{stitching}")
            st.write(f"Branding: ₹{branding}")
            st.write(f"Logistics: ₹{logistics}")

            st.subheader("🌍 Sustainability Score")
            st.progress(sustainability_score())

            st.subheader("📈 Trend Analysis (2025 Insight)")
            st.write(trend_analysis(prompt))

            st.subheader("🧠 Mood Board Concept")
            st.write(generate_moodboard_content(prompt))

            st.subheader("🖼 Visual Inspiration Board")
            mood_images = generate_moodboard_images(full_prompt)

            if len(mood_images) >= 4:
                col1, col2 = st.columns(2)
                col1.image(mood_images[0], use_container_width=True)
                col1.image(mood_images[1], use_container_width=True)
                col2.image(mood_images[2], use_container_width=True)
                col2.image(mood_images[3], use_container_width=True)