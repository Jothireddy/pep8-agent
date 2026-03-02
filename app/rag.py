import faiss
import numpy as np
from openai import OpenAI
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

class PEP8RAG:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index_path = "faiss_index.bin"
        self.docs_path = "faiss_docs.pkl"
        
        # Load or create index
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"✅ Loaded existing PEP 8 index ({len(self.documents)} chunks)")
        else:
            print("📚 Creating new PEP 8 index...")
            self.index = None
            self.documents = []
            self._load_pep8_rules()
    
    def _get_embedding(self, text):
        """Get embedding from OpenAI"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _load_pep8_rules(self):
        """Load PEP 8 rules into FAISS index"""
        # Read PEP 8 file
        with open("data/pep8_rules.txt", "r", encoding="utf-8") as f:
            pep8_content = f.read()
        
        # Split into chunks
        chunks = self._split_into_chunks(pep8_content)
        print(f"📝 Processing {len(chunks)} PEP 8 sections...")
        
        # Create embeddings using OpenAI
        embeddings = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                print(f"  Processing chunk {i+1}/{len(chunks)}...", end='\r')
                embedding = self._get_embedding(chunk)
                embeddings.append(embedding)
                self.documents.append(chunk)
        
        print(f"\n✅ Created {len(self.documents)} embeddings")
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_array.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_array)
        
        # Save index and documents
        faiss.write_index(self.index, self.index_path)
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"✅ Saved FAISS index with {len(self.documents)} PEP 8 rules")
    
    def _split_into_chunks(self, content):
        """Split PEP 8 content into logical chunks"""
        chunks = []
        current_chunk = []
        
        for line in content.split('\n'):
            # Split on headings
            if line.strip() and (line.isupper() or line.startswith('=')):
                if current_chunk and len(' '.join(current_chunk).split()) > 50:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            else:
                current_chunk.append(line)
            
            # Split on long chunks (max 400 words)
            if len(' '.join(current_chunk).split()) > 400:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Filter out very short chunks
        chunks = [c for c in chunks if len(c.split()) > 20]
        
        return chunks
    
    def query_rules(self, code_snippet, n_results=3):
        """Query relevant PEP 8 rules for a code snippet"""
        # Create embedding using OpenAI
        query_embedding = self._get_embedding(code_snippet)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, n_results)
        
        # Return relevant documents
        results = [self.documents[i] for i in indices[0]]
        return results


# Test
if __name__ == "__main__":
    rag = PEP8RAG()
    
    test_code = "def CalculateTotal(items): total=0"
    rules = rag.query_rules(test_code)
    
    print("\n🔍 Relevant PEP 8 rules:")
    for i, rule in enumerate(rules, 1):
        print(f"\n--- Rule {i} ---")
        print(rule[:300] + "..." if len(rule) > 300 else rule)