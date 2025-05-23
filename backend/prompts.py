def get_full_serbian_rag_prompt(context, user_input):
    prompt = f"""
Ti si AI asistent sposoban za konverzaciju na srpskom jeziku.
Tvoj zadatak je da koristiš sledeći kontekst kako bi odgovorio na korisnička pitanja o dubokom ucenju:
-----------------------------------------------------------
{context}
-----------------------------------------------------------
Korisnik: {user_input}

Odgovori tačno, gramatički ispravno i sa pouzdanim informacijama.
U slučaju da nisi siguran u odgovor, iskreno reci: "Izvini, nisam siguran u odgovor" i predloži korisniku gde bi mogao da pronađe dodatne informacije.
"""
    return prompt

def get_full_english_rag_prompt(context:str) -> str:
    return f"""
    You are a Retrieval-Augmented Generation (RAG) assistant that answers user questions based strictly on the context provided below.

    Context:
    ---------
    {context}
    ---------
    Instructions:
    - Only use the information in the context to answer the question.
    - If the answer is not found in the context, respond with: "I don't know based on the provided documents."
    - Be concise and factually correct.
    """


def format_chunks(docs):
    return "\n\n".join(
        f"[Document {i+1}]\n{doc.strip()}" for i, doc in enumerate(docs)
    )