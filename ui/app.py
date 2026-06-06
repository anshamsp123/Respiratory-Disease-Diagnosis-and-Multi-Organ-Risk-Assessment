import streamlit as st # Reload trigger: 2026-05-04 00:53
import requests
from PIL import Image
import sys
import os
import io
import base64
import streamlit.components.v1 as components

# Add parent dir to path so we can import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.explainability import generate_simulated_gradcam
from utils.risk_rules import generate_alerts, get_clinical_correlations, get_treatment_suggestions
from utils.simulation import generate_risk_timeline_chart, generate_contribution_pie_chart

st.set_page_config(page_title="Respiratory AI Diagnostics", layout="wide")

# Custom CSS for minimalist feel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        font-weight: 600;
        background-color: #1a1a1a;
        color: #ffffff;
        border: none;
        padding: 0.6rem 1rem;
        transition: opacity 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1a1a1a;
        color: #ffffff;
        opacity: 0.8;
    }
    div[data-testid="metric-container"] {
        background-color: #fafafa;
        border-radius: 4px;
        padding: 1.2rem;
        border: 1px solid #eaeaea;
        box-shadow: none;
    }
    [data-testid="stFileUploadDropzone"] {
        border-radius: 4px;
        border: 1px dashed #cccccc;
        background-color: #fafafa;
    }
    .risk-high { color: #d32f2f; font-weight: 600; }
    .risk-med { color: #f57c00; font-weight: 600; }
    .risk-low { color: #388e3c; font-weight: 600; }
    .alert-critical { background-color: #ffebee; color: #c62828; padding: 12px; border-radius: 5px; border-left: 5px solid #c62828; margin-bottom: 15px; }
    .alert-warning { background-color: #fff8e1; color: #f57f17; padding: 12px; border-radius: 5px; border-left: 5px solid #f57f17; margin-bottom: 15px; }
    .badge-low { background-color: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold;}
    .badge-medium { background-color: #fff3e0; color: #ef6c00; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold;}
    .badge-high { background-color: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_model_base64():
    """Reads and encodes the 3D lung model to base64 for embedding in the HTML component."""
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "realistic_human_lungs.glb")
    if not os.path.exists(model_path):
        return None
    with open(model_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_lung_model(risk_level, disease="Normal"):
    """Renders a 3D lung model using Three.js with dynamic coloring and localized highlighting."""
    colors = {
        "low": "#a8dadc", # Soft blue-green for healthy
        "medium": "#f4a261", # Orange for caution
        "high": "#e76f51"  # Deep red for high risk
    }
    target_color = colors.get(risk_level, "#a8dadc")
    model_base64 = get_model_base64()
    
    if not model_base64:
        st.error("3D model file (realistic_human_lungs.glb) could not be loaded.")
        return

    html_code = f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/loaders/GLTFLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/controls/OrbitControls.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #fafafa; }}
            #container {{ width: 100%; height: 100vh; }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <script>
            let scene, camera, renderer, model, controls;
            let markers = [];
            const riskLevel = "{risk_level}";
            const diseaseType = "{disease}";

            function init() {{
                scene = new THREE.Scene();
                
                camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
                camera.position.set(0, 0, 5);

                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(document.getElementById('container').clientWidth, document.getElementById('container').clientHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                document.getElementById('container').appendChild(renderer.domElement);

                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
                scene.add(ambientLight);

                const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
                directionalLight.position.set(5, 10, 7.5);
                scene.add(directionalLight);

                const loader = new THREE.GLTFLoader();
                const modelData = "data:model/gltf-binary;base64,{model_base64}";
                
                loader.load(modelData, function (gltf) {{
                    model = gltf.scene;
                    model.traverse((node) => {{
                        if (node.isMesh) {{
                            node.material = new THREE.MeshPhongMaterial({{
                                color: "{target_color}",
                                shininess: 50,
                                transparent: true,
                                opacity: diseaseType !== "Normal" ? 0.2 : 0.45,
                                side: THREE.DoubleSide
                            }});
                        }}
                    }});
                    
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    model.position.sub(center);
                    
                    const maxDim = Math.max(size.x, size.y, size.z);
                    camera.position.z = maxDim * 2.2;
                    scene.add(model);

                    // --- DISEASE HIGHLIGHT LOGIC ---
                    if (diseaseType !== "Normal") {{
                        const addMarker = (x, y, z, color=0xff3300) => {{
                            // Create a core sphere and a larger glow sphere
                            const coreGeo = new THREE.SphereGeometry(maxDim * 0.08, 32, 32);
                            const glowGeo = new THREE.SphereGeometry(maxDim * 0.15, 32, 32);
                            
                            const coreMat = new THREE.MeshBasicMaterial({{
                                color: color,
                                transparent: true,
                                opacity: 0.9,
                                blending: THREE.AdditiveBlending
                            }});
                            
                            const glowMat = new THREE.MeshBasicMaterial({{
                                color: color,
                                transparent: true,
                                opacity: 0.3,
                                blending: THREE.AdditiveBlending
                            }});

                            const core = new THREE.Mesh(coreGeo, coreMat);
                            const glow = new THREE.Mesh(glowGeo, glowMat);
                            
                            const group = new THREE.Group();
                            group.add(core);
                            group.add(glow);
                            group.position.set(x, y, z);
                            
                            scene.add(group);
                            markers.push(group);
                        }};

                        if (diseaseType === "Pneumonia") {{
                            // Pneumonia: Restricted to Mid/Lower Lobes
                            addMarker(-size.x * 0.2, -size.y * 0.15, size.z * 0.1);
                        }} else if (diseaseType === "Pulmonary Fibrosis") {{
                            // Fibrosis: Lower/Peripheral (Bilateral)
                            addMarker(size.x * 0.3, -size.y * 0.3, 0);
                            addMarker(-size.x * 0.3, -size.y * 0.35, 0);
                        }} else if (diseaseType === "Pleural Effusion") {{
                            // Effusion: Very low, near costophrenic angles
                            addMarker(size.x * 0.25, -size.y * 0.45, size.z * 0.05, 0x00aaff); // Blue-ish for fluid
                        }} else if (diseaseType === "COPD") {{
                            // COPD: Distributed central
                            addMarker(0, 0, 0, 0xffaa00);
                        }}
                    }}
                    
                    animate();
                }});
            }}

            function animate() {{
                requestAnimationFrame(animate);
                const time = Date.now() * 0.005;
                
                if (model) {{
                    model.rotation.y += 0.003;
                    // Subtle overall lung pulsing if disease detected
                    if (diseaseType !== "Normal") {{
                        const pulse = 1 + Math.sin(time * 0.5) * 0.02;
                        model.scale.set(pulse, pulse, pulse);
                    }}
                }}
                
                // Pulsing effect for markers
                markers.forEach(group => {{
                    const s = 1 + Math.sin(time) * 0.15;
                    group.scale.set(s, s, s);
                    group.children[1].material.opacity = 0.2 + Math.sin(time) * 0.1; // Glow pulses more
                }});

                controls.update();
                renderer.render(scene, camera);
            }}

            init();
        </script>
    </body>
    </html>
    """
    st.markdown("<p style='font-weight: 600; font-size: 1.1rem; margin-bottom: 0;'>Anatomical Localization (3D)</p>", unsafe_allow_html=True)
    components.html(html_code, height=400)

# State management
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.result = None
    st.session_state.uploaded_file_bytes = None
    st.session_state.age = 45
    st.session_state.spo2 = 96
    st.session_state.creatinine = 0.9
    st.session_state.troponin = 0.02

st.sidebar.title("Navigation Sections")
nav = st.sidebar.radio("", ["Clinical Input", "Diagnostic Results", "Explainable AI", "Systemic Risk Analysis"])

st.title("Multimodal Respiratory AI")
st.markdown("<p style='color: #666; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px;'>Simulated deep learning pipeline for disease prediction & systemic organ risk analysis</p>", unsafe_allow_html=True)

if nav == "Clinical Input":
    st.subheader("Clinical Data & Imaging")
    with st.container(border=True):
        uploaded_file = st.file_uploader("Upload Chest X-ray", type=["jpg", "jpeg", "png"])
        
        symptoms = st.text_area("Patient Symptoms", placeholder="e.g., Shortness of breath, dry cough, fever...")
        
        st.markdown("##### Biomarkers")
        col_a, col_b = st.columns(2)
        with col_a:
            age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.age)
            spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=st.session_state.spo2)
        with col_b:
            creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.1, max_value=15.0, value=st.session_state.creatinine, step=0.1)
            troponin = st.number_input("Troponin (ng/mL)", min_value=0.0, max_value=10.0, value=st.session_state.troponin, step=0.01)

        analyze_btn = st.button("Run Multimodal AI Analysis")
        
        if analyze_btn:
            if uploaded_file is None:
                st.warning("Please upload a Chest X-ray image to proceed.")
            else:
                with st.spinner("Fusing ResNet18 features and Tabular representations..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        "age": age,
                        "spo2": spo2,
                        "creatinine": creatinine,
                        "troponin": troponin,
                        "symptoms": symptoms
                    }
                    
                    try:
                        response = requests.post("http://127.0.0.1:8000/predict", files=files, data=data)
                        if response.status_code == 200:
                            st.session_state.result = response.json()
                            st.session_state.analysis_complete = True
                            st.session_state.uploaded_file_bytes = uploaded_file.getvalue()
                            st.session_state.age = age
                            st.session_state.spo2 = spo2
                            st.session_state.creatinine = creatinine
                            st.session_state.troponin = troponin
                            st.success("Analysis Complete. Please navigate to other sections using the left sidebar.")
                        else:
                            st.error(f"Error from API: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection failed: {e}. Is the FastAPI backend running on port 8000?")

elif not st.session_state.analysis_complete:
    st.info("Please complete the analysis in the 'Clinical Input' section first.")

else:
    # Use session state variables
    result = st.session_state.result
    age = st.session_state.age
    spo2 = st.session_state.spo2
    creatinine = st.session_state.creatinine
    troponin = st.session_state.troponin
    rk = result['organ_risk']['kidney']
    rh = result['organ_risk']['heart']
    rl = result['organ_risk']['liver']
    conf = result['confidence'] * 100
    alerts = generate_alerts(spo2, creatinine, troponin)
    
    if nav == "Diagnostic Results":
        # 1. CASE SUMMARY PANEL
        st.markdown("### Case Summary")
        
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        summary_col1.metric("Patient Age", age)
        summary_col2.metric("Predicted Disease", result["disease"])
        summary_col3.metric("Severity", result["severity"])
        
        # Calculate Overall Risk Level
        overall_risk = "Low"
        overall_risk_score = (rk + rh) / 2
        if overall_risk_score > 60 or result["severity"] == "High":
            overall_risk = "High"
        elif overall_risk_score > 30 or result["severity"] == "Moderate":
            overall_risk = "Medium"
        summary_col4.metric("Overall Risk Level", overall_risk)
        
        # 2. CLINICAL ALERT SYSTEM
        if alerts:
            st.markdown("### Clinical Alerts")
            for alert in alerts:
                st.markdown(f"<div class='alert-{alert['level']}'><strong>{alert['msg']}</strong></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 3. MULTIMODAL CONTRIBUTION
        st.markdown("### Multimodal Fusion Analysis")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown("**Model Contribution Breakdown**")
            pie_chart_buf = generate_contribution_pie_chart()
            st.image(pie_chart_buf, use_container_width=True)
        with m_col2:
            st.markdown("**Clinical Correlation**")
            correlations = get_clinical_correlations(spo2, creatinine, troponin)
            for corr in correlations:
                st.markdown(f"- {corr}")
            
            st.markdown("**Model Confidence & Uncertainty**")
            uncertainty_level = "Low" if conf > 85 else "Medium" if conf >= 60 else "High"
            badge_class = "badge-low" if uncertainty_level == "Low" else "badge-medium" if uncertainty_level == "Medium" else "badge-high"
            
            st.metric("Confidence", f"{conf:.1f}%")
            st.markdown(f"Uncertainty Level: <span class='{badge_class}'>{uncertainty_level}</span>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Treatment Suggestions
        st.markdown("### Treatment Suggestions")
        suggestions = get_treatment_suggestions(spo2, result["severity"])
        for sug in suggestions:
            st.markdown(f"- {sug}")
        st.caption("*Disclaimer: This is not medical advice. Outputs are generated by an AI research prototype for decision support.*")
        
        st.markdown("---")
        
        report_content = f"MULTIMODAL RESPIRATORY AI - PATIENT REPORT\n\nAge: {age}\nSpO2: {spo2}%\nCreatinine: {creatinine} mg/dL\nTroponin: {troponin} ng/mL\n\nPredicted Disease: {result['disease']}\nSeverity: {result['severity']}\nConfidence: {conf:.1f}%\n\nKidney Risk: {rk}%\nHeart Risk: {rh}%\n\nAlerts:\n"
        for alert in alerts:
            report_content += f"- {alert['msg']}\n"
        
        st.download_button(
            label="Download Patient Report",
            data=report_content,
            file_name="patient_report.txt",
            mime="text/plain"
        )
            
    elif nav == "Explainable AI":
        st.markdown("### Image Localization & 3D Visualization")
        
        # Risk Logic for 3D Model
        if spo2 < 90:
            lung_risk = "high"
        elif 90 <= spo2 <= 94:
            lung_risk = "medium"
        else:
            lung_risk = "low"
            
        img_col1, img_col2 = st.columns(2)
        img = Image.open(io.BytesIO(st.session_state.uploaded_file_bytes))
        
        with img_col1:
            st.markdown("**Model Attention (Grad-CAM)**")
            cam_img = generate_simulated_gradcam(img)
            st.image(cam_img, use_container_width=True)
            st.caption("Heatmap highlighting pulmonary regions with highest diagnostic weighting.")
            
        with img_col2:
            render_lung_model(lung_risk, result["disease"])
            st.caption(f"Interactive model colored by risk level (Current: **{lung_risk.capitalize()}**) based on SpO2 data.")
            
        st.markdown("#### Explainability Report")
        st.info(result.get("explanation", "Explanation not available."))

    elif nav == "Systemic Risk Analysis":
        st.markdown("### Systemic Organ Risk Analysis")
        
        risk_col1, risk_col2 = st.columns([1, 1.5])
        with risk_col1:
            st.markdown("**Current Risk Levels**")
            def get_risk_class(val):
                if val < 30: return "risk-low"
                elif val < 60: return "risk-med"
                else: return "risk-high"
            
            st.markdown(f"**Kidney Risk**: <span class='{get_risk_class(rk)}'>{rk}%</span>", unsafe_allow_html=True)
            st.progress(rk / 100.0)
            
            st.markdown(f"**Heart Risk**: <span class='{get_risk_class(rh)}'>{rh}%</span>", unsafe_allow_html=True)
            st.progress(rh / 100.0)
            
            st.markdown(f"**Liver Risk**: <span class='{get_risk_class(rl)}'>{rl}%</span>", unsafe_allow_html=True)
            st.progress(rl / 100.0)
        
        with risk_col2:
            st.markdown("**Risk Timeline Trend**")
            timeline_buf = generate_risk_timeline_chart(rk, rh)
            st.image(timeline_buf, use_container_width=True)

