# Adobe Round 1B – Persona-Based Document Analyzer

## 🚀 Description
This tool processes a collection of PDFs and ranks the most relevant sections based on a given persona and their job-to-be-done.

## 🔢 Features
- Semantic similarity using Sentence Transformers
- Extracts top N relevant sections
- Produces structured output in JSON
- Runs offline inside Docker

## 📥 Input Files
- `input/persona_job.json`:
```json
{
  "persona": "PhD Researcher",
  "job_to_be_done": "Prepare a literature review on GNN methods"
}
```
- `input/*.pdf`: Your documents

## 📤 Output
`output/results.json` containing:
- Metadata
- Ranked extracted sections
- Sub-section analysis

## 🐳 How to Run

### Build Docker Image
```bash
docker build --platform linux/amd64 -t round1b-solution .
```

### Run the Container
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none round1b-solution
```

## ✅ Constraints Met
- CPU-only, AMD64
- Offline only (no network)
- Model size < 1GB
- < 60s runtime for 3–5 PDFs
