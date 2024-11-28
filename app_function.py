import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor


def print_history():
    for msg in st.session_state["messages"]:
        st.chat_message(msg.role).write(msg.content)

def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))

def create_chain(prompt, model, temperature):
    chain = prompt | ChatOpenAI(model_name=model, temperature=temperature) | StrOutputParser()
    return chain

# Agent 생성
def create_agent(model, temperature, prompt):
    # ChatOpenAI LLM 인스턴스 생성
    llm = ChatOpenAI(
        temperature=temperature, 
        model_name=model  # model -> model_name 수정
    )
    
    # tool 설정
    search = TavilySearchResults(k=5)  # 검색 툴 예제
    tools = [search]  # 도구 목록에 검색 툴 추가
    
    # LangChain Agent 생성
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # AgentExecutor 생성
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True  # 실행 로그를 활성화
    )

    # 반환하는 객체에 agent 포함
    return agent_executor

# # Chain + Agent 생성
# def create_chain_agent(prompt, model, temperature):
#     agent_executor = create_agent(model, temperature, prompt)
#     chain =  agent_executor | StrOutputParser()
#     return chain