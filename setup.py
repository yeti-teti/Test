from setuptools import find_packages,setup

setup(
    name="generative-ai-project",
    version="0.1.0",
    author="Namita Chhantyal",
    author_email="chhantyalnamita.01@gmail.com",
    description="A Retrieval-Augmented Generation (RAG) based Medical Chatbot using Flask, LangChain, Pinecone, and OpenAI.",
    packages=find_packages(),
    python_requires=">=3.11,<3.12",   
    install_requires=[
        "Flask==3.1.2",
        "python-dotenv==1.1.1",
        "openai==1.109.1",
        "langchain==0.3.27",
        "langchain-core==0.3.29",
        "langchain-community==0.3.14",
        "langchain-openai==0.3.33",
        "langchain-pinecone==0.2.12",
        "langchain-experimental==0.3.4",
        "pinecone-client==6.0.0",
        "pinecone[grpc]==5.3.1",
        "sentence-transformers==5.1.1",
        "huggingface-hub==0.35.1",
        "pypdf==5.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)