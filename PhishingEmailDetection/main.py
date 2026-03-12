import email
from email import policy
import re
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Download the GGUF model
print("Downloading GGUF model...")
model_path = hf_hub_download(
    repo_id="bartowski/SmolLM2-135M-Instruct-GGUF",
    filename="SmolLM2-135M-Instruct-Q4_K_M.gguf"
)

# 2. Load the model into the Llama engine
print("Loading model...")
llm = Llama(
    model_path=model_path,
    n_ctx=2048,
    chat_format="chatml",
    verbose=False
)

def run_phishguard_model(email_filepath):
    print(f"Opening email: {email_filepath}")
    
    # --- A. Parse the .eml file ---
    with open(email_filepath, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    subject = msg.get('subject', 'No Subject')
    sender = msg.get('from', 'Unknown Sender')
    body_part = msg.get_body(preferencelist=('plain'))
    email_text = body_part.get_content() if body_part else "No readable text found."

    # --- B. Heuristic Scoring ---
    score = 0
    triggered_rules = []
    text_to_search = (subject + "  " + email_text).lower()

    # Rule 1: Urgency Phrases
    urgency_keywords = ['urgent', 'immediately', 'suspended', '24 hours', 'verify your identity', 'locked']
    found_urgency = [word for word in urgency_keywords if word in text_to_search]
    if found_urgency:
        score += 35
        triggered_rules.append(f"Urgency phrases detected: {', '.join(found_urgency)}")

    # Rule 2: Suspicious Sender Formatting (Numbers in name)
    if re.search(r'[0-9]', sender):
        score += 25
        triggered_rules.append("Sender email contains suspicious numbers (Possible spoofing)")

    # Rule 3: Link Extraction & Domain Mismatch
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_text)
    if urls:
        sender_domain = sender.split('@')[-1].strip(' >') if '@' in sender else ""
        for url in urls:
            if sender_domain and sender_domain not in url:
                score += 35
                triggered_rules.append(f"Link domain mismatch detected: {url}")
                break

    # Cap limits
    if score == 0:
        score = 5
    elif score > 99:
        score = 99

    # --- C. AI Analysis ---
    print("Analyzing email with SmolLM2...\n" + "-"*30)
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a cybersecurity AI. Analyze this email text for phishing. Briefly explain if it is safe or suspicious."},
            {"role": "user", "content": f"Analyze this email:\n\n{email_text[:1000]}"}
        ],
        max_tokens=200,
        temperature=0.2,
        repeat_penalty=1.1,
        stop=["<|im_end|>", "*", "\n\n\n"]
    )

    ai_result = response["choices"][0]["message"]["content"]

    # --- D. Return the data to Flask ---
    return {
        "score": score,
        "rules": triggered_rules if triggered_rules else ["No heuristic rules triggered. Email appears clean."],
        "explanation": ai_result
    }