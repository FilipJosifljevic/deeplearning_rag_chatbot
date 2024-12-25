from openai import OpenAI
import ollama
import fitz #PyMuPDF
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

#ollama_host = "https://models.institutonline.ai/v1"
#api_key = "bilosta"
client = OpenAI(
    base_url = 'https://models.institutonline.ai/v1',
    api_key='ollama',
)
#api_key = "bilo šta"
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text+=page.get_text()
    
    return text

def process_documents(doc_text):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_text(doc_text)

def load_documents(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return process_documents(text)


def chat_loop():

    pdf_path = 'documents/alexnet.pdf'  # Change to the path of your PDF file
    documents = load_documents(pdf_path)  # Loaded and processed documents

    document_context = "\n".join(documents)

    messages = [
            {"role":"system", "content":"Ti si napredni jezicki model koji razume i govori na srpskom jeziku, ispravnom gramatikom i sa postovanjem i uvazavanjem korisnika. Imas mogucnost citanja i razumevanja ucitanih dokumenata i njihovih detalja, i mozes da odgovaras na korisnicka pitanja u vezi njih.  U slucaju da ne znas odgovor na pitanje nemoj korisniku davati lazne informacije, vec ga obavesti o tome da ne znas i kako moze pronaci informacije koje mu trebaju."},
            {"role":"system", "content":"Dokumenti : {document_context}"}
    ]

    print("Pitajte model bilo šta ili napišite 'exit' za izlaz.")

    while True:
        user_input = input("Vi: ")

        if user_input.lower() == "exit":
            print("Završavamo razgovor.")
            break

        # Add user message to the conversation history
        messages.append({"role": "user", "content": user_input})

        # Here we could integrate document search when FAISS is added.
        # For now, we will just use the chat directly.

        # Get the response from the model
        response = client.chat.completions.create(
            model="llama3.1",
            messages=messages
        )

        # Display the response from the model
        model_reply = response.choices[0].message.content
        print(f"Model: {model_reply}")

        # Append model's reply to conversation history
        messages.append({"role": "assistant", "content": model_reply})


# Start the chat loop
chat_loop()
