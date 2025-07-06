# 🧠 LLM Streamlit App

This project launches a local Large Language Model (LLM) container and a Streamlit frontend for interaction.

---

## 🧰 Environment Setup

### ▶️ Python Virtual Environment

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
```

> 💡 Use `.\.venv\Scriptsctivate.bat` if you're using CMD.

---

## 🐳 Start the LLM Container

Make sure Docker is running, then:

```bash
docker compose up --build
```

---

## 🚀 Launch the Streamlit App

```bash
streamlit run src/streamlit/app.py
```