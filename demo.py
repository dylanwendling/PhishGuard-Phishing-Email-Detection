#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Download from the correct community repository
print("Downloading GGUF model...")
model_path = hf_hub_download(
    repo_id="bartowski/SmolLM2-135M-Instruct-GGUF",
    filename="SmolLM2-135M-Instruct-Q4_K_M.gguf" 
)

# 2. Load the model into the lightweight Llama engine
print("Loading model...")
llm = Llama(
    model_path=model_path,
    n_ctx=2048, 
    verbose=False 
)

# 3. Ask it a question
print("Generating text...\n" + "-"*30)
response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant for a video game."},
        {"role": "user", "content": "Write a short, cryptic note left behind by a frightened scientist."}
    ],
    max_tokens=50,
    temperature=0.7
)

# 4. Print the result
print(response["choices"][0]["message"]["content"])


# In[ ]:




