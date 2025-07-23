from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms import huggingface_hub
from langchain_community.llms import HuggingFacePipeline


model_id = "microsoft/phi-3-mini-4k-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
llm = HuggingFacePipeline(pipeline=pipe)
