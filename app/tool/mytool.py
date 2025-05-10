import argparse
import os
import warnings

import numpy as np
import pandas as pd
import torch
from transformers import BertForSequenceClassification, BertTokenizer, logging

from app.tool.base import BaseTool, ToolResult

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
logging.set_verbosity_error()
model_path = "./weight/best_model_state.bin"
# print(os.getcwd())
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=1)
model.load_state_dict(torch.load(model_path, weights_only=True, map_location=device))
model.eval()

model = model.to(device)

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
max_len = 128
_SENTIMENT_ANALYSIS_DESCRIPTION = (
    """This tool performs client's product satisfaction based on the comments."""
)


def preprocess_text(text):
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_len,
        return_token_type_ids=False,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors="pt",
    )
    return encoding


class sentiment_anlysis(BaseTool):  # 类名称，以后要用
    name: str = "sentiment"
    description: str = _SENTIMENT_ANALYSIS_DESCRIPTION

    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {
                "description": "The input text for sentiment analysis.",
                "type": "string",
            }
        },
        "required": ["text"],
    }

    async def execute(
        self, **kwargs
    ) -> str:  # , plan: str) -> str:  # , status: str) -> str:
        text = kwargs.get("text")
        if text is None:
            raise ValueError("Input text is required for sentiment analysis.")
        # 这里需要根据实际情况进行文本预处理，例如分词、向量化等
        # 假设我们已经有一个函数将文本转换为模型输入的张量
        encoding = preprocess_text(text)
        with torch.no_grad():
            output = model(
                input_ids=encoding["input_ids"].to(device),
                attention_mask=encoding["attention_mask"].to(device),
            )
            logits = output.logits
            prediction = logits.squeeze().cpu().numpy()
            predicted_rating = prediction * 9 + 1
            predicted_rating = np.clip(predicted_rating, 1, 10)
            predicted_rating = round(float(predicted_rating), 2)

            result_text = f"客户的情感分数是{predicted_rating}"
        return ToolResult(output=result_text)
        # return f"The interaction has been completed!!!!!"
