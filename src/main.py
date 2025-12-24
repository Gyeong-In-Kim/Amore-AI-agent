import json
import os
from sys import platform
import time
from vector_db import init_db, search_best_product
from generator import generate_marketing_copy

def load_users():
    """가상 고객 데이터 로드"""
    # 상위 폴더의 data/users.json 찾기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, 'data', 'users.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_batch_agent():
    print("🚀 [Amore Marketing Agent] 대량 발송 작업을 시작합니다...")
    print("--------------------------------------------------")
    
    # 1. 시스템 준비
    init_db()
    users = load_users()
    
    print(f"📋 총 {len(users)}명의 타겟 고객을 발견했습니다.\n")
    
    # 2. 고객 한 명씩 순회하며 작업 (Loop)
    for user in users:
        print(f"👤 고객 분석 중: {user['name']} ({user['age']}세, {user['skin_type']})")
        
        # (1) 검색: 고객 고민을 쿼리로 변환해서 검색
        # "지성 피부인데 오후만 되면 화장이 무너짐" -> 이런 식으로 검색
        query = f"{user['skin_type']} 피부, 고민: {', '.join(user['concerns'])}"
        best_product = search_best_product(query)
        
        if not best_product:
            print("   → ❌ 적합한 제품을 못 찾음 (패스)")
            continue
            
        print(f"   → 🔍 매칭 제품: {best_product['name']}")
        
        # (2) 생성: 개인화 메시지 작성
        # user 정보를 통째로 넘기지 않고, 필요한 문자열만 조합해서 넘김
        user_context = f"{user['name']}님({user['age']}세), 고민: {', '.join(user['concerns'])}"
        copy_text = generate_marketing_copy(best_product, user_context)
        
        # (3) 결과 출력 (실제로는 여기서 카톡 API를 쏘게 됨)
        # platform이 없으면 기본값으로 '알림톡'을 사용하도록 수정
        platform = user.get('platform', '알림톡')
        print(f"\n   📩 [발송할 메시지 ({platform})]")
        print("   " + "-" * 30)
        print(f"   {copy_text.strip()}")
        print("   " + "-" * 30 + "\n")
        
        # API 과부하 방지용 딜레이
        time.sleep(1) 

if __name__ == "__main__":
    run_batch_agent()