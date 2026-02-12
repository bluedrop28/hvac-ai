import pdfplumber
import re
# Utility: Get Right Side Cropped Page
def get_right_side_page(page):
    width = page.width
    height = page.height
    return page.crop((width * 0.6, 0, width, height))

# GLOBAL METADATA (Only Page 1)

def extract_global_metadata(pdf_path):
    metadata = {}
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        right = get_right_side_page(page)
        text = right.extract_text()
    lines = text.split("\n")

    # Consultant
    for i, line in enumerate(lines):
        if "MARVEL" in line.upper():
            metadata["Consultant"] = "MARVEL"

    # Plot Plan
    match = re.search(r"#\d{4}", text)
    if match:
        metadata["Plot Plan"] = match.group(0)

    # Plot Name + Address
    for i, line in enumerate(lines):
        if "ALAFIA" in line.upper():
            metadata["Plot Name"] = line.strip()
            if i + 1 < len(lines):
                metadata["Plot Address"] = lines[i + 2].strip() + " " + lines[i + 3].strip()
            break

    # Scale
    scale_match = re.search(r'\d+/\d+"\s*=\s*1\'-0"', text)
    if scale_match:
        metadata["Scale"] = scale_match.group(0)

    return metadata

# PAGE METADATA 

def extract_page_metadata(pdf_path, page_number):
    page_data = {}
    with pdfplumber.open(pdf_path) as pdf:
        if page_number < 1 or page_number > len(pdf.pages):
            return {"Error": "Invalid page number"}
        page = pdf.pages[page_number - 1]
        right = get_right_side_page(page)
        text = right.extract_text()
        words = right.extract_words(extra_attrs=["size"])

    # Correct Date 
    big_dates = []
    for w in words:
        if re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", w["text"]):
            big_dates.append((w["size"], w["text"]))

    if big_dates:
        page_data["Date"] = sorted(big_dates, reverse=True)[0][1]
    # Page Title (Line between Plot Address and Scale)
    lines = text.split("\n")
    for line in lines:
        if (
            len(line.strip()) > 5
            and not re.search(r"#\d{4}", line)
            and not re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", line)
            and "ALAFIA" not in line.upper()
            and "MARVEL" not in line.upper()
            and "SCALE" not in line.upper()
        ):
            if any(word in line.upper() for word in ["MECHANICAL", "PLUMBING", "HVAC", "COVER"]):
                page_data["Page Title"] = line.strip()
                break

    # Drawing Number
    draw_match = re.search(r"\b[A-Z]-\d+\.\d+\b", text)
    if draw_match:
        page_data["Drawing"] = draw_match.group(0)

    return page_data


if __name__ == "__main__":
    pdf_path = "Vital A1-A2 HVAC Drawings.pdf"
    print("Reading global metadata once...\n")
    global_data = extract_global_metadata(pdf_path)
    while True:
        user_input = input("Enter page number (0 to exit): ")
        if user_input.lower() == "exit" or user_input == "0":
            break
        page_number = int(user_input)
        page_data = extract_page_metadata(pdf_path, page_number)
        final_output = {**global_data, **page_data}

        print("\n------ METADATA OUTPUT ------\n")
        for key, value in final_output.items():
            print(f"{key}: {value}")
