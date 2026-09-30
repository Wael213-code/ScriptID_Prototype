import csv
import io
import urllib.request
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageFont
import math
import gdown
import matplotlib.pyplot as plt
import os
# top + features + 2 empty lines + the actual line = top + 4
def get_file_id_by_name(filename, folder_id, api_key):
    service = build('drive', 'v3', developerKey=api_key)
    query = f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        raise FileNotFoundError(f"File {filename} not found in Google Drive folder.")
    return items[0]['id']
    
# Using drive folder files
def identify(image_path,Folder_Id,API_KEY,top_k) : 
    file_path = f"dbase_test_Top_{top_k}.csv"
    file_id = get_file_id_by_name(file_path, Folder_Id, API_KEY)
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    req = urllib.request.urlopen(url)
    csvfile = io.StringIO(req.read().decode('utf-8'))
    fl = csv.reader(csvfile,delimiter=";")
    for i in range(1,21) :
        next(fl)
    i = 0
    j = 0
    top_k_hit_list = []
    for line in fl:
        if(i % (top_k + 4) == 0 ) :
            if(line[1][-9:] == image_path) :
                next(fl)
                j = 0
                for document in fl :
                    if (j < top_k) :
                        #print(document)
                        top_k_hit_list.append(document)
                    j += 1
        i += 1
    return top_k_hit_list

# Retrieving top matches' images from drive
def get_images_from_drive(image_filenames, folder_id, api_key):
    service = build("drive", "v3", developerKey=api_key)
    images_dict = {}

    for filename in image_filenames:
        # 1. Search for the image inside the folder by filename
        query = (
            f"'{folder_id}' in parents and name = '{filename}' and trashed = false"
        )
        results = (
            service.files().list(q=query, fields="files(id, name)").execute()
        )
        items = results.get("files", [])

        if items:
            file_id = items[0]["id"]

            # 2. Download the image bytes
            download_url = (
                f"https://drive.google.com/uc?export=download&id={file_id}"
            )
            req = urllib.request.urlopen(download_url)
            image_data = req.read()

            # 3. Convert bytes into PIL Image object (or save locally)
            img = Image.open(io.BytesIO(image_data))
            images_dict[filename] = img
            print(f"Successfully loaded: {filename}")
        else:
            print(f"Image not found in Drive folder: {filename}")

    return images_dict


