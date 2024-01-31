import ray
from ray import serve
import transformers
from fastapi import FastAPI, Request
import requests
app = FastAPI()

@serve.deployment
class LLMInferenceServer:
    def __init__(self):
        model_id = "EleutherAI/gpt-j-6B"
        revision = "float16"
        self.model = transformers.AutoModelForCausalLM.from_pretrained(model_id, revision=revision)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_id)

    async def __call__(self, request: Request):
        input_text = await request.json()
        inputs = self.tokenizer(input_text['input_text'], return_tensors="pt")
        outputs = self.model.generate(**inputs)
        generated_text = self.tokenizer.decode(outputs[0])
        return {
            "generated_text": generated_text
        }

@app.post("/generate_text")
async def generate_text_endpoint(request: Request):
    return await LLMInferenceServer.__call__(request)

if __name__ == "__main__":
    ray.init()
    serve.start(detached=True)
    LLMInferenceServer.deploy()
    serve.run(app)
# Test the inference server
response = requests.post("http://127.0.0.1:8000/generate_text", json={"input_text": "Hello, Ionet!"})
print(response.json())