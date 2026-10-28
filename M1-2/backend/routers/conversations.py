from datetime import datetime
from fastapi import APIRouter, HTTPException
from firebase_admin import firestore
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

class ConversationCreate(BaseModel):
    title: str
    messages: List[Dict[str, Any]]

@router.post("")
def save_conversation(conv: ConversationCreate):
    try:
        db = firestore.client()
        data = {
            "title": conv.title,
            "messages": conv.messages,
            "updated_at": datetime.utcnow().isoformat(),
        }
        doc_ref = db.collection("conversations").add(data)
        return {"id": doc_ref[1].id, "message": "대화가 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 💡 기존 대화에 메시지를 이어서 업데이트하는 PUT 엔드포인트 추가
@router.put("/{id}")
def update_conversation(id: str, conv: ConversationCreate):
    try:
        db = firestore.client()
        doc_ref = db.collection("conversations").document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        
        data = {
            "messages": conv.messages,
            "updated_at": datetime.utcnow().isoformat(),
        }
        doc_ref.update(data)
        return {"id": id, "message": "대화가 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_conversations_list():
    try:
        db = firestore.client()
        docs = (
            db.collection("conversations")
            .order_by("updated_at", direction="DESCENDING")
            .stream()
        )
        result = []
        for doc in docs:
            item = doc.to_dict()
            result.append(
                {
                    "id": doc.id,
                    "title": item.get("title", "대화"),
                    "updated_at": item.get("updated_at"),
                }
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
def get_conversation_detail(id: str):
    try:
        db = firestore.client()
        doc = db.collection("conversations").document(id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def delete_conversation(id: str):
    try:
        db = firestore.client()
        doc_ref = db.collection("conversations").document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        doc_ref.delete()
        return {"message": "대화가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))