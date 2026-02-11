from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
# from langchain.chains import LLMChain # Deprecated
from core.retriever import retriever
from core.llm import get_llm

DEBUG_TEMPLATE = """
As an expert Software Engineer, your task is to analyze the following stack trace and code context to find the bug.

CONTEXT FROM CODEBASE:
{context}

STACK TRACE / ERROR:
{error}

INSTRUCTIONS:
1. Analyze the stack trace to identify the failing module.
2. Use the provided context to understand the implementation.
3. Suggest a concrete fix with code snippets.
4. Explain *why* the fix works.

RESPONSE:
"""

class DebugAgent:
    def __init__(self):
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            input_variables=["context", "error"],
            template=DEBUG_TEMPLATE
        )
        # self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.chain = self.prompt | self.llm

    def analyze_error(self, error_trace: str) -> str:
        # 1. Extract keywords from trace for search (naive approach)
        # In a real system, we'd parse the trace key frames.
        # Here we just take the last few lines as query.
        query = "\n".join(error_trace.splitlines()[-3:])
        
        # 2. Retrieve context
        results = retriever.search(query, top_k=3)
        context_str = "\n\n".join([f"File: {r['file_path']}\nCode:\n{r['content']}" for r in results])
        
        if not context_str:
            context_str = "No relevant code found in index."

        # 3. Generate analysis
        try:
            # response = self.chain.run(context=context_str, error=error_trace)
            response = self.chain.invoke({"context": context_str, "error": error_trace})
            return response
        except Exception as e:
            return f"Error: Could not connect to AI service (Ollama). details: {str(e)}"\
                   "\n\nPlease ensure Ollama is running with `ollama run mistral`."

debug_agent = DebugAgent()
