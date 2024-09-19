from langchain_community.embeddings import OllamaEmbeddings

llama3_embeddings = OllamaEmbeddings(
    #base_url='http://llama3:11434',
    # for local testing, simple remove base url (default is localhost)
    model="llama3"
)