import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import load_prompt
from app_function import print_history, add_history, create_chain, create_agent
from dotenv import load_dotenv

# API KEY 정보 로드
load_dotenv()

st.set_page_config(page_title="상담 Chatbot 💬", page_icon="💬")
st.title("상담 Chatbot 💬")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    clear_btn = st.button("대화내용 초기화")
    
    # 초기화 상태에서 기본 모드 설정
    if "active_chatbot" not in st.session_state:
        st.session_state["active_chatbot"] = "일반 chatbot"

    # 일반챗봇과 Agent 적용 챗봇 선택
    chatbot_options = ["일반 chatbot", "Agent를 이용한 chatbot"]
    selected_chatbot = st.selectbox("chatbot 선택", chatbot_options, key="chatbot_select")

    # 모델 선택 
    model_options = ["gpt-3.5-turbo", "gpt-4o-mini"]
    selected_model = st.selectbox("모델 선택", model_options, key="model_select")

    # Temperature 슬라이더 추가
    temperature = st.slider(
        "응답의 다양성 조절 (Temperature)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1, 
        key="temperature"
    )

    # 프롬프트 내용 설정 (chatbot 선택에 따라 기본값 변경)
    if selected_chatbot == "일반 chatbot":
        prompt = """일반 챗봇 : 당신은 전문 상담사 역할을 맡은 AI 어시스턴트입니다. 사용자의 고민과 질문에 공감하며, 적절한 조언과 정보를 제공하세요. 모든 답변은 친절하고 명확하게 작성해야 합니다."""
        
    elif selected_chatbot == "Agent를 이용한 chatbot":
        prompt = """Agent 챗봇 : 당신은 전문 상담사 역할을 맡은 AI 어시스턴트입니다. 사용자의 고민과 질문에 공감하며, 적절한 조언과 정보를 제공하세요. 모든 답변은 친절하고 명확하게 작성해야 합니다."""

    # 프롬프트 입력 필드 및 적용 버튼
    tab3, tab4 = st.tabs(["프롬프트 정의", "프리셋"])
    
    user_text_prompt = tab3.text_area("프롬프트", value=prompt, key="user_text_prompt")
    
    # 프롬프트 적용 버튼
    user_text_apply_btn = tab3.button("적용", key="apply1")

    # 사용자가 직접 프롬프트를 적용한 경우
    if user_text_apply_btn:
        tab3.markdown(f"✅ 해당 모델이 적용되었습니다")
        # 일반 챗봇 또는 Agent 모드에 따라 다른 체인 생성
        if selected_chatbot == "일반 chatbot":
            # 일반 챗봇 프롬프트
            prompt_template = user_text_prompt + "\n\n#Question:\n{question}\n\n#Answer:"
            prompt = PromptTemplate.from_template(prompt_template)
            st.session_state["chain"] = create_chain(prompt, selected_model, temperature)
        else:
            # Agent 프롬프트 (agent_scratchpad 포함)
            prompt_template = user_text_prompt + "\n\n#Agent Scratchpad:\n{agent_scratchpad}\n\n#Question:\n{question}\n\n#Answer:"
            prompt = PromptTemplate(
                input_variables=["agent_scratchpad", "question"],  # Agent-specific variables
                template=prompt_template
            )
            st.session_state["chain"] = create_agent(selected_model, temperature, prompt)

    if selected_chatbot == "일반 chatbot":
        # 프리셋 선택
        user_selected_prompt = tab4.selectbox("프리셋 선택", ["친절한지인", "갑상선암전문의"])
        user_selected_apply_btn = tab4.button("적용", key="apply2")
    elif selected_chatbot == "Agent를 이용한 chatbot":
        user_selected_prompt = tab4.selectbox("프리셋 선택", ["친절한지인_agent", "갑상선암전문의_agent"])
        user_selected_apply_btn = tab4.button("적용", key="apply2")

    if user_selected_apply_btn:
        tab4.markdown(f"✅ 해당 모델이 적용되었습니다")
        prompt = load_prompt(f"prompts/{user_selected_prompt}.yaml", encoding="utf8")
        
        # 일반 챗봇 또는 Agent 모드에 따라 다른 체인 생성
        if selected_chatbot == "일반 chatbot":
            st.session_state["chain"] = create_chain(prompt, selected_model, temperature)
        else:
            st.session_state["chain"] = create_agent(selected_model, temperature, prompt)

# 대화내용 초기화 버튼을 누르면 대화내용 초기화
if clear_btn:
    st.session_state["messages"].clear()

print_history()

# 초기화 상태
if "chain" not in st.session_state:
    # 기본 프롬프트 설정
    prompt_template = prompt + "\n\n#Question:\n{question}\n\n#Answer:"
    prompt = PromptTemplate.from_template(prompt_template)
    if selected_chatbot == "일반 chatbot":
        st.session_state["chain"] = create_chain(prompt, selected_model, temperature)
    else:
        st.session_state["chain"] = create_agent(selected_model, temperature, prompt)

# 일반 chatbot 또는 Agent chatbot 이용
if selected_chatbot == "일반 chatbot":
    if user_input := st.chat_input():
        add_history("user", user_input)
        st.chat_message("user").write(user_input)

        # 스피너 추가
        with st.spinner("생각 중... 잠시만 기다려 주세요."):
            with st.chat_message("assistant"):
                chat_container = st.empty()

                # 데이터 스트리밍
                stream_response = st.session_state["chain"].stream(
                    {"question": user_input}
                )
                ai_answer = ""
                for chunk in stream_response:
                    # 딕셔너리 형태 처리
                    if isinstance(chunk, dict) and "output" in chunk:
                        chunk = chunk["output"]
                    ai_answer += chunk
                    chat_container.markdown(ai_answer)
                add_history("ai", ai_answer)

elif selected_chatbot == "Agent를 이용한 chatbot":
    st.write("Agent 기반 대화 기능이 활성화되었습니다.")
    if user_input := st.chat_input():
        add_history("user", user_input)
        st.chat_message("user").write(user_input)

        # 스피너 추가
        with st.spinner("생각 중... 잠시만 기다려 주세요."):
            with st.chat_message("assistant"):
                chat_container = st.empty()

                # 데이터 스트리밍
                stream_response = st.session_state["chain"].stream(
                    {"question": user_input, "agent_scratchpad": ""}
                )

                ai_answer = ""
                for chunk in stream_response:
                    # 딕셔너리 형태 처리
                    if isinstance(chunk, dict) and "output" in chunk:
                        chunk = chunk["output"]
                    ai_answer += chunk
                    chat_container.markdown(ai_answer)

                add_history("ai", ai_answer)


