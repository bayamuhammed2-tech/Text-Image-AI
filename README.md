# 🚀 AI Canvas Studio

AI Canvas Studio is a polished Streamlit text-to-image generator powered by Hugging Face's Stable Diffusion XL. Write a vivid prompt, send it securely to the Hugging Face Serverless Inference API, and turn your imagination into artwork without downloading large machine learning weights locally.

## 📝 Description

This project provides a lightweight AI art web app built for easy local development and simple Streamlit Community Cloud deployment. The app uses the `stabilityai/stable-diffusion-xl-base-1.0` model through Hugging Face's hosted API, keeping server memory usage low while still producing high-quality generated images.

## 🛠️ Tech Stack

- Python
- Streamlit
- Requests
- Pillow
- Hugging Face API

## 📦 Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/ai-canvas-studio.git
cd ai-canvas-studio
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app locally:

```bash
streamlit run app.py
```

## 🔑 Environment Configuration

The app reads your Hugging Face access token from Streamlit Secrets using:

```python
st.secrets["HF_TOKEN"]
```

For local development, create a `.streamlit/secrets.toml` file:

```toml
HF_TOKEN = "your_hugging_face_access_token"
```

The `.gitignore` file is configured to prevent `.streamlit/secrets.toml` from being committed, keeping your token private.

## 🚀 Deployment

To deploy on Streamlit Community Cloud:

1. Push this project to a GitHub repository.
2. Open Streamlit Community Cloud and create a new app from your repository.
3. Set the main file path to `app.py`.
4. Add `HF_TOKEN` in the app's Secrets settings.
5. Deploy and start generating artwork in the browser.

---

Built with Streamlit and Hugging Face for lightweight, creative AI image generation.
