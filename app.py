import streamlit as st
import pdfplumber
import re
import pandas as pd
import plotly.express as px
import requests
import pyperclip
from simpleTextExtraction import copyText
from datetime import datetime

# Page Config
st.set_page_config(page_title="Production Data Analyzer", page_icon="📊", layout="wide")

# Sidebar - File Upload
st.sidebar.header("📂 Upload Production Report")
uploaded_file = st.sidebar.file_uploader("Choose a PDF", type="pdf")

# Main Title
st.title("📊 Production Data Analyzer")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()

        # Extract production totals
        lantabur_match = re.search(r'Lantabur Prod. (\d+)', text)
        taqwa_match = re.search(r'Taqwa Prod. (\d+)', text)

        if lantabur_match and taqwa_match:
            lantabur_total = float(lantabur_match.group(1))
            taqwa_total = float(taqwa_match.group(1))

            # Display summary metrics
            col1, col2 = st.columns(2)
            col1.metric("🏭 Lantabur Production", f"{lantabur_total} kg")
            col2.metric("🏭 Taqwa Production", f"{taqwa_total} kg")

            # Extract tables
            tables = page.extract_tables()
            industry_data = {"Lantabur": [], "Taqwa": []}

            for table in tables:
                industry = None
                for row in table:
                    if row[0]:
                        industry = row[0]
                    if industry in industry_data and row[1]:
                        industry_data[industry].append([row[1], float(row[2])])

            # Convert to DataFrame
            lantabur_df = pd.DataFrame(industry_data["Lantabur"], columns=["Color", "Quantity"])
            taqwa_df = pd.DataFrame(industry_data["Taqwa"], columns=["Color", "Quantity"])

            # Calculate percentage
            lantabur_df["Percentage"] = (lantabur_df["Quantity"] / lantabur_total) * 100
            taqwa_df["Percentage"] = (taqwa_df["Quantity"] / taqwa_total) * 100

            # --- Data Visualization ---
            tab1, tab2 = st.tabs(["📍 Lantabur Data", "📍 Taqwa Data"])

            with tab1:
                st.subheader("📊 Lantabur Production Breakdown", divider="rainbow")
                with st.expander("📜 View Data Table"):
                    st.dataframe(lantabur_df, use_container_width=True)
                fig1 = px.pie(lantabur_df, names="Color", values="Quantity", title="Lantabur Production by Color")
                st.plotly_chart(fig1, use_container_width=True)

            with tab2:
                st.subheader("📊 Taqwa Production Breakdown", divider="rainbow")
                with st.expander("📜 View Data Table"):
                    st.dataframe(taqwa_df, use_container_width=True)
                fig2 = px.pie(taqwa_df, names="Color", values="Quantity", title="Taqwa Production by Color")
                st.plotly_chart(fig2, use_container_width=True)

            # Share and Copy Buttons
            col1, col2 = st.columns(2)

            def share_report():
                try:
                    response = requests.post("https://cl1p.net/api", json={"data": copyText(uploaded_file)})
                    if response.status_code == 200:
                        share_url = response.json().get("url", "")
                        st.success(f"✅ Report shared successfully! [View Report]({share_url})")
                    else:
                        st.error("⚠️ Failed to share the report. Try again!")
                except:
                    st.error("⚠️ Error connecting to clipboard service.")

            def copy_to_clipboard():
                data = copyText(uploaded_file)
                pyperclip.copy(data)
                # st.success("📋 Report copied to clipboard!")

            with col1:
                st.button("📤 Share Report", on_click=share_report)
            with col2:
                st.button("📋 Copy to Clipboard", on_click=copy_to_clipboard())

            # Display report in a text area
            data = copyText(uploaded_file)
            st.text_area("📋 Report", data, height=300)
        else:
            st.error("⚠️ Could not find production data in the PDF.")


        def copyText(PDF):
            output = f"Date: {datetime.now().strftime('%d-%b-%Y')}\n"

            with pdfplumber.open(PDF) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()  # Extract text from PDF

                # Search for total production values using regular expressions
                lantabur_total_prod = re.search(r'Lantabur Prod. (\d+)', text).group(1)
                taqwa_total_prod = re.search(r'Taqwa Prod. (\d+)', text).group(1)

                output += f"Lantabur total production = {lantabur_total_prod}kg\n"
                output += f"Taqwa total production = {taqwa_total_prod}kg\n"

                # Extract tables from the page
                tables = page.extract_tables()

                # Dictionary to store extracted data for each industry
                industry_data = {"Lantabur": [], "Taqwa": []}

                # Iterate over tables and process data
                for table in tables:
                    industry = None  # Variable to track the current industry

                    for row in table:
                        if row[0]:  # If the industry name is present in this row
                            industry = row[0]  # Update the current industry

                        # Append data to the respective industry (only if industry is 'Lantabur' or 'Taqwa')
                        if industry in industry_data and row[1]:  # Ensure the row contains valid data
                            industry_data[industry].append(row[1:])

                # Combine Inhouse and Sub Contract data with color values
                for industry in ["Lantabur", "Taqwa"]:
                    output += f"\n╰─>{industry} Data:\nLoading cap:\n"

                    # Merge all data for the industry into a single list
                    combined_data = industry_data[industry]

                    # Print combined data
                    for row in combined_data:
                        color_group = row[0]  # Color name or category
                        quantity = row[1]  # Corresponding quantity

                        # Calculate percentage of total production
                        if industry == "Lantabur":
                            percentage = (float(quantity) / float(lantabur_total_prod)) * 100
                        else:
                            percentage = (float(quantity) / float(taqwa_total_prod)) * 100

                        # Append the combined data to the output variable
                        output += f"{color_group}: {quantity}kg ({percentage:.2f}%)\n"

                    # Add LAB RFT and Total this month for Lantabur
                    if industry == "Lantabur":
                        output += "\nLAB RFT: \n"
                        output += "Total this month: \nAvg/day:\n"
                    else:
                        output += "\nTotal this month: \nAvg/day:"

            return output
else:
    st.info("📂 Please upload a PDF to analyze.")