# Handling fonts sizes
def get_large_font(size):
    """
    Attempts to load a scalable system font across Linux, Windows, and macOS.
    Falls back to PIL default font if none are found.
    """
    font_paths = [
        # Linux / Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        # Windows
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

# Generating identification report
def build_merged_dashboard(query_img,metadata,results_dict,output_path="merged_result_dashboard.png"):
    """
    Builds a large, high-resolution composite dashboard image containing 
    the query image, experiment metadata, and Top-N results.
    """
    top_n = max(1, min(20, len(results_dict)))
    results_data = list(results_dict.items())[:top_n]

    # --- 1. Dynamic Grid & High-Res Cell Dimensions ---
    cols = 2 if top_n > 1 else 1
    rows = math.ceil(top_n / cols)

    # Expanded dimensions for crisp, large display
    cell_w = 900       # Width per result image box
    cell_h = 360       # Height per result image box
    header_h = 45      # Height of title bar above each result image
    padding = 25       # Outer and inter-cell padding

    # Load scalable font or fallback
    font_large = get_large_font(25)   # Query title
    font_header = get_large_font(22)  # Result headers (Rank = XX)
    font_meta = get_large_font(24)    # Metadata sidebar

    # Total canvas dimensions
    grid_w = (cols * cell_w) + ((cols + 1) * padding)
    top_section_h = 380
    grid_h = (rows * (cell_h + header_h)) + ((rows + 1) * padding)
    canvas_w = max(1800, grid_w)
    canvas_h = top_section_h + grid_h

    # Create high-res white background canvas
    canvas = Image.new("RGB", (canvas_w, canvas_h), color=(240, 240, 240))
    draw = ImageDraw.Draw(canvas)

    # --- 2. Top Section (Metadata & Query Image) ---
    
    # Metadata Box (Left)
    meta_x, meta_y = padding, padding + 10
    formatted_meta = (
        f"Database: {metadata.get('Database', '')}\n"
        f"Feature: {metadata.get('Feature', '')}\n"
        f"Cross validation: {metadata.get('Cross validation', '')}\n"
        f"Classifier: {metadata.get('Classifier', '')}\n"
        f"Distance: {metadata.get('Distance', '')}\n"
        f"Hit list size: Top-{top_n}\n"
        f"Criterion: {metadata.get('Criterion', '')}"
    )
    draw.text((meta_x, meta_y), formatted_meta, fill=(0, 0, 0), font=font_meta)

    # Query Image (Right Side)
    q_img_obj = Image.open(query_img) if isinstance(query_img, str) else query_img
    q_width = 950
    q_height = top_section_h - 60 - padding
    q_img_resized = q_img_obj.resize((q_width, q_height))
    
    q_x = canvas_w - q_width - padding
    q_y = padding + 35
    canvas.paste(q_img_resized, (q_x, q_y))

    # Query Header Banner
    q_title = f"Query: Writer ID = {metadata.get('Query_Writer_ID', 'N/A')}, Sample ID = {metadata.get('Query_Sample_ID', 'N/A')}"
    draw.rectangle([q_x, padding, q_x + q_width, padding + 35], fill=(255, 255, 204), outline=(0, 0, 0), width=2)
    draw.text((q_x + 15, padding + 6), q_title, fill=(0, 0, 0), font=font_large)
    draw.rectangle([q_x, q_y, q_x + q_width, q_y + q_height], outline=(0, 0, 0), width=2)

    # --- 3. Large Grid Results Section ---
    grid_start_y = top_section_h

    for idx, (file_name, img_data) in enumerate(results_data):
        r = idx // cols
        c = idx % cols

        x = padding + c * (cell_w + padding)
        y = grid_start_y + padding + r * (cell_h + header_h + padding)

        # Header Banner (Light Green for Rank 1)
        header_bg = (217, 242, 217) if idx == 0 else (255, 255, 255)
        draw.rectangle([x, y, x + cell_w, y + header_h], fill=header_bg, outline=(0, 0, 0), width=2)
        
        title_str = f"Rank = {idx + 1:02d} | File: {file_name}"
        draw.text((x + 12, y + 10), title_str, fill=(0, 0, 0), font=font_header)

        # High-Res Sample Image
        pil_img = Image.open(img_data) if isinstance(img_data, str) else img_data
        sample_resized = pil_img.resize((cell_w, cell_h))
        
        img_y = y + header_h
        canvas.paste(sample_resized, (x, img_y))
        draw.rectangle([x, img_y, x + cell_w, img_y + cell_h], outline=(0, 0, 0), width=2)

    # Open the enlarged image viewer
    #canvas.show()
    #canvas.save(f"csv_files/Top_{top_k}_identification.png")
    return canvas

# Verification functions ...

# Chai square distance
def chi2_distance(pdf1, pdf2, eps=1e-10):
    size = len(pdf1) 
    distance = 0
    for i in range(size) :
        distance += ((pdf1[i] - pdf2[i]) ** 2) / (pdf1[i] + pdf2[i] + eps)
    return (distance / 2)

# CSV processing helper function
def get_line_at(reference_base_id,position) :
    url = f"https://drive.google.com/uc?id={reference_base_id}"
    # 1. Create an in-memory byte buffer
    memory_buffer = io.BytesIO()
    
    # 2. Stream the download directly into RAM
    gdown.download(url, output=memory_buffer, quiet=False)
    
    # 3. Move buffer cursor back to the start
    memory_buffer.seek(0)
    
    # 4. Wrap in TextIOWrapper and read line-by-line
    text_stream = io.TextIOWrapper(memory_buffer, encoding="utf-8")
    reader = csv.reader(text_stream,delimiter=";")
    for i in range(1,position) :
        next(reader)
    our_line = []
    for line in reader :
        our_line = line
        break
    return our_line

# Verification process
def verify(reference_base_id,sample_1,sample_2) :
    url = f"https://drive.google.com/uc?id={reference_base_id}"
    # 1. Create an in-memory byte buffer
    memory_buffer = io.BytesIO()

    # 2. Stream the download directly into RAM
    gdown.download(url, output=memory_buffer, quiet=False)

    # 3. Move buffer cursor back to the start
    memory_buffer.seek(0)

    # 4. Wrap in TextIOWrapper and read line-by-line
    text_stream = io.TextIOWrapper(memory_buffer, encoding="utf-8")
    reader = csv.reader(text_stream,delimiter=";")

    for i in range(1,9):
        next(reader)
    stop = 0
    distance_vects = []
    for line in reader :
        if (stop % 5 == 0) :
            if (line[1][-9:] == sample_1 or line[1][-9:] == sample_2) :
                distance_vects.append(get_line_at(reference_base_id,(stop + 1)))
                if (len(distance_vects) == 2) : break
        stop += 1 
    pdf1 = distance_vects[0][1:-1]
    pdf2 = distance_vects[1][1:-1]   
    for i in range(0,len(pdf1)) :
        pdf1[i] = float(pdf1[i].replace(",","."))
        pdf2[i] = float(pdf2[i].replace(",","."))
    distance = chi2_distance(pdf1,pdf2)
    authenticity = distance < 0.0765
    return authenticity,distance


# Generating verification process
def generate_verification_report(img1, img2, distance, is_authentic):
    # Generates a clean visual report image showing side-by-side images and verification metadata.
    fig = plt.figure(figsize=(9, 5), dpi=150)
    fig.patch.set_facecolor("#f8f9fa")

    # 1. Main Title Header
    plt.suptitle(
        "1:1 BIOMETRIC VERIFICATION REPORT",
        fontsize=14,
        fontweight="bold",
        y=0.95,
    )

    # 2. Display Claimed Image
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.imshow(Image.open(img1))
    ax1.set_title(
        f"Claimed Identity\n({img1.name[:3]})", fontsize=9, fontweight="bold"
    )
    ax1.axis("off")

    # 3. Display True Image
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.imshow(Image.open(img2))
    ax2.set_title(f"True Identity\n({img2.name[:3]})", fontsize=9, fontweight="bold")
    ax2.axis("off")

    # 4. Results Card (Right panel)
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.axis("off")

    status_str = "AUTHENTIC" if is_authentic else "IMPOSTER"
    status_color = "#28a745" if is_authentic else "#dc3545"

    summary_text = (
        f"DECISION: {status_str}\n"
        f"----------------------\n"
        f"Chi-Sq Distance:\n  {distance:.5f}\n\n"
        f"Threshold:\n  0.0765\n\n"
        f"Result:\n  "
        f"{'AUTHENTIC' if is_authentic else 'MISMATCH'}"
    )

    ax3.text(
        0.05,
        0.5,
        summary_text,
        fontsize=10,
        fontweight="bold",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.8",
            facecolor="white",
            edgecolor=status_color,
            linewidth=2.5,
        ),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.90])

    # Convert plot figure to BytesIO PNG buffer
    report_buffer = io.BytesIO()
    plt.savefig(
        report_buffer,
        format="png",
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    report_buffer.seek(0)

    return report_buffer
