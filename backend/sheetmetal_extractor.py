import pdfplumber
import json
import math


def extract_ducts_from_page(pdf_path, page_number):
    ducts = []
    seen = set()

    with pdfplumber.open(pdf_path) as pdf:

        if page_number < 1 or page_number > len(pdf.pages):
            print("Invalid page number")
            return []

        page = pdf.pages[page_number - 1]
        lines = page.lines
        page_width = page.width
        page_height = page.height

        for line in lines:
            x0 = round(line["x0"], 1)
            x1 = round(line["x1"], 1)
            y0 = round(line["y0"], 1)
            y1 = round(line["y1"], 1)
            thickness = round(line.get("linewidth", 0), 2)
            if thickness < 9.5:
                continue

            length = math.hypot(x1 - x0, y1 - y0)
            if length < 80:
                continue

            if (
                x0 < 40 or x1 > page_width - 40 or
                y0 < 40 or y1 > page_height - 40
            ):
                continue
            # Horizontal
            if abs(y0 - y1) < 2:
                key = ("H", x0, x1, y0)

                if key not in seen:
                    seen.add(key)
                    ducts.append({
                        "type": "horizontal",
                        "page": page_number,
                        "x_start": min(x0, x1),
                        "x_end": max(x0, x1),
                        "center_y": y0,
                        "thickness": thickness,
                        "length": round(length, 1)
                    })

            # Vertical
            elif abs(x0 - x1) < 2:
                key = ("V", y0, y1, x0)

                if key not in seen:
                    seen.add(key)
                    ducts.append({
                        "type": "vertical",
                        "page": page_number,
                        "y_start": min(y0, y1),
                        "y_end": max(y0, y1),
                        "center_x": x0,
                        "thickness": thickness,
                        "length": round(length, 1)
                    })
    return ducts

if __name__ == "__main__":
    pdf_path = "Vital A1-A2 HVAC Drawings.pdf"
    while True:
        user_input = input("\nEnter page number for sheet metal extraction (0 to exit): ")
        if user_input.lower() in ["0", "exit"]:
            break
        if not user_input.isdigit():
            print("Invalid input. Enter a number.")
            continue
        page_number = int(user_input)
        ducts = extract_ducts_from_page(pdf_path, page_number)
        print(f"\nDUCTS FOUND: {len(ducts)}\n")
        for d in ducts[:10]:
            print(d)
