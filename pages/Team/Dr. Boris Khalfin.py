import streamlit as st
import pandas as pd
from Bio import Entrez
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Publications | Dr. Boris Khalfin",
    page_icon="📚",
    layout="wide"
)

# Set NCBI Email
Entrez.email = "khalphin@bgu.ac.il"

ORCID_ID = "0000-0003-1695-6544"
AUTHOR_NAME = "Dr. Boris Khalfin"

st.title("📚 Publications")
st.write("")
st.caption(f"Researcher: **{AUTHOR_NAME}** | ORCID: [{ORCID_ID}](https://orcid.org/{ORCID_ID})")

st.divider()

@st.cache_data(ttl=86400)  # Cache publications for 24 hours
def fetch_pubmed_publications(orcid_id: str, author_query: str):
    query = f"{orcid_id}[ORCID] OR {author_query}[Author]"
    
    try:
        # Step 1: Search PMID list
        handle = Entrez.esearch(db="pubmed", term=query, retmax=100, sort="pub_date")
        record = Entrez.read(handle)
        handle.close()
        
        pmid_list = record.get("IdList", [])
        
        if not pmid_list:
            return []
        
        # Step 2: Fetch detailed XML records
        handle = Entrez.efetch(db="pubmed", id=",".join(pmid_list), rettype="xml", retmode="xml")
        xml_data = handle.read()
        handle.close()
        
        root = ET.fromstring(xml_data)
        publications = []
        
        for article in root.findall(".//PubmedArticle"):
            # Title
            title_node = article.find(".//ArticleTitle")
            title = title_node.text if title_node is not None and title_node.text else "Title unavailable"
            title = title.rstrip(".")

            # Journal
            journal_node = article.find(".//Journal/Title")
            journal = journal_node.text if journal_node is not None else "N/A"

            # Publication Year
            pub_date = article.find(".//JournalIssue/PubDate/Year")
            if pub_date is None:
                pub_date = article.find(".//JournalIssue/PubDate/MedlineDate")
            year = pub_date.text[:4] if pub_date is not None and pub_date.text else "N/A"

            # Authors
            authors = []
            for author in article.findall(".//AuthorList/Author"):
                last_name = author.find("LastName")
                fore_name = author.find("ForeName")
                initials = author.find("Initials")
                
                if last_name is not None:
                    name_str = last_name.text
                    if fore_name is not None and fore_name.text:
                        name_str = f"{last_name.text} {fore_name.text[0]}."
                    elif initials is not None and initials.text:
                        name_str = f"{last_name.text} {initials.text}"
                    
                    if "khalfin" in name_str.lower():
                        name_str = f"**{name_str}**"
                    
                    authors.append(name_str)

            # DOI & PMID
            doi = None
            pmid = None
            for article_id in article.findall(".//ArticleId"):
                id_type = article_id.get("IdType")
                if id_type == "doi":
                    doi = article_id.text
                elif id_type == "pubmed":
                    pmid = article_id.text

            # Abstract
            abstract_nodes = article.findall(".//AbstractText")
            abstract_parts = [node.text for node in abstract_nodes if node.text]
            abstract = " ".join(abstract_parts) if abstract_parts else None

            publications.append({
                "title": title,
                "journal": journal,
                "year": year,
                "authors": ", ".join(authors),
                "doi": doi,
                "pmid": pmid,
                "abstract": abstract
            })
            
        publications.sort(key=lambda x: x["year"] if x["year"].isdigit() else "0000", reverse=True)
        return publications

    except Exception as e:
        st.error(f"Error fetching data from PubMed: {e}")
        return []

# Fetch publications
with st.spinner("Fetching latest publications from PubMed..."):
    pubs = fetch_pubmed_publications(ORCID_ID, "Khalfin B")

if not pubs:
    st.warning("No publications found or unable to connect to PubMed at this moment.")
else:
    # Sidebar Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filter Publications")
    
    years = sorted(list(set(p["year"] for p in pubs if p["year"].isdigit())), reverse=True)
    selected_years = st.sidebar.multiselect("Select Year(s):", options=years, default=years)
    
    search_term = st.sidebar.text_input("Keyword Search:", "")

    filtered_pubs = [
        p for p in pubs 
        if (p["year"] in selected_years or not p["year"].isdigit()) and
        (search_term.lower() in p["title"].lower() or 
         search_term.lower() in p["authors"].lower() or 
         search_term.lower() in p["journal"].lower())
    ]

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total PubMed Articles", len(pubs))
    m2.metric("Filtered Count", len(filtered_pubs))
    latest_year = years[0] if years else "N/A"
    m3.metric("Latest Publication", latest_year)

    st.markdown("---")

    # Display Publications
    for pub in filtered_pubs:
        with st.container():
            st.markdown(f"### {pub['title']}")
            st.markdown(f"**Authors:** {pub['authors']}")
            st.markdown(f"📖 *{pub['journal']}* ({pub['year']})")
            
            link_cols = st.columns([1, 1, 4])
            with link_cols[0]:
                if pub["doi"]:
                    st.markdown(f"[🔗 DOI Link](https://doi.org/{pub['doi']})")
            with link_cols[1]:
                if pub["pmid"]:
                    st.markdown(f"[🔬 PubMed (PMID: {pub['pmid']})](https://pubmed.ncbi.nlm.nih.gov/{pub['pmid']}/)")

            if pub["abstract"]:
                with st.expander("Show Abstract"):
                    st.write(pub["abstract"])

            st.divider()
