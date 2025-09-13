from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# ----------------------------------------------------
# 1) Load fine-tuned model + tokenizer
# ----------------------------------------------------
MODEL_DIR = "./flan_t5_lora_output"   # same directory used in training

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# ----------------------------------------------------
# 2) Example input (CSV correction test)
# ----------------------------------------------------
instruction = """
Compare these two CSV records and correct any mistake in the matriculation number.

CSV1: Name=John Doe, MatricNo=2021001
CSV2: Name=John Doe, MatricNo=2021010
"""

# ----------------------------------------------------
# 3) Run inference
# ----------------------------------------------------
inputs = tokenizer(instruction, return_tensors="pt", truncation=True).to(device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.3,
        do_sample=False
    )

result = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("🔎 Instruction:", instruction)
print("✅ Model output:", result)
