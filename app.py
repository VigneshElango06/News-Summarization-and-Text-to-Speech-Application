import streamlit as st
import requests
import io
import base64

def main():
    st.title("Company News Sentiment Analysis and TTS")

    company_name = st.text_input("Enter Company Name:")

    if st.button("Get Sentiment Report"):
        if company_name:
            try:
                api_url = fapi_url = f"http://127.0.0.1:8000/analyze_company?company_name={company_name}" # Replace with your deployed API URL
                return {"message": f"API works! Company: {company_name}"}
                response = requests.get(api_url)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                if data:
                    st.subheader("News Sentiment Report")
                    for article in data["articles"]:
                        st.write(f"**Title:** {article['title']}")
                        st.write(f"**Summary:** {article['summary']}")
                        st.write(f"**Sentiment:** {article['sentiment']}")
                        st.write(f"**Topics:** {', '.join(article['topics'])}")
                        st.write("---")

                    st.subheader("Comparative Analysis")
                    st.json(data["comparative_analysis"])

                    if "audio_base64" in data:
                        audio_bytes = base64.b64decode(data["audio_base64"])
                        st.audio(audio_bytes, format="audio/wav")

                else:
                     st.write("No news articles found for the given company.")

            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                print(f"Request Error: {e}") #print error for debugging.
            except KeyError as e:
                st.error(f"Error processing data: {e}")
                print(f"Key Error: {e}") #print error for debugging.
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                print(f"Unexpected Error: {e}") #print error for debugging.
        else:
            st.warning("Please enter a company name.")

if __name__ == "__main__":
    main()
