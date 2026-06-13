from io import BytesIO
from typing import Any

import requests
import streamlit as st
from PIL import Image, UnidentifiedImageError


HF_MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"
REQUEST_TIMEOUT_SECONDS = 180


st.set_page_config(
    page_title="Canvas Forge",
    page_icon="🎨",
    layout="centered",
)


st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #f7f4ef 0%, #edf6f9 45%, #f8f9fb 100%);
        }
        .main .block-container {
            max-width: 780px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }
        h1 {
            text-align: center;
            letter-spacing: 0;
        }
        .subtitle {
            color: #475569;
            font-size: 1.08rem;
            line-height: 1.6;
            margin: 0 auto 1.75rem auto;
            max-width: 680px;
            text-align: center;
        }
        .hint {
            color: #64748b;
            font-size: 0.92rem;
            line-height: 1.45;
            margin-top: -0.5rem;
            margin-bottom: 1rem;
        }
        div.stButton > button {
            border-radius: 0.5rem;
            font-weight: 700;
            min-height: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_hf_token() -> str | None:
    """Read the Hugging Face token from Streamlit secrets without exposing it."""
    try:
        token = st.secrets["HF_TOKEN"]
    except KeyError:
        return None
    except Exception as exc:
        if exc.__class__.__name__ == "StreamlitSecretNotFoundError":
            return None
        raise

    token = str(token).strip()
    return token or None


def parse_error_message(response: requests.Response) -> str:
    """Extract a helpful error message from a Hugging Face API response."""
    try:
        payload: dict[str, Any] = response.json()
    except ValueError:
        return response.text.strip() or "The image service returned an unexpected error."

    error = payload.get("error")
    if isinstance(error, list):
        return " ".join(str(item) for item in error)
    if error:
        return str(error)

    return payload.get("message", "The image service returned an unexpected error.")


def generate_image(prompt: str, token: str) -> Image.Image:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "image/png",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        },
        "options": {
            "wait_for_model": True,
            "use_cache": False,
        },
    }

    response = requests.post(
        HF_API_URL,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    content_type = response.headers.get("content-type", "").lower()

    if response.status_code == 401:
        raise RuntimeError(
            "Your Hugging Face token was rejected. Check that `HF_TOKEN` is set correctly "
            "in Streamlit secrets."
        )
    if response.status_code == 403:
        raise RuntimeError(
            "Access was denied. Make sure your Hugging Face token has permission to use "
            "the Inference API and that you have accepted the model terms if required."
        )
    if response.status_code == 429:
        raise RuntimeError(
            "The Hugging Face API rate limit was reached. Please wait a moment and try again."
        )
    if response.status_code in {502, 503, 504}:
        raise RuntimeError(
            "The image model is currently busy or starting up. Please try again in a minute."
        )
    if not response.ok:
        raise RuntimeError(parse_error_message(response))

    if "image" not in content_type:
        raise RuntimeError(parse_error_message(response))

    try:
        image = Image.open(BytesIO(response.content))
        image.load()
    except UnidentifiedImageError as exc:
        raise RuntimeError("The API response could not be decoded as an image.") from exc

    return image


st.title("Canvas Forge")
st.markdown(
    '<p class="subtitle">Describe a scene, mood, material, lighting style, or impossible '
    "idea. Stable Diffusion XL will turn your prompt into artwork using Hugging Face's "
    "serverless inference API.</p>",
    unsafe_allow_html=True,
)

prompt = st.text_area(
    "Artwork prompt",
    placeholder=(
        "Example: A cinematic portrait of an astronaut botanist tending glowing orchids "
        "inside a glass greenhouse on Mars, soft volumetric light, ultra detailed"
    ),
    height=180,
)
st.markdown(
    '<p class="hint">Tip: richer prompts usually work best when they include subject, setting, '
    "style, lighting, mood, and detail level.</p>",
    unsafe_allow_html=True,
)

generate_clicked = st.button(
    "Generate Artwork",
    type="primary",
    use_container_width=True,
)

if generate_clicked:
    clean_prompt = prompt.strip()

    if not clean_prompt:
        st.error("Please enter a prompt before generating artwork.")
    else:
        hf_token = get_hf_token()

        if hf_token is None:
            st.error(
                "Missing Hugging Face token. Add `HF_TOKEN` to your Streamlit secrets before "
                "generating images."
            )
        else:
            try:
                with st.spinner("Drawing your artwork with Stable Diffusion XL..."):
                    artwork = generate_image(clean_prompt, hf_token)
            except requests.exceptions.Timeout:
                st.error(
                    "The request timed out while the model was generating. Try again with the "
                    "same prompt in a moment."
                )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the Hugging Face API. Check your connection and try again."
                )
            except requests.exceptions.RequestException as exc:
                st.error(f"The image request failed: {exc}")
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.success("Artwork generated successfully.")
                st.image(artwork, caption=clean_prompt, use_container_width=True)
