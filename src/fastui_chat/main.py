# main.py

import bs4

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import Docx2txtLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableMap
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import AIMessage, HumanMessage

from operator import itemgetter

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

folder_path = "communiques/"  # Chemin du dossier contenant les documents

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
vectorstore = None

# Parcours de tous les fichiers du dossier
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    if os.path.isfile(file_path): # Vérification si le chemin correspond à un fichier
        loader = Docx2txtLoader(file_path)
        document = loader.load()
        
        splits = text_splitter.split_documents(document)

        if vectorstore is None:  # Création de la base de vecteurs chroma si elle n'existe pas encore
            vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        else:
            vectorstore.add_documents(documents=splits)

retriever = vectorstore.as_retriever(search_kwargs={"k": 6}) #récupère les 6 docs les plus proches de la question. Par défaut, k=4

template = """Use the following pieces of context to answer the question at the end. If the question is about a "group", this group is the Casino group.
Use the most current information if possible and if no date has been mentioned in the question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Keep the answer as concise as possible.
{context}
Question: {question}
Helpful Answer:"""
prompt_custom = PromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain_from_docs = (
    {
        "context": lambda input: format_docs(input["documents"]),
        "question": itemgetter("question"),
    }
    | prompt_custom
    | llm
    | StrOutputParser()
)

rag_chain_with_source = RunnableMap(
    {"documents": retriever, "question": RunnablePassthrough()}
) | {
    "Réponse": rag_chain_from_docs,
    "Documents": lambda input: set(doc.metadata['source'] for doc in input["documents"])
}