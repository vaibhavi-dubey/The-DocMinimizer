import os
import tempfile
import matplotlib.pyplot as plt
import streamlit as st
from modules.extractor import extract_text_from_pdf
from modules.replacer import load_abbreviations, replace_with_abbreviations
from modules.abbreviator import abbreviate_pdf

# Page Config
st.set_page_config(page_title="DocMinimizer", layout="wide")
st.title("📄 DocMinimizer – PDF Abbreviation Compressor")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

# Day/Night Toggle
mode = st.toggle("🌙 Night Mode", value=False)

# Define styles
if mode:  # Night mode
    background_color = "#0e1117"
    text_color = "#fafafa"
    widget_color = "#262730"
    metric_value_color = "#ffffff"
    metric_label_color = "#cccccc"
    table_text_color = "#ffffff"
else:  # Day mode
    background_color = "#ffffff"
    text_color = "#000000"
    widget_color = "#f0f2f6"
    metric_value_color = "#000000"
    metric_label_color = "#444444"
    table_text_color = "#000000"

# Inject custom CSS with improved metric and table styling
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {background_color};
            color: {text_color};
        }}
        .stTextArea textarea {{
            background-color: {widget_color};
            color: {text_color};
        }}
        .stTextInput > div > div > input {{
            background-color: {widget_color};
            color: {text_color};
        }}
        .stDownloadButton button,
        .stButton button {{
            background-color: {widget_color};
            color: {text_color};
        }}
        
        /* Fix for metric styling */
        [data-testid="stMetric"] {{
            background-color: {widget_color};
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        [data-testid="stMetric"] > div {{
            color: {metric_value_color} !important;
        }}
        [data-testid="stMetric"] label {{
            color: {metric_label_color} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {metric_value_color} !important;
            font-weight: bold;
        }}
        [data-testid="stMetricLabel"] {{
            color: {metric_label_color} !important;
        }}
        [data-testid="stMetricDelta"] {{
            color: {metric_value_color} !important;
        }}
        
        /* Fix for table styling */
        .stTable {{
            color: {table_text_color} !important;
        }}
        .stTable th {{
            background-color: {widget_color};
            color: {text_color} !important;
            font-weight: bold;
        }}
        .stTable td {{
            color: {table_text_color} !important;
        }}
        
        /* Dataframe styling removed as we're using table instead */
        
        /* Toggle button styling */
        .stToggle {{
            background-color: {widget_color};
            border-radius: 20px;
            padding: 2px;
        }}
        
        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color} !important;
        }}
        
        /* Info box */
        .stAlert {{
            background-color: {widget_color};
            color: {text_color};
        }}
    </style>
""", unsafe_allow_html=True)

if uploaded_file:
    include_reference_pages = st.toggle("Include abbreviation reference pages", value=False)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    output_path = input_path.replace(".pdf", "_minimized.pdf")

    original_text_pages = extract_text_from_pdf(input_path)
    abbreviations = load_abbreviations("config/abbreviations.json")
    replaced_pages = replace_with_abbreviations(original_text_pages, abbreviations)

    used_abbr = abbreviate_pdf(
        input_path,
        output_path,
        abbreviations,
        return_used=True,
        include_reference_pages=include_reference_pages
    )

    original_size = os.path.getsize(input_path)
    minimized_size = os.path.getsize(output_path)
    percent_reduction = ((original_size - minimized_size) / original_size * 100) if original_size else 0

    # Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Original Text")
        st.text_area("Before", "\n\n".join(original_text_pages[:2]), height=400)

    with col2:
        st.subheader("📉 Minimized Text")
        st.text_area("After", "\n\n".join(replaced_pages[:2]), height=400)

    st.markdown("---")
    
    # Using columns for better metric display
    st.subheader("📊 Compression Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Size (KB)", f"{original_size / 1024:.2f}")
    with col2:
        st.metric("Minimized Size (KB)", f"{minimized_size / 1024:.2f}")
    with col3:
        st.metric("Reduction (%)", f"{percent_reduction:.2f}%")
    
    st.metric("Total Replacements", sum(data["count"] for data in used_abbr.values()))

    st.markdown("---")

    # 📊 Compression Effectiveness Graph
    st.subheader("📉 Compression Effectiveness Graph")
    fig, ax = plt.subplots(figsize=(5, 3))
    labels = ['Original', 'Minimized']
    sizes = [original_size / 1024, minimized_size / 1024]
    ax.bar(labels, sizes, color=['skyblue', 'lightgreen'])
    ax.set_ylabel("File Size (KB)")
    ax.set_title("Size Before and After Compression")
    # Set text color for plot based on mode
    ax.tick_params(colors=text_color)
    ax.title.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)
    st.pyplot(fig)

    # 🔢 Top Abbreviations Used
    if used_abbr:
        st.subheader("🔢 Top Abbreviations Used")
        sorted_abbr = sorted(
            used_abbr.items(),
            key=lambda item: item[1]["count"],
            reverse=True
        )[:10]
        labels = [item[0] for item in sorted_abbr]
        counts = [item[1]["count"] for item in sorted_abbr]
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(labels, counts, color='orange')
        ax2.set_xlabel("Replacement Count")
        ax2.set_title("Top 10 Abbreviations Used")
        # Set text color for plot based on mode
        ax2.tick_params(colors=text_color)
        ax2.title.set_color(text_color)
        ax2.xaxis.label.set_color(text_color)
        fig2.patch.set_facecolor(background_color)
        ax2.set_facecolor(background_color)
        ax2.invert_yaxis()
        st.pyplot(fig2)

    # ⏱️ Reading Time Estimation
    st.subheader("⏱️ Reading Time Estimation")
    words_original = sum(len(p.split()) for p in original_text_pages)
    words_minimized = sum(len(p.split()) for p in replaced_pages)
    original_time = words_original / 200  # Average: 200 wpm
    minimized_time = words_minimized / 200
    time_saved = original_time - minimized_time
    
    # Using columns for better metric display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Time (min)", f"{original_time:.2f}")
    with col2:
        st.metric("Minimized Time (min)", f"{minimized_time:.2f}")
    with col3:
        st.metric("Time Saved (min)", f"{time_saved:.2f}")

    st.markdown("---")
    st.subheader("🔤 Replaced Abbreviations")

    if used_abbr:
        # Create a custom styled dataframe
        abbr_data = [
            {
                "Full Form": full,
                "Abbreviation": data["abbr"],
                "Replacement Count": data["count"]
            }
            for full, data in used_abbr.items()
        ]
        # Use table instead of dataframe for consistent styling
        st.table(abbr_data)
    else:
        st.info("No abbreviations were used in this document.")

    with open(output_path, "rb") as f:
        st.download_button("📥 Download Minimized PDF", f, file_name="minimized_output.pdf", mime="application/pdf")