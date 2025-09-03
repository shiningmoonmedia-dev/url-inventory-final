import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="URL Inventory Tool", layout="wide")
st.title("🌐 URL Inventory Tool")

# Initialize session state
if "urls" not in st.session_state:
    st.session_state.urls = []
if "results" not in st.session_state:
    st.session_state.results = []

mode = st.radio("Choose Mode", ["Manual URLs / CSV", "Crawl Domain"])

# --- Manual Mode ---
if mode == "Manual URLs / CSV":
    input_text = st.text_area("Paste URLs (one per line)...")
    uploaded_file = st.file_uploader("Or upload CSV/TXT file", type=["csv", "txt"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.session_state.urls = [line.strip() for line in file_content.splitlines() if line.strip()]

    if input_text:
        st.session_state.urls = [line.strip() for line in input_text.splitlines() if line.strip()]

# --- Crawl Mode ---
elif mode == "Crawl Domain":
    domain = st.text_input("Enter domain (e.g. https://example.com)")
    if st.button("Crawl Domain"):
        try:
            res = requests.get(domain, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = [a["href"] for a in soup.find_all("a", href=True)]
            st.session_state.urls = [l if l.startswith("http") else domain.rstrip("/") + "/" + l.lstrip("/") for l in links]
            st.success(f"✅ Found {len(st.session_state.urls)} links")
        except Exception as e:
            st.error(f"Error crawling domain: {e}")

# --- Check Status ---
if st.session_state.urls and st.button("Check Status"):
    st.session_state.results = []
    with st.spinner("Checking URLs..."):
        for url in st.session_state.urls:
            try:
                r = requests.head(url, allow_redirects=True, timeout=5)
                st.session_state.results.append({"URL": url, "Status": r.status_code})
            except:
                st.session_state.results.append({"URL": url, "Status": "Error"})

# --- Show Results Table ---
if st.session_state.urls:
    if st.session_state.results:  # if status check done
        df = pd.DataFrame(st.session_state.results)
    else:  # just show crawled/entered URLs
        df = pd.DataFrame({"URL": st.session_state.urls})

    # Improved styled table
    def style_status(val):
        if val == 200:
            color = "green"
        elif val == "Error":
            color = "red"
        else:
            color = "orange"
        return f"color: {color}; font-weight: bold;"

    if "Status" in df.columns:
        st.dataframe(df.style.applymap(style_status, subset=["Status"]), use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download as CSV",
        csv,
        "url_inventory.csv",
        "text/csv"
    )
