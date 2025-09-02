from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

def build_rag_chain(llm, retriever, chain_type: str = "stuff", return_source_documents: bool = True):
    prompt = PromptTemplate.from_template(
        """You are a nutrition expert assistant. Based on the context provided, answer the question clearly and concisely.
    Present your answer using bullet points if multiple distinct facts are available, or a single paragraph otherwise.
    
    CRITICAL INSTRUCTIONS:
    1. The context contains valuable nutrition information - use ALL of it to answer the question.
    2. Look for BOTH direct mentions AND related information about the topic.
    3. Information about health professionals, dietitians, nutritionists, and medical experts IS present in the data.
    4. If you see ANY information related to the question, use it to provide an answer.
    5. NEVER state information is unavailable unless you've thoroughly examined all context and found nothing relevant.
    6. When information is partially available, provide what you can find rather than saying it's not available.
    
Context:
{context}

Question: {question}

Answer:"""
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type=chain_type,
        retriever=retriever,
        return_source_documents=return_source_documents,
        chain_type_kwargs={"prompt": prompt},
    )
