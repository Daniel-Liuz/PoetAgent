# E:\Program\poetry_project\ai_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# --- 配置 ---
# 你的模型路径
MODEL_PATH = "E:/Program/7B"
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {DEVICE}")

# --- 初始化 Flask 应用 ---
app = Flask(__name__)
CORS(app)  # 允许跨域请求，方便 Django 调用

# --- 加载模型和分词器 (在服务启动时加载一次) ---
print("Loading model, please wait...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype=torch.bfloat16).to(DEVICE)
model = model.eval()
print("Model loaded successfully.")


# --- API 端点 ---
@app.route('/get_ai_critique', methods=['POST'])
def get_ai_critique():
    try:
        data = request.get_json()
        if not data or 'poem' not in data:
            return jsonify({'error': 'Missing "poem" in request body'}), 400

        poem_text = data['poem']

        # --- Prompt 工程：构建给模型的指令 ---
        prompt = f"请以一位文学评论家的身份，从意境、修辞、情感和格律（如果有）几个方面，深入分析以下这首诗的优缺点，并给出改进建议。请分点论述，语言优美，富有洞察力。\n\n诗歌原文：\n{poem_text}\n\n我的评论是："

        messages = [{'role': 'user', 'content': prompt}]
        inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(DEVICE)

        outputs = model.generate(
            inputs,
            max_new_tokens=512,  # 评论长度
            do_sample=True,
            top_p=0.95,
            temperature=0.8,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id
        )

        response_text = tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)

        return jsonify({'critique': response_text.strip()})

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500


# --- 启动服务 ---
if __name__ == '__main__':
    # 使用一个与 Django 不同的端口，例如 5001
    app.run(host='0.0.0.0', port=5001, debug=False)
