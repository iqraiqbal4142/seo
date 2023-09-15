import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import requests
from bs4 import BeautifulSoup

# Initialize NLTK's VADER sentiment analyzer
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# Streamlit Configuration
st.title("SEO Content Analyzer")
st.markdown("This app analyzes your text for SEO optimization based on a primary keyword. "
            "You can analyze text or check a web URL.")
st.sidebar.title("Navigation")
selected_option = st.sidebar.radio("Choose Analysis Option:", ["Analyze Text", "Analyze Web URL"])

# Function to check SEO optimization for a primary keyword
def check_seo_optimization(text, keyword):
    report = []

    # 1. Check if the primary keyword appears in the content.
    keyword_count = text.lower().count(keyword.lower())
    report.append(f"1. Keyword '{keyword}' appears {keyword_count} times.")

    # 2. Calculate keyword density for the primary keyword.
    words = re.findall(r'\w+', text.lower())
    word_count = len(words)
    keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
    report.append(f"2. Keyword Density for '{keyword}': {keyword_density:.2f}% (Optimal: 1-2%).")

    # 3. Check for high-quality, informative content.
    sentiment_score = analyze_sentiment(text)
    sentiment_result = 'Positive' if sentiment_score >= 0.05 else 'Negative' if sentiment_score <= -0.05 else 'Neutral'
    report.append(f"3. Sentiment Analysis Result: {sentiment_result}")

    # 4. Check for proper headings (H1, H2, H3).
    headings = re.findall(r'<h[1-3]>', text.lower())
    heading_result = "Proper headings (H1, H2, H3) are used." if headings else "Proper headings (H1, H2, H3) are not used."
    report.append(f"4. {heading_result}")

    # 5. Check for meta titles and descriptions.
    meta_title = re.search(r'<title>(.*?)<\/title>', text, re.DOTALL | re.IGNORECASE)
    meta_description = re.search(r'<meta name="description" content="(.*?)"', text, re.DOTALL | re.IGNORECASE)

    meta_title_result = "Meta title is defined." if meta_title else "Meta title is missing."
    meta_description_result = "Meta description is defined." if meta_description else "Meta description is missing."

    report.append(f"5. {meta_title_result}\n   {meta_description_result}")

    return report

# Sentiment analysis function using VADER
def analyze_sentiment(text):
    sentiment_score = sia.polarity_scores(text)
    compound_score = sentiment_score["compound"]
    return compound_score

# Function to classify the type of web page (Informational, Transactional, Navigational, Commercial)
def classify_web_page(text):
    # Define keywords for different types of web pages
    informational_keywords = ["what is", "how to", "guide", "tutorial"]
    transactional_keywords = ["buy", "purchase", "order", "subscribe"]
    navigational_keywords = ["home", "about", "contact", "login"]
    commercial_keywords = ["product", "service", "pricing", "offer"]

    # Initialize counters for each type
    informational_count = 0
    transactional_count = 0
    navigational_count = 0
    commercial_count = 0

    # Check the presence of keywords
    for keyword in informational_keywords:
        if keyword in text.lower():
            informational_count += 1

    for keyword in transactional_keywords:
        if keyword in text.lower():
            transactional_count += 1

    for keyword in navigational_keywords:
        if keyword in text.lower():
            navigational_count += 1

    for keyword in commercial_keywords:
        if keyword in text.lower():
            commercial_count += 1

    # Determine the type of web page based on the counts
    max_count = max(informational_count, transactional_count, navigational_count, commercial_count)

    if max_count == informational_count:
        return "Informational"
    elif max_count == transactional_count:
        return "Transactional"
    elif max_count == navigational_count:
        return "Navigational"
    elif max_count == commercial_count:
        return "Commercial"
    else:
        return "Unclassified"

# Function to check SEO optimization for a web URL
def check_seo_url(url, keyword):
    try:
        response = requests.get(url)
        response.raise_for_status()
        web_content = response.text

        # Extract text from web content (you may need more advanced web scraping)
        soup = BeautifulSoup(web_content, "html.parser")
        web_text = soup.get_text()

        # Initialize an empty list for the SEO report
        seo_report = []

        # Check SEO optimization for the primary keyword
        seo_report += check_seo_optimization(web_text, keyword)

        # Classify the web page
        page_classification = classify_web_page(web_text)
        seo_report.append(f"Page Classification: {page_classification}")

        return seo_report

    except Exception as e:
        return [f"Error: {str(e)}"]

# Function to analyze web content from a given URL
def analyze_web_url():
    # Input web URL
    web_url = st.text_input("Enter the web URL for SEO analysis:")

    if web_url:
        # Input primary keyword for SEO analysis
        primary_keyword_url = st.text_input("Enter the primary keyword for SEO analysis (Web URL content):")

        # Analyze web URL content when the user submits
        if st.button("Analyze Web URL"):
            try:
                # Check SEO optimization for the primary keyword in web URL content
                seo_report_url = check_seo_url(web_url, primary_keyword_url)

                # Convert the list into a single string
                seo_report_url_string = "\n".join(seo_report_url)

                # Display SEO report for web URL content
                st.subheader("SEO Optimization Report (Web URL content):")
                for item in seo_report_url:
                    st.write(item)

                # SEO Suggestions
                st.subheader("SEO Suggestions:")
                # Suggestion 1: Add keyword to title
                if not re.search(f'<title>.*{primary_keyword_url}.*<\/title>', seo_report_url_string):
                    st.write("1. Consider adding the primary keyword to the document title.")
                # Suggestion 2: Add keyword to meta description
                if not re.search(f'<meta name="description" content=".*{primary_keyword_url}.*"', seo_report_url_string):
                    st.write("2. Consider adding the primary keyword to the meta description.")
                # Suggestion 3: Use keyword within 100 words
                word_count = len(re.findall(r'\w+', seo_report_url_string))
                if word_count > 0 and word_count <= 100 and primary_keyword_url.lower() not in seo_report_url_string.lower():
                    st.write("3. Consider using the primary keyword within the first 100 words of the content.")
                # Suggestion 4: Use keyword in subheading
                if not re.search(r'<h[1-3]>.*{primary_keyword_url}.*<\/h[1-3]>', seo_report_url_string):
                    st.write("4. Consider using the primary keyword in subheadings (H1, H2, H3).")
                # Suggestion 5: Use keyword naturally (additional logic needed)
                st.write("5. Consider using the primary keyword naturally throughout the content.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Analyze Text Option
if selected_option == "Analyze Text":
    # Input text
    user_input = st.text_area("Enter your content:")
    # Input primary keyword
    primary_keyword = st.text_input("Enter the primary keyword for SEO analysis:")

    # Analyze text when the user submits
    if st.button("Analyze"):
        if user_input:
            # Check SEO optimization for the primary keyword in user-provided text
            seo_report = check_seo_optimization(user_input, primary_keyword)

            # Display SEO report
            st.subheader("SEO Optimization Report (User-provided text):")
            for item in seo_report:
                st.write(item)

# Analyze Web URL Option
elif selected_option == "Analyze Web URL":
    analyze_web_url()