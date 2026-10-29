"""CYF AI Concierge local pilot. Approved FAQ records only."""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from faq_loader import approved_faq, build_faq_context, reviewed_faq

load_dotenv()
st.set_page_config(page_title='CYF AI Concierge', page_icon='💬')
st.title('CodeYourFuture AI Concierge')
st.caption('Internal pilot · Not an official application or eligibility decision')

from app_policy import SYSTEM_POLICY

dev_mode = os.getenv("CYF_DEV_MODE") == "true"

records = reviewed_faq() if dev_mode else approved_faq()

if dev_mode:
    st.warning(
        "DEVELOPMENT MODE: Answers use reviewed but "
        "not officially approved CYF content."
    )
    
if not records:
    st.warning('No FAQ answers are approved yet. CYF-specific questions will receive a verification notice.')

system_prompt = SYSTEM_POLICY + '\nAPPROVED FAQ:\n' + build_faq_context(records)
if 'messages' not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if prompt := st.chat_input('Ask about CodeYourFuture courses'):
    st.session_state.messages.append({'role':'user','content':prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        if not records:
            reply = ('The CYF course information is currently awaiting review, so I cannot confirm '
                     'specific requirements or policies yet. Please check '
                     'https://codeyourfuture.io/become-a-student/ for official guidance.')
        elif not os.getenv('OPENAI_API_KEY'):
            reply = 'An OpenAI API key is required to run this internal pilot.'
        else:
            try:
                response = OpenAI().chat.completions.create(
                    model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),
                    temperature=0.2,
                    messages=[{'role':'system','content':system_prompt}] + st.session_state.messages[-12:]
                )
                reply = response.choices[0].message.content or 'I could not generate an answer.'
            except Exception:
                reply = 'The assistant is temporarily unavailable. Please try again later.'
        st.markdown(reply)
    st.session_state.messages.append({'role':'assistant','content':reply})
