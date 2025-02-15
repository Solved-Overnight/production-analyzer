import streamlit as st
import pdfplumber
import re
from datetime import datetime

# Streamlit app title
st.title("Production Data Analyzer")

# File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Process the PDF file
    output = f"Date: {datetime.now().strftime('%d-%b-%Y')}\n"

    with pdfplumber.open(uploaded_file) as pdf:
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

    # Display the output in the Streamlit app
    st.text_area("Analysis Results", output, height=400)