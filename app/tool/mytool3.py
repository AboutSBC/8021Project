from app.tool.base import BaseTool, ToolResult
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
import torch.nn as nn
from transformers import DistilBertModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class DistilBERTClassifier(nn.Module):
    def __init__(self, model_name="distilbert-base-uncased", num_classes=3):
        super().__init__()
        self.distilbert = DistilBertModel.from_pretrained(model_name)
        self.pre_classifier = nn.Linear(self.distilbert.config.hidden_size, self.distilbert.config.hidden_size)
        self.dropout = nn.Dropout(0.2)
        self.classifier = nn.Linear(self.distilbert.config.hidden_size, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.distilbert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        hidden_state = outputs.last_hidden_state[:, 0, :]  # 取[CLS]
        pooled_output = self.pre_classifier(hidden_state)
        pooled_output = nn.ReLU()(pooled_output)
        pooled_output = self.dropout(pooled_output)
        return self.classifier(pooled_output)

distil_model = DistilBERTClassifier().to(device)
# 加载预训练模型和分词器
model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
distil_model.load_state_dict(torch.load('./weight/best_distilbert.pt',map_location=device))

# 映射标签
label_map = {0: "negative", 1: "neutral", 2: "positive"}
def preprocess_text(text, tokenizer, max_length=128):
    """将文本编码为模型输入格式"""
    encoding = tokenizer(
        text,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    return {
        "input_ids": encoding["input_ids"],
        "attention_mask": encoding["attention_mask"]
    }
def predict_single(text, model, tokenizer):
    """单条文本预测"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # 预处理
    inputs = preprocess_text(text, tokenizer)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    # 预测
    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        #logits = outputs.logits
        pred = torch.argmax(outputs, dim=1).item()

    return label_map[pred]

_FIN_SENTIMENT_ANALYSIS_DESCRIPTION = """This tool is used to do sentiment-analysis on financial texts and classify it into three categories, the categories includes positive、negative and neutral"""

class fin_sentiment_anlysis(BaseTool): #类名称，以后要用
    name: str = "Fin-sentiment"
    description: str = _FIN_SENTIMENT_ANALYSIS_DESCRIPTION

    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {
                "description": "Input text is required for financial sentiment analysis.",
                "type": "string"
            }
        },
        "required": ["text"]
    }

    async def execute(self,**kwargs) -> str:  # , plan: str) -> str:  # , status: str) -> str:
        text = kwargs.get('text')
        inputs = preprocess_text(text, tokenizer)
        result = predict_single(text, distil_model, tokenizer)
        result_text = f"预测结果:{result}"
        return ToolResult(output=result_text)
        #return f"The interaction has been completed!!!!!"

