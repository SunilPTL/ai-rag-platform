from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import chromadb

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.Client()

collection = client.get_or_create_collection(
    name="mydoc"
)

def process_pdf(file_path:str, user_id:int, file_id:int):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

    splitters = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 50
    )    

    chunks = splitters.split_text(text)

    embeddings = model.encode(chunks)

    metadata = [
        {
            "user_id": str(user_id),
            "file_id": str(file_id)
        }

        for _ in chunks
    ]

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata,
        ids= [f"{file_id}_{i}" for i in range(len(chunks))]
    )

def query_rag(question:str, user_id:int):
    query_embeddings = model.encode([question])[0]

    # similarity search 
    results = collection.query(
        query_embeddings=[query_embeddings.tolist()],
        n_results = 3,
        where= {"user_id" : str(user_id)}
    )

    documents = results["documents"][0]

    # build context
    context = "\n".join(documents)

    return context

def resume_rag(user_id:int):

    # similarity search 
    results = collection.get(
        where= {"user_id" : str(user_id)}
    )

    docs = results["documents"]

    # build context
    # context = "\n".join(docs)

    return docs