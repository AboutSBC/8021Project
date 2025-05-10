from app.tool.base import BaseTool, ToolResult
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

documents_path = "./weight/rag_documents.npy"
embeddings_path = "./weight/rag_embeddings.npy"
baseembeddings = np.load(embeddings_path,allow_pickle=True)
basedocuments = np.load(documents_path,allow_pickle=True)

_RAG_DESCRIPTION = """This tool is used to query internal product documentation and retrieve the most contextually relevant text segments."""

class rag(BaseTool): #类名称，以后要用
    name: str = "retrieve"
    description: str = _RAG_DESCRIPTION

    parameters: dict = {
        "type": "object",
        "properties": {
            "text": {
                "description": "The input text of requirements for internal product documentation and retrieve the most contextually relevant text segments.",
                "type": "string"
            }
        },
        "required": ["text"]
    }

    async def execute(self,**kwargs) -> str:  # , plan: str) -> str:  # , status: str) -> str:
        text = kwargs.get('text')
        if text is None:
            raise ValueError("Input text is required for sentiment analysis.")
        query_embedding = model.encode([text])
        similarities = cosine_similarity(query_embedding, baseembeddings)[0]
        most_similar_indices = np.argsort(similarities)[-3:][::-1]
        result = []
        for idx in most_similar_indices:
            temp = ""
            doc = basedocuments[idx]
            temp += f"【相关度: {similarities[idx]:.2f} | 来源: {doc['source']} (页: {doc['page']})】\n"
            temp += doc['text']
            result.append(temp)
        result_text = f"检索结果:{result[0]}"
        return ToolResult(output=result_text)
        #return f"The interaction has been completed!!!!!"

