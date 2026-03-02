# 🤖 PEP 8 Code Review Agent

An AI-powered tool that automatically reviews Python code against PEP 8 standards and adds inline comments highlighting violations - WITHOUT modifying your original code.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- ✅ **Safe Code Review** - Only adds comments, never modifies your code
- ✅ **Live Streaming** - Watch AI add comments in real-time
- ✅ **RAG-Powered** - Uses official PEP 8 documentation via vector search
- ✅ **Batch Processing** - Review multiple files or entire folders
- ✅ **Detailed Reports** - Summary statistics and downloadable results
- ✅ **Zero Hallucination Risk** - Original code preserved character-by-character

---

## 🎯 What It Does

### Input (Your Code):
```python
def CalculateTotal(items):
    total=0
    for item in items:
        total+=item['price']
    return total
```

### Output (Code with Comments):
```python
# PEP8: Function name should be 'calculate_total' (snake_case)
# PEP8: Missing docstring
def CalculateTotal(items):
    # PEP8: Add spaces around '=' operator (should be 'total = 0')
    total=0
    for item in items:
        # PEP8: Add spaces around '+=' operator
        total+=item['price']
    return total
```

**Your original code stays 100% intact! ✅**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download the project:**
```bash
cd Desktop
git clone <your-repo-url>
cd pep8-agent
```

2. **Create virtual environment:**
```bash
# Windows
py -3.11 -m venv venv
venv\Scripts\activate

# macOS/Linux
python3.11 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up OpenAI API key:**

Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

---

## 🎮 Usage

### Run the Web Application
```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Interface

1. **Upload Files**
   - Choose individual `.py` files, or
   - Upload a `.zip` folder containing your Python project

2. **Start Review**
   - Click "🚀 Start Review & Add Comments"
   - Watch live as AI analyzes code and adds comments

3. **Download Results**
   - Download summary report
   - Download all commented files as ZIP

---

## 📁 Project Structure
```
pep8-agent/
├── app/
│   ├── __init__.py         # Package initializer
│   ├── agent.py            # AI agent with streaming support
│   ├── rag.py              # RAG system for PEP 8 rules
│   └── main.py             # Streamlit web interface
├── data/
│   └── pep8_rules.txt      # Official PEP 8 documentation
├── venv/                   # Virtual environment (not in git)
├── .env                    # API keys (not in git)
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🛠️ Technical Details

### Architecture
```
┌─────────────┐
│  User Code  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  RAG System │ ← Retrieves relevant PEP 8 rules
│   (FAISS)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ GPT-4o-mini │ ← Generates inline comments
│   (OpenAI)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Commented   │ ← Original code + PEP 8 comments
│    Code     │
└─────────────┘
```

### Technology Stack

- **Backend:** Python 3.11
- **AI Model:** OpenAI GPT-4o-mini
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **Frontend:** Streamlit
- **Embeddings:** OpenAI text-embedding-3-small

---

## 📋 Requirements
```txt
# Core
python-dotenv==1.0.0
requests==2.31.0

# AI
openai==1.57.4

# Vector Database
faiss-cpu==1.7.4
numpy==1.24.3

# Web UI
streamlit==1.28.0
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Supported Python Versions

- ✅ Python 3.11 (Recommended)
- ✅ Python 3.10
- ⚠️ Python 3.12+ (May have dependency issues)

---

## 💡 Example Use Cases

### For Team Leads
- Quickly review code from team members
- Ensure PEP 8 compliance before merging
- Educate developers on best practices

### For Developers
- Learn PEP 8 standards by seeing violations in your code
- Prepare code for production deployment
- Self-review before submitting pull requests

### For Students
- Understand Python coding standards
- Improve code quality
- Learn best practices

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution:** Make sure you're running from the project root and `app/__init__.py` exists.

### Issue: `OPENAI_API_KEY not found`
**Solution:** Create `.env` file with your API key in the project root.

### Issue: Streamlit won't start
**Solution:** 
```bash
pip uninstall streamlit pyarrow pandas -y
pip install streamlit
```

### Issue: `faiss-cpu` installation fails
**Solution:** Make sure you're using Python 3.11, not 3.12+

---

## 📊 Performance

- **Speed:** ~5-10 seconds per file (depends on file size)
- **Accuracy:** Uses official PEP 8 documentation via RAG
- **Cost:** ~$0.001-0.005 per file review (OpenAI API costs)

---

## 🔒 Safety & Privacy

- ✅ Code is sent to OpenAI API for analysis
- ✅ Original code is NEVER modified
- ✅ No code is stored permanently
- ✅ API calls are encrypted (HTTPS)

**Note:** For sensitive/proprietary code, consider:
- Using a local LLM instead of OpenAI
- Running in an air-gapped environment
- Reviewing OpenAI's data usage policies

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [PEP 8](https://peps.python.org/pep-0008/) - Python Enhancement Proposal 8
- [OpenAI](https://openai.com/) - GPT-4o-mini API
- [Streamlit](https://streamlit.io/) - Web framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search

---

## 📞 Support

Having issues? 

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Contact: [jothireddy939@gmail.com]

---

## 🗺️ Roadmap

- [ ] Support for more Python linters (pylint, flake8)
- [ ] Custom rule configuration
- [ ] VS Code extension
- [ ] Team collaboration features
- [ ] Historical review tracking
- [ ] Azure DevOps integration

---

## 📈 Changelog

### Version 1.0.0 (2025-01-XX)
- Initial release
- Live streaming comment insertion
- RAG-powered PEP 8 analysis
- Batch file processing
- Summary reports

---

Made with ❤️ for better Python code