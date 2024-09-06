import streamlit as st
import base64
import requests
import components
from utils import show_code


def submit(image, api_key):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    base64_image = base64.b64encode(image).decode("utf-8")

    payload = {
       "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
                        You are assisting an NCAA athlete to determine if a supplement is safe for consumption under NCAA regulations. Your job is to analyze the supplement’s label, extract all listed ingredients, and check for compliance with NCAA banned substances and regulations. Additionally, check for a third-party tested certification on the label.

                        Instructions:
                        1. Extract Ingredients:
                            - Extract all visible ingredients from the supplement label.
                            
                        2. Compare Ingredients to the Following NCAA-Banned Substance Categories:
                            - **Stimulants**: Amphetamine, Caffeine (Guarana), Cocaine, Ephedrine, Methamphetamine, Modafinil, and other stimulants listed.
                            - **Anabolic Agents**: Testosterone, Androstenedione, Boldenone, Clenbuterol, SARMs, etc.
                            - **Beta Blockers**: Atenolol, Metoprolol, Propranolol (banned for rifle athletes only).
                            - **Diuretics and Masking Agents**: Bumetanide, Furosemide, Hydrochlorothiazide, etc.
                            - **Narcotics**: Fentanyl, Hydrocodone, Methadone, Morphine, etc.
                            - **Peptide Hormones and Growth Factors**: HGH, EPO, IGF-1, etc.
                            - **Hormone and Metabolic Modulators**: Aromatase inhibitors, SERMs like Clomid, Tamoxifen, etc.
                            - **Beta-2 Agonists**: Albuterol, Formoterol, Salmeterol, etc.
                            - Flag any ingredient that is chemically or pharmacologically related to the above classes, even if not explicitly listed on the label.

                        3. Check for a Third-Party Tested Label:
                            - Look for a third-party tested label or certification that confirms the supplement has undergone independent testing for banned substances. Common third-party labels include NSF Certified for Sport, Informed-Choice, or other recognized testing bodies.
                            - If the third-party tested certification is found, inform the user. If not found, advise the user that the supplement may not be certified as safe from contamination with banned substances.

                        4. Provide Feedback:
                            - If ingredients are detected that match any banned substance class, **warn** the user that the supplement may not be safe for consumption under NCAA rules and advise them to consult their athletic department.
                            - If no banned ingredients are found, but the label is unclear or incomplete, instruct the user to verify the product with their athletic department before use, as contamination is still possible.

                        5. Fallback for Unreadable Labels:
                            - If the label is **unclear** or difficult to read (for example, blurry or partially obstructed), respond with:
                                "The label on this supplement is difficult to read. Please retake the image, ensuring the label is clear and fully visible, or manually check the ingredients with your athletic department."
                            - If you cannot confidently determine the ingredients due to poor image quality, notify the user:
                                "We are unable to determine the ingredients from this image. Please retake the photo or consult with your athletic department for further guidance."

                        ### Important Notes:
                        - Supplements may be contaminated with banned substances not listed on the label. If the product is not third-party tested, or if any uncertainty arises, advise the athlete to consult their athletic department.
                        - Supplements are taken at the athlete’s own risk, and the NCAA does not approve any dietary supplements.
                        - There is no complete list of banned substances. Err on the side of caution when reviewing ingredients.
                        - Provide feedback if a third-party certification is present or missing.
                        - After identifying any ingredients, provide feedback on whether the supplement may contain NCAA-banned substances based on the label.
                     """},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()

        camera_caption = response.json()["choices"][0]["message"]["content"]
        st.session_state.camera_caption = camera_caption

        if "balloons" in st.session_state and st.session_state.balloons:
            st.balloons()

    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error: {err}")
    except Exception as err:
        st.error(f"Error: {err}")


def run():
    selected_option = st.radio(
        "Image Input",
        ["Camera", "Image File"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if selected_option == "Camera":
        image = components.camera_uploader()
    else:
        image = components.image_uploader()

    api_key = components.api_key_with_warning()

    components.submit_button(image, api_key, submit)

    if "camera_caption" in st.session_state:
        st.markdown(st.session_state.camera_caption)


st.set_page_config(page_title="Supplement Scanner", page_icon="💊")
components.inc_sidebar_nav_height()
st.write("# 📷 Camera")
st.write("Take a clear photo or upload a photo of the supplement you'd like to scan")
st.info(
    "This is a MVP proof of concept for a supplement scanner and all responses should be double checked to ensure accuracy."
)

run()

components.toggle_balloons()
show_code([submit, run, components])
