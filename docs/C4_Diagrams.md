# C4 Diagrams for Medical Chatbot

This document contains C4 model diagrams (Levels 1-3) for the Medical Chatbot system, based on the C4 model from c4model.com.

The C4 model helps visualize software architecture at different levels of abstraction.

## Level 1: System Context Diagram

This diagram shows the system in its environment, including users and external systems.

```plantuml
@startuml System Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "User", "Medical professional or patient asking health-related questions")

System(medical_chatbot, "Medical Chatbot", "RAG-based medical Q&A system")

System_Ext(openai, "OpenAI API", "Provides GPT language model")
System_Ext(pinecone, "Pinecone", "Vector database for embeddings")
System_Ext(huggingface, "Hugging Face", "Provides embedding models")

Rel(user, medical_chatbot, "Asks medical questions")
Rel(medical_chatbot, openai, "Queries for answer generation")
Rel(medical_chatbot, pinecone, "Retrieves relevant medical context")
Rel(medical_chatbot, huggingface, "Downloads embedding models")
@enduml
```

## Level 2: Container Diagram

This diagram shows the high-level technology choices and how containers communicate.

```plantuml
@startuml Containers
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "Medical professional or patient")

System_Boundary(medical_chatbot_system, "Medical Chatbot System") {
    Container(flask_app, "Flask Web App", "Python/Flask", "Serves web interface and handles chat logic")
    ContainerDb(vector_db, "Pinecone Vector DB", "Pinecone", "Stores document embeddings for similarity search")
    Container(embedding_service, "Embedding Service", "Hugging Face", "Generates vector embeddings from text")
    Container(llm_service, "LLM Service", "OpenAI GPT", "Generates natural language responses")
}

System_Ext(pdf_data, "Medical PDF Data", "Static PDF files")

Rel(user, flask_app, "HTTP requests", "JSON")
Rel(flask_app, vector_db, "Queries embeddings", "API")
Rel(flask_app, embedding_service, "Downloads model", "HTTP")
Rel(flask_app, llm_service, "Generates answers", "API")
Rel(flask_app, pdf_data, "Loads documents", "File system")
@enduml
```

## Level 3: Component Diagram

This diagram shows the internal components within the Flask Web App container.

```plantuml
@startuml Components
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container_Boundary(flask_app, "Flask Web App") {
    Component(small_talk_handler, "Small Talk Handler", "Python", "Handles greetings and basic interactions")
    Component(rag_chain, "RAG Chain", "LangChain", "Orchestrates retrieval and generation")
    Component(retriever, "Retriever", "LangChain/Pinecone", "Fetches relevant documents from vector store")
    Component(prompt_engine, "Prompt Engine", "LangChain", "Creates prompts with context for LLM")
    Component(llm_interface, "LLM Interface", "OpenAI", "Interfaces with GPT model")
}

ContainerDb(vector_store, "Pinecone Vector Store", "Pinecone", "Indexed medical document chunks")

Rel(small_talk_handler, rag_chain, "Delegates to RAG if not small talk")
Rel(rag_chain, retriever, "Uses retriever to get context")
Rel(retriever, vector_store, "Similarity search")
Rel(rag_chain, prompt_engine, "Builds prompt with retrieved docs")
Rel(prompt_engine, llm_interface, "Sends prompt to LLM")
Rel(llm_interface, rag_chain, "Returns generated answer")
@enduml
```

These diagrams provide a hierarchical view of the Medical Chatbot architecture, from high-level context to detailed components.
