from openai import OpenAI
import yaml

completion_tokens = prompt_tokens = 0
key_path = "../api_key.yaml"
with open(key_path, "r") as f:
    key_data = yaml.safe_load(f)

client = OpenAI(
        api_key=key_data["api_key"],
    )

def gpt(usr_prompt, model="gpt-3.5-turbo-1106", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list:
    messages = [{"role": "user", "content": usr_prompt}]
    global completion_tokens, prompt_tokens
    outputs = []
    global client
    completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
    outputs = completion.choices[0].message.content
    completion_tokens += completion.usage.completion_tokens
    prompt_tokens += completion.usage.prompt_tokens
    return outputs
    
def gpt_usage():
    global completion_tokens, prompt_tokens
    cost = completion_tokens / 1000 * 0.002 + prompt_tokens / 1000 * 0.001
    return {"completion_tokens": completion_tokens, "prompt_tokens": prompt_tokens, "cost": cost}
