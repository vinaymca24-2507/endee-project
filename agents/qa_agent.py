from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
# from langchain.chains import LLMChain # Deprecated
from core.retriever import retriever
from core.llm import get_llm

QA_TEMPLATE = """
You are a Senior Architect explaining a codebase. Use the following context to answer the question. 
If the answer is not in the context, say so. Do not hallucinate code.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

class QAAgent:
    def __init__(self):
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=QA_TEMPLATE
        )
        # self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.chain = self.prompt | self.llm

    def ask(self, question: str) -> str:
        # 1. Retrieve context
        results = retriever.search(question, top_k=5)
        context_str = "\n\n".join([f"File: {r['file_path']}\nCode:\n{r['content']}" for r in results])
        
        # 2. Answer
        try:
            # response = self.chain.run(context=context_str, question=question)
            response = self.chain.invoke({"context": context_str, "question": question})
            return response
        except Exception as e:
            return f"Error: Could not connect to AI service (Ollama). details: {str(e)}"\
                   "\n\nPlease ensure Ollama is running with `ollama run mistral`."

qa_agent = QAAgent()
