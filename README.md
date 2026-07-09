# ResumeInt

<p align="center">
  <img src="ResumeInt.jpeg" alt="ResumeInt logo" width="220" />
</p>

<p align="center">
  <strong>An NLP-powered resume screener for comparing candidates against job descriptions.</strong>
</p>

ResumeInt analyzes resumes using sentence embeddings, cosine similarity, and automated skill extraction. It supports both single-resume analysis and batch candidate ranking through a custom Streamlit interface.

## Features

- **Single Resume Analysis** — compare one resume with a job description and receive an overall similarity score.
- **Batch Resume Ranking** — upload multiple resumes and rank candidates by semantic similarity.
- **Skill Gap Analysis** — identify matched skills, missing skills, and the overall skill-match rate.
- **Multiple File Formats** — upload resumes as PDF, DOCX, or TXT files.
- **Visual Reports** — view score charts, skill breakdowns, category coverage, and candidate leaderboards.
- **Desktop Support for macOS** — launch the Streamlit app inside a native desktop window.
- **Privacy-Friendly Workflow** — resume processing runs locally on your machine.

## How It Works

1. Paste a job description into the app.
2. Upload one resume or a batch of resumes.
3. ResumeInt extracts text from each document.
4. Sentence embeddings are generated for the resume and job description.
5. Cosine similarity is used to calculate a semantic match score.
6. Skills are extracted and compared to show matched and missing requirements.
7. Results are displayed as scores, charts, and ranked candidate summaries.

## Tech Stack

- Python 3.10+
- Streamlit
- Sentence Transformers
- PyTorch
- scikit-learn
- spaCy
- PDFPlumber
- python-docx
- Pandas
- Plotly
- PyWebView for the optional macOS desktop wrapper

## Project Structure

```text
resume-screener/
├── app.py                 # Main Streamlit application
├── desktop.py             # Native macOS desktop launcher
├── build_app.py           # Builds the ResumeInt.app bundle
├── generate_icon.py       # Generates the macOS application icon
├── requirements.txt       # Python dependencies
├── setup.sh               # Conda setup script
├── ResumeInt.jpeg         # Project logo/image
├── data/
│   └── skills_db.py       # Skill categories and skill database
└── src/
    ├── pdf_parser.py      # PDF, DOCX, and TXT text extraction
    ├── skill_extractor.py # Skill extraction and overlap analysis
    └── embeddings.py      # Similarity scoring and resume ranking
```

## Installation

### Option 1: Use the setup script

Make sure Conda is installed, then run:

```bash
chmod +x setup.sh
./setup.sh
```

Activate the environment if needed:

```bash
conda activate resume-screener
```

### Option 2: Install manually

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Run the Web App

```bash
streamlit run app.py
```

Streamlit will open the application in your browser. By default, it is usually available at:

```text
http://localhost:8501
```

## Using ResumeInt

### Single Resume Mode

1. Select **Single Resume**.
2. Paste the job description.
3. Upload a PDF, DOCX, or TXT resume.
4. Review:
   - semantic similarity score
   - skill-match percentage
   - matched skills
   - missing skills
   - category coverage
   - extracted resume text

### Batch Ranking Mode

1. Select **Batch Ranking**.
2. Paste the job description.
3. Upload multiple resumes.
4. Review:
   - ranked candidates
   - similarity scores
   - average similarity
   - number of strong matches
   - top-candidate skill breakdown

## Optional: Run as a macOS Desktop App

The desktop wrapper uses PyWebView to launch Streamlit inside a native macOS window.

Install the additional desktop dependency:

```bash
pip install pywebview
```

Run the desktop launcher:

```bash
python desktop.py
```

The desktop app starts Streamlit on port `8502` and opens it in a native Cocoa window.

## Build the macOS App Bundle

The included build script creates `ResumeInt.app` inside `~/Applications`.

Before running it, check the paths near the top of `build_app.py` and update them for your machine:

```python
PROJ = os.path.expanduser("~/resume-screener")
PYTHON = os.path.expanduser("~/miniconda3/envs/resume-screener/bin/python")
```

Then run:

```bash
python build_app.py
```

To generate the `.icns` icon first, install Pillow and run:

```bash
pip install pillow
python generate_icon.py
```

> Note: `generate_icon.py` currently contains a machine-specific output path. Update the `out` variable before running it on another computer.

## Notes

- The first sentence-transformer model load may take longer because model files may need to be downloaded.
- Resume quality, formatting, and the wording of the job description can affect match scores.
- Similarity scores should support human review, not replace it. Hiring decisions should consider experience, achievements, context, and fair evaluation practices.
- The current `requirements.txt` covers the main Streamlit application. Install `pywebview` for desktop mode and `Pillow` for icon generation.

## Future Improvements

- Export reports as CSV or PDF
- Add configurable scoring weights
- Support custom skill dictionaries
- Add resume anonymization
- Improve explainability for similarity scores
- Add Docker support
- Add automated tests and CI

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, make your changes, and open a pull request.

```bash
git checkout -b feature/your-feature-name
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

## License

No license has been added yet. Add a `LICENSE` file before distributing or accepting external contributions.

---

<p align="center">Built with Python, NLP, and Streamlit.</p>
