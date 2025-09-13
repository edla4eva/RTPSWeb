import logging
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
from peft import LoraConfig, get_peft_model

# CONFIG
MODEL_NAME = "google/flan-t5-small" 
TRAIN_FILE = "train.jsonl"            
OUTPUT_DIR = "./flan_t5_lora_output"  
# Logging
logging.basicConfig(level=logging.INFO)
#  Load tokenizer + base model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
# Apply LoRA adapter
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q", "v"], 
    lora_dropout=0.05,
    bias="none",
    task_type="SEQ_2_SEQ_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Load dataset
dataset = load_dataset("json", data_files=TRAIN_FILE)
# Preprocessing / Tokenization
max_input_length = 256
max_target_length = 128

def preprocess(examples):
    inputs = examples["instruction"]
    targets = examples["output"]

    model_inputs = tokenizer(
        inputs, max_length=max_input_length, truncation=True, padding="max_length"
    )
    labels = tokenizer(
        targets, max_length=max_target_length, truncation=True, padding="max_length"
    )

    # Replace pad token with -100 (ignored in loss)
    labels["input_ids"] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label]
        for label in labels["input_ids"]
    ]
    model_inputs["labels"] = labels["input_ids"]

    return model_inputs

tokenized = dataset["train"].map(
    preprocess, batched=True, remove_columns=dataset["train"].column_names
)
# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
#  Training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    save_total_limit=2,
    fp16=False,  # set True if your GPU supports mixed precision
    logging_steps=50,
    save_strategy="epoch",
    remove_unused_columns=False,
)
# 8) Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train
trainer.train()
# 10) Save adapter + tokenizer
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"Fine-tuned model saved in {OUTPUT_DIR}")

