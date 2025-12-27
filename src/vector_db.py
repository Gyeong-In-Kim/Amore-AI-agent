import os
import chromadb
from chromadb.utils import embedding_functions
from data_loader import load_product_data 

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(os.path.dirname(current_dir), 'chroma_db')

# 한국어 지원 임베딩 모델 설정
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

def get_client():
    return chromadb.PersistentClient(path=db_path)

def init_db(force_reset=False):
    """DB 초기화 및 데이터 적재 (force_reset=True시 강제 갱신)"""
    client = get_client()
    
    # 컬렉션 이름 목록 가져오기 (안전한 방법)
    try:
        cols = client.list_collections()
        col_names = [c.name for c in cols]
    except:
        col_names = []

    # 강제 리셋 요청 시 삭제
    if force_reset and "cosmetics" in col_names:
        print("🔄 [Vector DB] 기존 DB 삭제 후 재생성...")
        client.delete_collection("cosmetics")
    
    collection = client.get_or_create_collection(
        name="cosmetics", 
        embedding_function=sentence_transformer_ef
    )

    # 데이터가 비어있으면 로드
    if collection.count() == 0:
        products = load_product_data()
        if not products: return None

        ids = [str(i) for i in range(len(products))]
        docs = [p['search_text'] for p in products]
        metas = [p['metadata'] for p in products]

        collection.add(ids=ids, documents=docs, metadatas=metas)
        print(f"🎉 [Vector DB] {len(ids)}개 데이터 적재 완료!")
    
    return collection

def search_best_product(query):
    """쿼리와 가장 유사한 제품 1개 검색"""
    client = get_client()
    try:
        collection = client.get_collection(name="cosmetics", embedding_function=sentence_transformer_ef)
    except:
        collection = init_db()

    results = collection.query(query_texts=[query], n_results=1)
    
    if not results['documents'] or not results['documents'][0]:
        return None
    return results['metadatas'][0][0]