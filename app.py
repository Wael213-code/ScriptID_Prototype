import streamlit as st
from PIL import Image
import time
import io
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import LCP_RL 
API_KEY = st.secrets["GOOGLE_API_KEY"]
Folder_Id = "1KAWg939Ac6I6upIitF3deSc6iZGn_vr-" # dbase top k test
Training_folder_id = "14qF5kESYluTQOWfw0EdduwFpOTAWAt9y" # Training folder
# --- Page Configuration ---
st.set_page_config(
    page_title="ScriptID - Historical Archive Prototype",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Historical Document Biometric Archive")
st.subheader("Offline text-independent writer recognition")
st.write("---")
# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
operation = st.sidebar.radio(
    "Select Core Operation:",
    ["🏠 Home","1. Enrollment", "2. Verification (1:1)", "3. Identification (1:N)"]
)

st.sidebar.info(
    "This prototype processes handwriting traits using handcrafted feature vectors, "
    "keeping analysis completely independent of the text content."
)
TARGET_FOLDER_ID = "1mmYt0Ggj6_UNy6OyjHaRZDPWf0Zinwvl"
if operation == "🏠 Home" :
    st.markdown("### Welcome to ScriptID")
    st.write(
        """
        **ScriptID** is an AI-powered historical document biometric platform designed to analyze 
        handwriting traits independently of the text written. Using specialized computer vision 
        and distance-metric algorithms, ScriptID enables accurate offline writer recognition for 
        archival research, manuscript authentication, and document forensic analysis.
        """
    )

    st.write("#### Select a Core Operation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 👤 Enrollment")
        st.write(
            "Extract feature vectors from newly digitized historical manuscripts and register them into the reference base."
        )

    with col2:
        st.markdown("### 🔍 Verification (1:1)")
        st.write(
            "Compare an unknown sample against a target claimed writer to confirm or reject authenticity using Chi² distance metric."
        )

    with col3:
        st.markdown("### 🗂️ Identification (1:N)")
        st.write(
            "Search an unidentified handwriting sample across the entire database of known writers to discover the Top-K most similar writer matches."
        )

    st.info("👈 Choose an operation from the sidebar navigation to begin.")

    st.write("---")

    # =====================================================================
    # REFERENCES & RESEARCH METHODOLOGY SECTION
    # =====================================================================
    st.markdown("### 📚 References & Research Methodology")

    ref_col1, ref_col2 = st.columns(2)

    with ref_col1:
        st.info(
            """
            **📁 Prototype Dataset (IAM Database)**  
            This prototype is configured specifically to run evaluations on samples preprocessed from the **IAM Handwriting Database**.
            
            * 🔗 [Official IAM Database Site](https://fki.tic.heia-fr.ch/databases/iam-handwriting-database) *(Original benchmark dataset by Marti & Bunke)*
            """
        )

    with ref_col2:
        st.success(
            """
            **📄 Scientific Foundation & Feature Extraction**  
            Our feature vector generation relies on handcrafted geometrical and local contour features, specifically **Local Contour Pattern with Run length Pixels Between Outer Contour Points**.
            
            * 🔗 [Read Methodological Paper (DOI/URL)](https://www.sciencedirect.com/science/article/pii/S1319157822001847#article)
            * **Publication Benchmark:** Classified under Top-tier (A+) Document Analysis & Pattern Recognition domain.
            """
        )

    st.info(
        "👈 Select an operation from the sidebar navigation to begin testing the system."
    )
# ================================================================
# 1. ENROLLMENT VIEW
# =====================================================================
elif operation == "1. Enrollment":
    st.header("👤 Document & Writer Enrollment")
    st.write("Extract handwriting traits from a new historical document and register it into the reference base.")
    st.warning(
        """
        ⚠️ **Functionality Notice:** Automated Document & Writer Enrollment is disabled in this public prototype. 
        
        Extracting text-independent feature vectors from raw historical manuscripts requires high-performance computational resources 
        (e.g., intensive image binarization, contour tracing, and GPU-accelerated feature extraction pipelines). 
        To maintain lightweight server performance, this prototype uses pre-computed feature vectors from the IAM database. \
         **🔗 Reference base:** If you would like to see the reference base we are using in this prototype here is a link to it (https://drive.google.com/file/d/11my0jUxZDgDVTGuiWyYXllCNorKIe2G7/view?usp=sharing)
        """
    )
    st.info("💡 To evaluate the biometric recognition algorithms, please navigate to **2. Verification (1:1)** or **3. Identification (1:N)** in the sidebar.")
# =====================================================================
# 2. VERIFICATION VIEW (1:1)
# =====================================================================
elif operation == "2. Verification (1:1)":
    st.header("🔍 Biometric Identity Verification (1:1)")
    st.write("Verify if an uploaded document matches a claimed historical writer identity.")
    st.warning(
        """**Note:** This prototype is not for final user, the verification process consists of preprocessing, feature extraction then verification. since we use a specific protocole to preprocess scanned images inorder to verify the authorship of a writer, uploading any scanned images makes it complicated at this phase (prototype). therefore, we privide preprocessed images from IAM database for testing the functionalities of the prototype." \
        Download an image from trainig database and uplaod it as the true identity and the download an image from testing database and upload as the claimed identity.
        """
    )
    # Training folder
    st.components.v1.iframe(
        src=f"https://drive.google.com/embeddedfolderview?id={Training_folder_id}#list",
        height=400,
        scrolling=True
    )
    # Testing folder
    st.components.v1.iframe(
        src=f"https://drive.google.com/embeddedfolderview?id={TARGET_FOLDER_ID}#list",
        height=400,
        scrolling=True
    )

    st.warning(
        """
        📌 **Crucial Filename Requirement:**  
        Do **NOT** rename the image files downloaded from the IAM dataset!  
        The system relies on the strict naming convention **`(writer id)_(sample number).png`** (e.g., `a01-000u_01.png` or `001_01.png`) to query and map feature vectors accurately from the database.
        """
    )
    reference_base_id = "11my0jUxZDgDVTGuiWyYXllCNorKIe2G7"
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Training DB (Claimed)")
        img1_file = st.file_uploader(
            "Upload Claimed Image", type=["jpg", "png", "bmp"], key="img1"
        )
        if img1_file:
            st.image(
                img1_file, caption=f"Claimed: {img1_file.name}", use_container_width=True
            )

    with col2:
        st.subheader("Testing DB (True)")
        img2_file = st.file_uploader(
            "Upload True Image", type=["jpg", "png", "bmp"], key="img2"
        )
        if img2_file:
            st.image(
                img2_file, caption=f"True: {img2_file.name}", use_container_width=True
        )
    if st.button("🔍 Run Verification Process", use_container_width=True):
        if not img1_file or not img2_file:
            st.warning(
                "Please upload both training and testing images before proceeding."
            )
        else:
            # Extract last 9 characters of the filename without extension if needed
            # Adjust slice [-9:] based on how your filenames match the CSV field
            sample_1 = img1_file.name
            sample_2 = img2_file.name

            with st.spinner("Downloading features & computing Chi² distance... it may take some minutes (less than 5min)"):
                is_authentic, distance = LCP_RL.verify(
                    reference_base_id, sample_1, sample_2
                )

            if distance is None:
                st.error(
                    "Could not locate feature vectors for the provided image samples in the database."
                )
            else:
                st.markdown("### Verification Result")
                st.metric(
                    label="Chi-Square Distance",
                    value=f"{distance:.5f}",
                    delta="Threshold < 0.0765",
                )

                if is_authentic:
                    st.success("✅ **ATHENTIC USER:** Match Verified!")
                else:
                    st.error("❌ **IMPOSTER USER:** Identity Spoof/Mismatch!")
            # Generate Clean Report Image
            report_buf = LCP_RL.generate_verification_report(
                img1_file, img2_file, distance, is_authentic
            )

            # Display generated report preview
            st.subheader("📊 Generated Verification Report")
            st.image(
                report_buf,
                caption="Verification Report Summary",
                use_container_width=True,
            )

            # Add Download Button
            st.download_button(
                label="📥 Download Report Image (.png)",
                data=report_buf,
                file_name=f"verification_report_{sample_1}_vs_{sample_2}.png",
                mime="image/png",
                use_container_width=True,
            )
# =====================================================================
# 3. IDENTIFICATION VIEW (1:N)
# =====================================================================
elif operation == "3. Identification (1:N)":
    st.header("🗂️ Global Database Identification (1:N)")
    st.write("Query an unknown document against the entire system index to find the most visually similar writing profiles.")
    st.warning(
        """**Note:** This prototype is not for final user, the identification process consists of preprocessing, feature extraction then identification. since we use a specific protocole to preprocess scanned images inorder to identify its writer, uploading any scanned images makes it complicated at this phase (prototype). therefore, we provide preprocessed images from IAM database for testing the functionalities of the prototype.
        Download an image from testing database and uplaod it, then select the number of top k matches where k is number the most similar writers for the unknown documents.
        """
    )
    st.write("Download an image from the database and then upload it.")
    #st.write("")
    st.components.v1.iframe(
        src=f"https://drive.google.com/embeddedfolderview?id={TARGET_FOLDER_ID}#list",
        height=400,
        scrolling=True
    )
    st.warning(
        """
        📌 **Crucial Filename Requirement:**  
        Do **NOT** rename the image files downloaded from the IAM dataset!  
        The system relies on the strict naming convention **`(writer id)_(sample number).png`** (e.g., `a01-000u_01.png` or `001_01.png`) to query and map feature vectors accurately from the database.
        """
    )
    DBase_top_k_folder_Id = "1KAWg939Ac6I6upIitF3deSc6iZGn_vr-" # dbase top k test
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload Unknown Document Image", type=["png", "jpg", "jpeg"], key="identify_upload")
        top_k = st.number_input("Number of top matches to return (K)", min_value=1, max_value=20, value=1)
        
        if uploaded_file is not None:
            file_name = uploaded_file.name
            if st.button("🔎 Search Feature Index"):
                with st.spinner("Searching vector registry..."):
                    time.sleep(2)
                    # 1. Load user's uploaded query image into PIL format
                    query_pil = Image.open(uploaded_file)
                    hit_list = LCP_RL.identify(file_name,DBase_top_k_folder_Id,API_KEY,top_k)
                    image_file_names = []
                    for element in hit_list:
                        image_file_names.append(element[1] + ".png")
                    
                    mock_retrieved_images = LCP_RL.get_images_from_drive(image_file_names,folder_id=Training_folder_id,api_key=API_KEY)

                    exp_metadata = {
                        "Database": "IAM",
                        "Feature": "LCP with RL Pixels Between Outer Contour Points",
                        "Cross validation": "Holdout",
                        "Classifier": "k-NN",
                        "Distance": "Chi-Square",
                        "Criterion": "Soft Top-N",
                        "Query_Writer_ID": f"{file_name[:-6]}",
                        "Query_Sample_ID": f"{file_name[:-4]}"
                    }
                    dashboard_image = LCP_RL.build_merged_dashboard(query_pil,exp_metadata,mock_retrieved_images)
                    st.session_state['result_dashboard'] = dashboard_image
    with col2:
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Query Document Target", use_container_width=True)
    if 'result_dashboard' in st.session_state and uploaded_file is not None:
        st.write("---")
        st.subheader("📊 Identification Results Dashboard")
        
        # Render the merged composite dashboard image
        st.image(
            st.session_state['result_dashboard'], 
            caption=f"Top-{top_k} Identification Dashboard", 
            use_container_width=True
        )

        # Download button to allow users to save the output image
        img_byte_arr = io.BytesIO()
        st.session_state['result_dashboard'].save(img_byte_arr, format='PNG')
        
        st.download_button(
            label="💾 Download Result Dashboard Image",
            data=img_byte_arr.getvalue(),
            file_name="identification_result_dashboard.png",
            mime="image/png"
        )