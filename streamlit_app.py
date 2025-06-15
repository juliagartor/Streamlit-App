import streamlit as st
import random
import pandas as pd
from pathlib import Path
import requests
from PIL import Image, ImageEnhance

# App configuration
st.set_page_config(page_title="Image Authenticity Test", layout="wide")

# Initialize session state for tracking progress and results
if 'current_round' not in st.session_state:
    st.session_state.current_round = -1  # -1 for example phase, 0-9 for test rounds
    st.session_state.results = []
    st.session_state.method1_choices = 0  # For simulated method
    st.session_state.method2_choices = 0  # For SDXL method
    st.session_state.example_shown = False

# Predefined pairs of simulated images (SDXL vs simulated)
IMAGE_PAIRS = [
    ('data/sdXL/sdxl_8.png', 'data/simulated/SS000020.png'),
    ('data/sdXL/sdxl_10.png', 'data/simulated/SS000370.png'),
    ('data/sdXL/sdxl_5.png', 'data/simulated/SS000434.png'),
    ('data/sdXL/sdxl_1.png', 'data/simulated/SS000268.png'),
    ('data/sdXL/sdxl_7.png', 'data/simulated/SS000430.png'),
    ('data/sdXL/sdxl_3.png', 'data/simulated/SS000254.png'),
    ('data/sdXL/sdxl_9.png', 'data/simulated/SS000259.png'),
    ('data/sdXL/sdxl_2.png', 'data/simulated/SS000126.png'),
    ('data/sdXL/sdxl_4.png', 'data/simulated/SS000274.png'),
    ('data/sdXL/sdxl_6.png', 'data/simulated/SS000300.png')
]

def setup_image_data():
    comparisons = []
    for left_path, right_path in IMAGE_PAIRS:
        # Randomize which method is on which side
        if random.random() > 0.5:
            left_img, right_img = Path(left_path), Path(right_path)
            left_method = "Stable Diffusion XL"
            right_method = "Simulated"
        else:
            left_img, right_img = Path(right_path), Path(left_path)
            left_method = "Simulated"
            right_method = "Stable Diffusion XL"
            
        comparisons.append({
            "left": left_img,
            "right": right_img,
            "left_method": left_method,
            "right_method": right_method
        })
    return comparisons

def darken_image(image_path, factor=0.5):
    """Factor 1.0 returns original image, lower values darken it"""
    img = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(img)
    darkened_img = enhancer.enhance(factor)
    return darkened_img

# Load or create the comparisons
if 'comparisons' not in st.session_state:
    st.session_state.comparisons = setup_image_data()
    if not st.session_state.comparisons:
        st.error("No images found. Please check your image directories.")
        st.stop()

# Show example real images first (to maintain the illusion)
if st.session_state.current_round == -1:
    st.title("Package Code Close-ups")
    st.markdown("""
    ### First, let's look at some examples of real package codes:
    These are close-up images of laser printed codes on real packages.
    """)
    
    real_imgs_paths = [
        "data/real/image191.png",
        "data/real/image1328.png",
        "data/real/image712.png",
    ]
    # Display 3 example real images
    real_images = [Path(img_path) for img_path in real_imgs_paths if Path(img_path).exists()]
    if real_images:
        cols = st.columns(3)
        for i, img_path in enumerate(real_images):
            with cols[i]:
                st.image(Image.open(img_path), caption=f"Real package code example {i+1}")
    
    st.markdown("""
    ### Next, you'll see pairs of images - one real and one synthetic.
    Your task is to identify which one is the real photograph.
    """)
    
    if st.button("Start the Test"):
        st.session_state.current_round = 0
        st.session_state.example_shown = True
        st.rerun()

# Display test comparisons
elif 0 <= st.session_state.current_round < len(st.session_state.comparisons):
    st.title("Which image is real?")
    st.markdown(f"**Round {st.session_state.current_round + 1} of {len(st.session_state.comparisons)}**")
    
    current = st.session_state.comparisons[st.session_state.current_round]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Darken only if it's Stable Diffusion XL
        if current["left_method"] == "Stable Diffusion XL":
            img = darken_image(current["left"], factor=0.6)  # 0.7 makes it 30% darker
        else:
            img = Image.open(current["left"])
        st.image(img, use_container_width=True, caption="Image A")
        if st.button("Choose A", key="left"):
            # Track which method was chosen
            if current["left_method"] == "Stable Diffusion XL":
                st.session_state.method2_choices += 1
            else:
                st.session_state.method1_choices += 1
                
            st.session_state.results.append({
                "round": st.session_state.current_round + 1,
                "choice": "left",
                "method": current["left_method"]
            })
            st.session_state.current_round += 1
            st.rerun()
    
    with col2:
        # Darken only if it's Stable Diffusion XL
        if current["right_method"] == "Stable Diffusion XL":
            img = darken_image(current["right"], factor=0.6)  # 0.7 makes it 30% darker
        else:
            img = Image.open(current["right"])
        st.image(img, use_container_width=True, caption="Image B")
        if st.button("Choose B", key="right"):
            # Track which method was chosen
            if current["right_method"] == "Stable Diffusion XL":
                st.session_state.method2_choices += 1
            else:
                st.session_state.method1_choices += 1
                
            st.session_state.results.append({
                "round": st.session_state.current_round + 1,
                "choice": "right",
                "method": current["right_method"]
            })
            st.session_state.current_round += 1
            st.rerun()

# Show final results
else:
    st.balloons()
    st.success("Test completed! Thank you for participating.")
    
    # The big reveal
    st.subheader("Surprise!")
    st.markdown("""
    **All the images you saw in the test were actually synthetic!**  
    There were no real photographs in the comparison rounds.
    
    We showed you two different types of synthetic images:
    - **Simulated**: Pixel manipulation method
    - **Stable Diffusion XL**: AI-generated images
    
    Your choices help us understand which method appears more realistic to human observers.
    """)
    
    total_rounds = len(st.session_state.comparisons)
    
    st.subheader("Your Preferences")
    st.write(f"You chose 'Simulated' images {st.session_state.method1_choices} times")
    st.write(f"You chose 'Stable Diffusion XL' images {st.session_state.method2_choices} times")
    
    preferred_method = "Simulated" if st.session_state.method1_choices > st.session_state.method2_choices else "Stable Diffusion XL"
    if st.session_state.method1_choices == st.session_state.method2_choices:
        preferred_method = "Neither - you were equally split!"
    
    st.success(f"Your preferred method was: **{preferred_method}**")

    # Only submit results if they haven't been submitted yet
    if 'results_submitted' not in st.session_state:
        # Prepare data for Google Forms submission
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeKjq4wiLCKbe_nVjGLuzEQ_0btWe6eeIOZzKJiUOLuaheKcA/formResponse"
        form_data = {
            "entry.1319823618": str(max(st.session_state.method1_choices, st.session_state.method2_choices)),
            "entry.1994929153": str(total_rounds),
            "entry.1844798411": preferred_method,
            "entry.1614317066": str(st.session_state.method1_choices),
            "entry.238554702": str(st.session_state.method2_choices),
        }
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": form_url.replace("/formResponse", "/viewform")
            }
            response = requests.post(form_url, data=form_data, headers=headers)
            if response.status_code == 200:
                st.session_state.results_submitted = True
                st.toast("Results successfully submitted!", icon="✅")
            else:
                st.warning("Results couldn't be submitted automatically. Please take a screenshot of your results.")
        except Exception as e:
            st.warning(f"Error submitting results: {e}. Please take a screenshot of your results.")

    if st.checkbox("Show detailed results"):
        st.table(pd.DataFrame(st.session_state.results))