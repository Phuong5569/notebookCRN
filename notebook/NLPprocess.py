import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
model_name = "VietAI/vit5-base"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model = T5ForConditionalGeneration.from_pretrained("models/vit5-finetuned")
tokenizer = T5Tokenizer.from_pretrained("models/vit5-finetuned")

def correct_ocr(text):
    inputs = tokenizer("sửa: " + text, return_tensors="pt", max_length=64, truncation=True)
    output = model.generate(inputs.input_ids, max_length=64)
    return tokenizer.decode(output[0], skip_special_tokens=True)
