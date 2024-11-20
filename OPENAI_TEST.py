import os

os.environ["OPENAI_API_KEY"] = "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"

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import faiss
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import LLMChain

# 모델 초기화
model = ChatOpenAI(model="gpt-4o-mini")

# PDF 파일 로드. 파일의 경로 입력
loader = PyPDFLoader(r"C:\Users\late4\OneDrive\바탕 화면\Study\AI_CAMP/AI_Brif.pdf")

# 페이지 별 문서 로드
docs = loader.load()

text_splitter = CharacterTextSplitter( 
    separator="\n\n",
    chunk_size=100,
    chunk_overlap=10,
    length_function=len,
    is_separator_regex=False,
)

splits = text_splitter.split_documents(docs)

# OpenAI 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
print(model.invoke("hi"))
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

# 프롬프트 템플릿 정의
contextual_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question using only the following context."),
    ("user", "Context: {context}\\n\\nQuestion: {question}")
])

class SimplePassThrough:
    def invoke(self, inputs, **kwargs):
        return inputs

class ContextToPrompt:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template
    
    def invoke(self, inputs):
        # 문서 내용을 텍스트로 변환
        if isinstance(inputs, list):
            context_text = "\n".join([doc.page_content for doc in inputs])
        else:
            context_text = inputs
        
        # 프롬프트 템플릿에 적용
        formatted_prompt = self.prompt_template.format_messages(
            context=context_text,
            question=inputs.get("question", "")
        )
        return formatted_prompt

# Retriever를 invoke() 메서드로 래핑하는 클래스 정의
class RetrieverWrapper:
    def __init__(self, retriever):
        self.retriever = retriever

    def invoke(self, inputs):
        if isinstance(inputs, dict):
            query = inputs.get("question", "")
        else:
            query = inputs
        # 검색 수행
        response_docs = self.retriever.get_relevant_documents(query)
        return response_docs

llm_chain = LLMChain(llm=model, prompt=contextual_prompt)

# RAG 체인 설정
rag_chain_debug = {
    "context": RetrieverWrapper(retriever),
    "prompt": ContextToPrompt(contextual_prompt),
    "llm": model
}

# 챗봇 구동
while True:
    print("========================")
    query = input("질문을 입력하세요 : ")
    
    # 1. Retriever로 관련 문서 검색
    response_docs = rag_chain_debug["context"].invoke({"question": query})
    
    # 2. 문서를 프롬프트로 변환
    prompt_messages = rag_chain_debug["prompt"].invoke({
        "context": response_docs,
        "question": query
    })
    
    # 3. LLM으로 응답 생성
    response = rag_chain_debug["llm"].invoke(prompt_messages)
    
    print("\n답변:")
    print(response.content)