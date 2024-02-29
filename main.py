import tempfile

from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Manual- Automation Test Case Converter", layout='wide', page_icon="🤖")
st.title('Manual- Automation Test Case Converter')
os.environ['OPENAI_API_KEY'] = ''


def gen_testcases(uploaded_file, option_pl, option_af):
    with st.status("Generating code...", expanded=True) as status:
        file_path = uploaded_file
        dir_path = os.path.dirname(file_path)
        df = pd.read_excel(file_path)
        temp_dir = tempfile.mkdtemp()
        llm = OpenAI(model_name="gpt-3.5-turbo-0125")
        chat_model = ChatOpenAI(temperature=0.8)
        for ind in df.index:
            prompt = PromptTemplate(
                template=""""/
            You are an software automation test engineer. Generate a script for the test case {test_case} using below instructions.
            Please write a code in {pgm_lang} based {auto_framework} framework to automate the below steps in Firefox browser.

            {steps}

            just give me the code and make sure all the required libraries are imported. No explanations are required.
            """,
                input_variables=["test_case", "pgm_lang", "auto_framework", "steps"]
            )

            prompt_formatted_str: str = prompt.format(
                test_case=df['Test Case'][ind],
                pgm_lang=option_pl,
                auto_framework=option_af,
                # test_framework="testNG",
                steps=df['Steps'][ind]
            )

            # predict_code = llm.invoke(prompt_formatted_str)
            st.write(f"Generating code for ...{df['Test Case No'][ind]}")
            predict_code = chat_model.invoke(prompt_formatted_str)
            # print(predict_code)
            ext = 'java'
            if option_pl.lower() == 'java':
                ext = 'java'
                comment_start_char = "/*"
                comment_end_char = "*/"
                header1 = "///////////////////////////////////////////////////////////////////////////////"
                header2 = "/////////////////////////////SOURCE CODE///////////////////////////////////////"
            else:
                ext = 'py'
                comment_start_char = '"""'
                comment_end_char = '"""'
                header1 = "################################################################################"
                header2 = "###########################SOURCE CODE##########################################"
            op_file_path = os.path.join(dir_path, f"{df['Test Case No'][ind]}.{ext}")

            with open(op_file_path, 'w') as f:
                f.write(f"{comment_start_char}Test Case ID : {df['Test Case No'][ind]} {comment_end_char}\n")
                f.write(f"{comment_start_char}Description  : {df['Test Case'][ind]} {comment_end_char}\n")
                f.write(f"{comment_start_char}Manual Steps  : \n{df['Steps'][ind]} \n{comment_end_char}\n")
                f.write(header1)
                f.write(header2)

                f.write(predict_code.content)
            st.write(f"Created a source code file")
        status.update(label="Scripts are generated!", state="complete", expanded=False)


uploaded_file = st.text_input("Choose a test case file")
# print(uploaded_file.f)
col1, col2 = st.columns(2)
with col1:
    option_af = st.selectbox("Select a automation framework", ('Selenium', 'TestNG', 'Cucumber', 'Junit'))
with col2:
    option_pl = st.selectbox("Select a Programming Language", ('Java', 'Python'))

if st.button('Generate'):
    gen_testcases(uploaded_file, option_pl, option_af)
