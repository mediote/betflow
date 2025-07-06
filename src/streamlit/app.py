import streamlit as st
import requests
from pathlib import Path

st.set_page_config(page_title="Dialog Analyzer", layout="wide")

# Prepare logo path


# Configuration
API_ENDPOINT = "http://localhost:8080/score"  # Replace if needed
audio_options = [f"dialog_{i}.mp3" for i in range(1, 7)]
prompt_list = ["check_rules"]

# --- Sidebar for User Input ---
st.sidebar.title("Dialog Settings")

# Logo
base_path = Path(__file__).parent
logo_path = base_path / "logo.png"
st.image(str(logo_path), width=200)

selected_audio = st.sidebar.selectbox("Select Audio File:", audio_options)
selected_prompt = st.sidebar.selectbox("Select Actions:", prompt_list)
analyze_button = st.sidebar.button("🔍 Analyze Dialog")

# --- Main Page ---
st.title("Compliance Analyzer - Betflow API")

if analyze_button:
    payload = {
        "audio_file_name": selected_audio,
        "dialogs_container_dir": "dialogs",
        "prompt_list": [selected_prompt],
        "prompt_base_dir": "./prompts",
    }

    with st.spinner("Analyzing audio, please wait..."):
        try:
            response = requests.post(API_ENDPOINT, json=payload)

            if response.status_code == 200:
                result = response.json()
                extracted = result.get("extracted_clausules", {}).get(
                    selected_prompt, {}
                )

                st.success("Analysis completed successfully!")

                # Display results inside one big expander (NO nested expanders)
                with st.expander("🧾 View Detailed Analysis", expanded=True):

                    # --- Compliance Check ---
                    compliance = extracted.get("compliance_check", {})
                    st.subheader("🛡️ Compliance Check")
                    if compliance.get("violated") == "true":
                        st.error("⚠️ Compliance Violation Detected")
                        for violation in compliance.get("violations", []):
                            st.markdown(
                                f"**Violation Rule {violation.get('rule_number')}**"
                            )
                            st.markdown(f"🔹 {violation.get('description')}")
                            st.markdown("---")
                    else:
                        st.success("✅ No compliance violations detected.")

                    # --- Interaction Summary ---
                    summary = extracted.get("interaction_summary", {})
                    st.subheader("📝 Interaction Summary")
                    st.info("Summary of the client and attendant interaction:")
                    st.markdown(
                        f"**Client Intent:** {summary.get('client_intent', 'N/A')}"
                    )
                    st.markdown(
                        f"**Attendant Response:** {summary.get('attendant_response', 'N/A')}"
                    )
                    st.markdown(f"**Context:** {summary.get('context', 'N/A')}")

                    # --- Metadata ---
                    metadata = extracted.get("metadata", {})
                    st.subheader("📚 Metadata")
                    st.caption("Identifiers for tracking the interaction:")
                    st.markdown(
                        f"**Interaction ID:** {metadata.get('interaction_id', 'N/A')}"
                    )
                    st.markdown(
                        f"**Attendant ID:** {metadata.get('attendant_id', 'N/A')}"
                    )
                    st.markdown(f"**Client ID:** {metadata.get('client_id', 'N/A')}")

            else:
                st.error(f"❌ Request failed! Status code: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"❌ Error during request: {str(e)}")

else:
    st.info(
        "Please select an audio and prompt in the sidebar, then click **Analyze Dialog**."
    )
