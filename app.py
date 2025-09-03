import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="URL Inventory Tool", layout="wide")
st.title("🌐 URL Inventory Tool")

mode = st.radio("Choose Mode", ["Manual URLs / CSV", "Crawl Domain"])
urls = []

# Manual Mode
if mode == "Manual URLs / CSV":
    input_text = st.text_area("Paste URLs (one per line)...")
    uploaded_file = st.file_uploader("Or upload CSV/TXT file", type=["csv", "txt"])

    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        urls += [line.strip() for line in file_content.splitlines() if line.strip()]

    if input_text:
        urls += [line.strip() for line in input_text.splitlines() if line.strip()]

# Crawl Mode
elif mode == "Crawl Domain":
    domain = st.text_input("Enter domain (e.g. https://example.com)")
    if st.button("Crawl"):
        try:
            res = requests.get(domain, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = [a["href"] for a in soup.find_all("a", href=True)]
            # Normalize relative URLs
            urls = [l if l.startswith("http") else domain.rstrip("/") + "/" + l.lstrip("/") for l in links]
            st.success(f"✅ Found {len(urls)} links")
        except Exception as e:
            st.error(f"Error crawling domain: {e}")

# Status Check
results = []
if urls and st.button("Check Status"):
    with st.spinner("Checking URLs..."):
        for url in urls:
            try:
                r = requests.head(url, allow_redirects=True, timeout=5)
                results.append({"URL": url, "Status": r.status_code})
            except:
                results.append({"URL": url, "Status": "Error"})

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        # CSV Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download as CSV", csv, "url_inventory.csv", "text/csv"
        )
