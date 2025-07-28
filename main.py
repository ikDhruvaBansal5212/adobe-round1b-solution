import os
import json
import fitz  # PyMuPDF
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if len(text.strip()) < 20:
            continue
        sections.append({
            "document": os.path.basename(pdf_path),
            "page_number": page_num,
            "text": text.strip()
        })
    return sections

def load_persona_and_job(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    persona = data["persona"]
    job = data["job_to_be_done"]
    return persona, job

def rank_sections(sections, persona, job, model):
    prompt = f"{persona}. Task: {job}"
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    for section in sections:
        section_embedding = model.encode(section["text"], convert_to_tensor=True)
        score = util.cos_sim(prompt_embedding, section_embedding).item()
        section["score"] = score
    sections.sort(key=lambda x: x["score"], reverse=True)
    return sections

def generate_output(sections, persona, job):
    top_sections = sections[:5]
    metadata = {
        "input_documents": list(set(sec["document"] for sec in sections)),
        "persona": persona,
        "job_to_be_done": job,
        "timestamp": datetime.now().isoformat()
    }
    extracted_sections = [{
        "document": sec["document"],
        "page_number": sec["page_number"],
        "section_title": sec["text"].split("\n")[0][:80],
        "importance_rank": idx + 1
    } for idx, sec in enumerate(top_sections)]

    sub_section_analysis = [{
        "document": sec["document"],
        "page_number": sec["page_number"],
        "refined_text": sec["text"][:500] + "..." if len(sec["text"]) > 500 else sec["text"]
    } for sec in top_sections]

    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "sub_section_analysis": sub_section_analysis
    }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    persona_file = os.path.join(input_dir, "persona_job.json")

    persona, job = load_persona_and_job(persona_file)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    all_sections = []
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            sections = extract_sections_from_pdf(pdf_path)
            all_sections.extend(sections)

    ranked = rank_sections(all_sections, persona, job, model)
    result = generate_output(ranked, persona, job)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "results.json"), "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
