from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes
import os
from dotenv import load_dotenv
load_dotenv()

# 1. Create prompt template
system_template = "Translate the following sentence into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# 2. Model from Groq Cloud (Gemma2-9b-It)
groq_api_key=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key)

# 3. Output Parser to beautify
parser=StrOutputParser()

# 4. Create chain usin LCEL
chain=prompt_template|model|parser



## App definition
app=FastAPI(title="Langchain Server",
            version="1.0",
            description="A simple API server using Langchain runnable interfaces")

## Adding chain routes
add_routes(app, chain, path="/chain")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)


# python LCEL_Chain.py to run
# URL/docs --> http://127.0.0.1:8000/docs to access all endpoints of FastAPI


