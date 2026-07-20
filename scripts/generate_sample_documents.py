import os

DOCUMENTS = [
    {
        "filename": "cnc_maintenance_report.txt",
        "content": "Maintenance Action: Replaced spindle bearings on CNC milling machine due to excessive vibration.\nThe process duration was 2.5 hours. Bearing wear caused excessive vibration.\nA vibration sensor monitors the conveyor motor."
    },
    {
        "filename": "welding_specs.txt",
        "content": "The welding machine consumes stainless steel and operates at 1200 degrees Celsius.\nThe welding process uses a laser."
    },
    {
        "filename": "quality_inspection_01.txt",
        "content": "Surface defect detected on aluminum casing. The defect was caused by a dull carbide cutting tool in the lathe.\nMeasurement: 5 mm deviation."
    }
]

def generate_documents(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    for i, doc in enumerate(DOCUMENTS):
        # We duplicate them a bit to reach 20 documents if needed, but let's just make 20 variations
        for j in range(7):
            idx = (i * 7) + j
            if idx >= 20: break
            
            fname = f"{doc['filename'].split('.')[0]}_{idx}.txt"
            path = os.path.join(output_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Document ID: {idx}\n")
                f.write(doc["content"])

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "data", "sample_documents")
    generate_documents(out_dir)
    print(f"Generated sample documents in {out_dir}")
