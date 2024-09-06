


def convert_to_pdf_url(general_url):
    parts = general_url.strip('/').split('/')
    
    if len(parts) < 2:
        raise ValueError("Invalid URL format")
    
    session = parts[1]  # '37-1'
    bill_number = parts[2]  # 'C-330'
    # Remove the dash in the session to form '371'
    session_number = session.replace('-', '')
    
    # Assume the bill type is 'Private' (can be adjusted based on your needs)
    bill_type = "Private"
    
    # Construct the PDF URL
    pdf_url = f"https://www.parl.ca/Content/Bills/{session_number}/{bill_type}/{bill_number}/{bill_number.lower()}_1/{bill_number.lower()}_1.pdf"
    
    return pdf_url