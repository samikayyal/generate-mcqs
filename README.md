# Generate MCQs

Generate multiple choice questions from documents using Google's Gemini API, then take a quiz via a Flask web app.

## Setup

1. Install dependencies:

```bash
pip install -e .
```

2. Set your Gemini API key:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY = "your-api-key-here"

# Linux/macOS
export GOOGLE_API_KEY="your-api-key-here"
```

Get your API key from: <https://aistudio.google.com/apikey>

## Usage

### Step 1: Generate MCQs from documents

```bash
python main.py <file_path> [file_path2 ...] [-n num_questions]
```

Examples:

```bash
python main.py document.pdf                     # Generate 10 questions (default)
python main.py document.pdf -n 15               # Generate 15 questions from a PDF
python main.py notes.txt                        # Generate 10 questions from text file
python main.py lecture.md -n 20                 # Generate 20 questions from markdown
python main.py slides.pptx -n 15                # Generate 15 questions from PowerPoint
python main.py doc1.pdf doc2.pdf notes.txt      # Combine multiple files
python main.py ch1.pdf ch2.pdf ch3.pdf -n 30    # 30 questions from 3 PDFs
```

Supported file types: PDF, PPTX, TXT, Markdown, HTML, JSON, XML, CSV, Python, JavaScript, TypeScript

### Step 2: Take the quiz

```bash
python app.py
```

Open <http://localhost:5000> in your browser to start the quiz.

## Database

Questions are stored in `mcqs.db` (SQLite) with this structure:

- **questions**: `question_id`, `text`
- **options**: `option_id`, `question_id`, `text`, `is_correct`

## Features

- Uses Gemini 2.5 Flash with structured output for reliable JSON responses
- Well-crafted prompt for high-quality MCQs without explanations
- Clean, responsive quiz interface
- Shows correct answer after each question
- Final results summary with score
