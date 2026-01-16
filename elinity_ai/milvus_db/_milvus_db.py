# Mock classes
class MockHit:
    def __init__(self, id, score):
        self.id = id
        self.score = score
        self.entity = {"id": id} # Some clients access entity dict

class MilvusDB: 
    def __init__(self,collection_name="tenants",dim=768,top_k=6):
        # MOCK INIT
        self.collection_name = collection_name
            
    def embed_docs(self,docs):  
        return []
        
    def upsert(self,data):
        return None
    
    def query(self,query): 
        # MOCK QUERY Response
        # Returns list of lists of Hit-like objects, NOT dicts, because router uses item.id
        # USE VALID UUID to prevent DB 500 errors
        return [[MockHit("123e4567-e89b-12d3-a456-426614174000", 0.99)]]

# Mock Pipeline for recommendations.py
class MilvusUserSimilarityPipeline:
    def __init__(self): pass
    def find_similar_users_by_id(self, embedding_id, top_k=5):
        return [{"id": "mock_id_123", "score": 0.95}]
    def close(self): pass


 

 
try:
    milvus_db = MilvusDB()
except Exception:
    # If Milvus is not configured or unavailable, expose milvus_db as None
    # so other parts of the app can run with degraded functionality.
    milvus_db = None