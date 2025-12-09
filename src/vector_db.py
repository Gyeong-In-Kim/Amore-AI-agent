import os
import json
import chromadb
from chromadb.utils import embedding_functions

# 1. 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
# src의 상위 폴더(프로젝트 루트)를 찾음
project_root = os.path.dirname(current_dir) 
db_path = os.path.join(project_root, 'chroma_db')
data_path = os.path.join(project_root, 'data', 'products.json')

# 2. ChromaDB 클라이언트 설정 (Global 변수로 설정해서 어디서든 쓰게 함)
client = chromadb.PersistentClient(path=db_path)
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name="cosmetics",
    embedding_function=sentence_transformer_ef
)

def init_db():
    """JSON 파일을 읽어서 DB에 저장하는 함수"""
    # 이미 데이터가 있으면 패스
    if collection.count() > 0:
        return

    # JSON 파일 읽기
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"❌ 파일을 못 찾겠어! 경로 확인: {data_path}")
        return

    # DB에 넣을 데이터 준비
    ids = []
    documents = []
    metadatas = []

    for idx, item in enumerate(products):
        ids.append(str(idx))
        text = f"제품명: {item['name']}, 추천 피부: {item['skin_type']}, 해결 고민: {item['concern']}"
        documents.append(text)
        metadatas.append(item)

    # 데이터 삽입
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"🎉 데이터 {len(ids)}개 DB 적재 완료!")

def search_best_product(query):
    """
    사용자 질문(query) 하나만 받아서 가장 적절한 제품을 찾는 함수
    """
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    if not results['documents'][0]:
        return None
        
    best_match = results['metadatas'][0][0]
    return best_match