import pdfplumber
import re
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)


# Function to create a visually structured and colored output
def format_output(title, data, total_prod):
    color = Fore.CYAN if "Lantabur" in title else Fore.MAGENTA  # Different colors for each section
    output = f"\n{color}╭─[ {title} ]──────────────────────────{Style.RESET_ALL}\n"
    output += f"{color}│{Style.RESET_ALL} {Fore.YELLOW}Loading Cap:{Style.RESET_ALL}\n"

    for row in data:
        color_group = row[0]
        quantity = row[1]

        # Calculate percentage of total production
        percentage = (float(quantity) / float(total_prod)) * 100
        output += f"{color}│ {Fore.GREEN}{color_group.ljust(20)}{Style.RESET_ALL} {quantity.rjust(6)} kg  ({percentage:6.2f}%)\n"

    output += f"{color}├──────────────────────────────────{Style.RESET_ALL}\n"

    if title == "Lantabur Data":
        output += f"{color}│ {Fore.BLUE}📌 LAB RFT: {Style.RESET_ALL}\n"
    output += f"{color}│ {Fore.CYAN}📅 Total this month:{Style.RESET_ALL}\n"

    output += f"{color}╰──────────────────────────────────{Style.RESET_ALL}\n"
    return output


# Formatted date
output = f"\n{Fore.YELLOW}📅 Date: {datetime.now().strftime('%d-%b-%Y')}{Style.RESET_ALL}\n"

# PDF file location
pdf_location = "/media/rishad/4EF86DBFF86DA5C5/Python_projects/production_data/Assets/06.02.25.pdf"

# Open the PDF file
with pdfplumber.open(pdf_location) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()  # Extract text from PDF

    # Extract total production values
    lantabur_total_prod = re.search(r'Lantabur Prod. (\d+)', text).group(1)
    taqwa_total_prod = re.search(r'Taqwa Prod. (\d+)', text).group(1)

    output += f"\n{Fore.GREEN}🏭 Lantabur Total Production: {lantabur_total_prod} kg{Style.RESET_ALL}\n"
    output += f"{Fore.MAGENTA}🏭 Taqwa Total Production:    {taqwa_total_prod} kg{Style.RESET_ALL}\n"

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

    # Generate formatted output for Lantabur & Taqwa
    output += format_output("Lantabur Data", industry_data["Lantabur"], int(lantabur_total_prod))
    output += format_output("Taqwa Data", industry_data["Taqwa"], int(taqwa_total_prod))

# Print the final output
print(output)
