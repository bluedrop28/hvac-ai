import pdfplumber
import json


def extract_pipes_from_page(pdf_path, page_number):

    pipes = []
    seen = set()

    with pdfplumber.open(pdf_path) as pdf:
        if page_number < 1 or page_number > len(pdf.pages):
            print("Invalid page number.")
            return []
        page = pdf.pages[page_number - 1]

        # Remove hairlines (very thin drafting lines)
        lines = [
            l for l in page.lines
            if l.get("width", 0) > 0.5
        ]

        # Separate horizontal and vertical
        horizontal = []
        vertical = []
        for l in lines:
            x0, y0, x1, y1 = l["x0"], l["y0"], l["x1"], l["y1"]

            if abs(y0 - y1) < 1:  # horizontal
                if abs(x1 - x0) > 100:  # strong length filter
                    horizontal.append(l)

            if abs(x0 - x1) < 1:  # vertical
                if abs(y1 - y0) > 100:
                    vertical.append(l)

        # Horizontal Pipe Pairing

        for i in range(len(horizontal)):
            for j in range(i + 1, len(horizontal)):
                l1 = horizontal[i]
                l2 = horizontal[j]
                gap = abs(l1["y0"] - l2["y0"])
                overlap = min(l1["x1"], l2["x1"]) - max(l1["x0"], l2["x0"])

                if 3 < gap < 8 and overlap > 120:  # stronger overlap filter
                    x_start = round(max(l1["x0"], l2["x0"]), -1)   # round to nearest 10
                    x_end   = round(min(l1["x1"], l2["x1"]), -1)
                    center_y = round((l1["y0"] + l2["y0"]) / 2, 0)
                    pipe_key = (x_start, x_end, center_y)   
                
                    if pipe_key not in seen:
                        seen.add(pipe_key)
                        pipes.append({
                            "type": "horizontal",
                            "page": page_number,
                            "x_start": x_start,
                            "x_end": x_end,
                            "center_y": center_y,
                            "thickness": round(gap, 2)
                        })

        # Vertical Pipe Pairing

        for i in range(len(vertical)):
            for j in range(i + 1, len(vertical)):
                l1 = vertical[i]
                l2 = vertical[j]
                gap = abs(l1["x0"] - l2["x0"])
                overlap = min(l1["y1"], l2["y1"]) - max(l1["y0"], l2["y0"])

                if 3 < gap < 8 and overlap > 120:
                    center_x = round((l1["x0"] + l2["x0"]) / 2, 0)
                    y_start  = round(max(l1["y0"], l2["y0"]), -1)
                    y_end    = round(min(l1["y1"], l2["y1"]), -1)
                    pipe_key = (center_x, y_start, y_end)
                    if pipe_key not in seen:
                        seen.add(pipe_key)
                        pipes.append({
                            "type": "vertical",
                            "page": page_number,
                            "center_x": center_x,
                            "y_start": y_start,
                            "y_end": y_end,
                            "thickness": round(gap, 2)
                        })


    return pipes

# MAIN (User Input Controlled)

if __name__ == "__main__":
    pdf_path = "Vital A1-A2 HVAC Drawings.pdf"
    while True:
        user_input = input("\nEnter page number for piping extraction (0 to exit): ")
        if user_input.lower() == "exit" or user_input == "0":
            break
        page_number = int(user_input)
        pipes = extract_pipes_from_page(pdf_path, page_number)
        print(f"\nPIPES FOUND: {len(pipes)}\n")

        for p in pipes[:10]:  # print first 10 only
            print(p)
        output_file = f"pipes_page_{page_number}.json"
        with open(output_file, "w") as f:
            json.dump(pipes, f, indent=2)
        print(f"\nSaved {output_file}")
