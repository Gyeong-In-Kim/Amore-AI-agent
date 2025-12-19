import os
import chromadb
from chromadb.utils import embedding_functions
# data_loader에서 데이터 로딩 함수 가져오기
from data_loader import load_product_data 

# 1. 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) 
db_path = os.path.join(project_root, 'chroma_db')

# 2. ChromaDB 클라이언트 설정
client = chromadb.PersistentClient(path=db_path)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name="cosmetics",
    embedding_function=sentence_transformer_ef
)

def init_db():
    """CSV 데이터를 로드해서 DB에 저장하는 함수"""
    # 이미 데이터가 있으면 패스 (테스트 할 때 매번 다시 만들고 싶으면 client.reset() 필요)
    if collection.count() > 0:
        print(f"✅ DB에 이미 데이터가 {collection.count()}개 있어서 스킵할게!")
        return collection

    # data_loader 모듈을 통해 풍부한 CSV 데이터 가져오기
    products = load_product_data()
    
    if not products:
        print("❌ 데이터를 못 가져왔어. data_loader.py 확인해봐!")
        return None

    # DB에 넣을 데이터 준비
    ids = []
    documents = []
    metadatas = []

    for idx, item in enumerate(products):
        ids.append(str(idx))
        # data_loader에서 이미 search_text를 잘 만들어뒀으니 그대로 사용
        documents.append(item['search_text'])
        # 메타데이터도 미리 정리된 것 사용
        metadatas.append(item['metadata'])

    # 데이터 삽입
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"🎉 데이터 {len(ids)}개 DB 적재 완료!")
    return collection

def search_best_product(query):
    """
    사용자 질문(query) 하나만 받아서 가장 적절한 제품을 찾는 함수
    """
    # 혹시 모를 초기화 보장
    if collection.count() == 0:
        init_db()
        
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    if not results['documents'] or not results['documents'][0]:
        return None
        
    best_match = results['metadatas'][0][0]
    return best_match