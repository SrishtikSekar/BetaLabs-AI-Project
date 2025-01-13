import PyPDF2
import spacy
import re

# Step 1: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# Step 2: Extract information using spaCy and regex
def parse_resume(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Initialize placeholders for details
    details = {
        "Name": None,
        "Phone": None,
        "Email": None,
        "Degree": [],
        "Institution": [],
        "Work Experience": [],
        "Projects": []
    }

    # Keywords for filtering institutions
    institution_keywords = ["University", "Institute", "College", "School", "Academy"]

    # Extract Name using spaCy's NER
    for ent in doc.ents:
        if ent.label_ == "PERSON" and details["Name"] is None:
            details["Name"] = ent.text

        # Extract Institutions (filtered by keywords)
        if ent.label_ == "ORG":
            for keyword in institution_keywords:
                if keyword.lower() in ent.text.lower():
                    details["Institution"].append(ent.text)

    # Extract Email using regex
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        details["Email"] = email_match.group(0)

    # Extract Phone using regex
    phone_match = re.search(r'\b\d{10}\b', text)  # Adjust regex for different formats
    if phone_match:
        details["Phone"] = phone_match.group(0)

    # Extract Full Degrees and Branches using regex
    degree_patterns = [
        r"(Bachelor(?:'s)?|Master(?:'s)?|Ph\.D|Diploma|Associate).*?(?:in|of)?.*?(Engineering|Technology|Science|Arts|Business Administration|Data Analytics|AI|Artificial Intelligence|CSE|ECE|Mechanical|Electrical|Civil|IT|Information Technology|Electronics|Physics|Mathematics|Biology|Architecture|Design|Robotics)[A-Za-z\s,]*"
    ]
    for pattern in degree_patterns:
        degrees = re.findall(pattern, text, re.IGNORECASE)
        if degrees:
            full_degrees = [' '.join(degree).strip() for degree in degrees]
            details["Degree"].extend(full_degrees)

    # Extract Work Experience (based on section header or job titles)
    work_experience_keywords = ["Work Experience", "Professional Experience", "Employment History"]
    experience_pattern = r"(Work Experience|Professional Experience|Employment History)([\s\S]+?)(?=(Projects|Education|Skills|$))"
    work_experience_match = re.search(experience_pattern, text, re.IGNORECASE)
    if work_experience_match:
        details["Work Experience"].append(work_experience_match.group(2).strip())

    # Extract Projects (based on section header)
    projects_pattern = r"(Projects|Key Projects|Notable Projects)([\s\S]+?)(?=(Work Experience|Education|Skills|$))"
    projects_match = re.search(projects_pattern, text, re.IGNORECASE)
    if projects_match:
        details["Projects"].append(projects_match.group(2).strip())

    # Deduplicate lists
    details["Degree"] = list(set(details["Degree"]))
    details["Institution"] = list(set(details["Institution"]))

    return details





# Step 3: Main Function
if __name__ == "__main__":
    pdf_path = "Resume.pdf"  # Replace with the path to your PDF file
    extracted_text = extract_text_from_pdf(pdf_path)
    parsed_data = parse_resume(extracted_text)

    print("Extracted Resume Details:")
for key, value in parsed_data.items():# to change the occurance of \n
    if isinstance(value, list):
        value = [item.replace("\n", " ") for item in value]  # Replace \n with spaces in lists
    elif isinstance(value, str):
        value = value.replace("\n", " ")  # Replace \n with spaces in strings
    print(f"{key}: {value}")

