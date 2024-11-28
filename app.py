import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import ChatMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import load_prompt
from dotenv import load_dotenv

# API KEY 정보 로드
load_dotenv()

st.set_page_config(page_title="상담 Chatbot 💬", page_icon="💬")
st.title("상담 Chatbot 💬")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def print_history():
    for msg in st.session_state["messages"]:
        st.chat_message(msg.role).write(msg.content)

def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))

# 체인을 생성합니다. (ChatOpenAI 부붙에 agent를 추가해주면 agent사용가능)
def create_chain(prompt, model):
    chain = prompt | ChatOpenAI(model_name=model) | StrOutputParser()
    return chain


with st.sidebar:
    clear_btn = st.button("대화내용 초기화")

    # 모델 선택 
    model_options = ["gpt-3.5-turbo", "gpt-4o-mini",]
    selected_model = st.selectbox("모델 선택", model_options, key="model_select")

    # 프롬프트 선택
    tab1, tab2 = st.tabs(["프롬프트 정의", "프리셋"])
    prompt = """당신은 전문 상담사 역할을 맡은 AI 어시스턴트입니다. 사용자의 고민과 질문에 공감하며, 적절한 조언과 정보를 제공하세요. 모든 답변은 친절하고 명확하게 작성해야 합니다."""
    user_text_prompt = tab1.text_area("프롬프트", value=prompt)
    user_text_apply_btn = tab1.button("프롬프트 적용", key="apply1")

    # 사용자가 직접 프롬프트를 적용한 경우
    if user_text_apply_btn:
        tab1.markdown(f"✅ 프롬프트가 적용되었습니다")
        prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
        prompt = PromptTemplate.from_template(prompt_template)
        st.session_state["chain"] = create_chain(prompt, selected_model)  # 모델 선택 반영

    # 개발자가 지정해둔 프롬프트를 적용한 경우
    user_selected_prompt = tab2.selectbox("프리셋 선택", ["친절한지인", "갑상선암전문의"])
    user_selected_apply_btn = tab2.button("프롬프트 적용", key="apply2")
    if user_selected_apply_btn:
        tab2.markdown(f"✅ 프롬프트가 적용되었습니다")
        prompt = load_prompt(f"prompts/{user_selected_prompt}.yaml", encoding="utf8")
        st.session_state["chain"] = create_chain(prompt, selected_model)  # 모델 선택 반영

# 대화내용 초기화 버튼을 누르면 대화내용 초기화 시킴
if clear_btn:
    st.session_state["messages"].clear()

print_history()

if "chain" not in st.session_state:
    # user_prompt
    prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
    prompt = PromptTemplate.from_template(prompt_template)
    st.session_state["chain"] = create_chain(prompt, selected_model)  # 모델 선택 반영


if user_input := st.chat_input():
    add_history("user", user_input)
    st.chat_message("user").write(user_input)
    with st.chat_message("assistant"):
        chat_container = st.empty()

        stream_response = st.session_state["chain"].stream(
            {"question": user_input}
        )  # 문서에 대한 질의
        ai_answer = ""
        for chunk in stream_response:
            ai_answer += chunk
            chat_container.markdown(ai_answer)
        add_history("ai", ai_answer)
