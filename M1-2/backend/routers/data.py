from fastapi import APIRouter, HTTPException
from firebase_config import db
from pydantic import BaseModel
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/data", tags=["Data"])


class ExerciseData(BaseModel):
    date: str  # "YYYY-MM-DD"
    exercise_type: str  # 예: "스쿼트", "벤치프레스", "달리기"
    value: float  # 중량(kg) 또는 시간(분)
    memo: str = ""


@router.post("")
def create_data(data: ExerciseData):
    try:
        doc_ref = db.collection("data").add(data.dict())
        return {"id": doc_ref[1].id, "message": "데이터가 성공적으로 추가되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def get_data_list():
    try:
        docs = (
            db.collection("data").order_by("date", direction="DESCENDING").stream()
        )
        result = []
        for doc in docs:
            item = doc.to_dict()
            item["id"] = doc.id
            result.append(item)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{id}")
def update_data(id: str, data: ExerciseData):
    try:
        doc_ref = db.collection("data").document(id)
        if not doc_ref.get().exists:
            raise HTTPException(
                status_code=404, detail="데이터를 찾을 수 없습니다."
            )
        doc_ref.update(data.dict())
        return {"message": "데이터가 수정되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
def delete_data(id: str):
    try:
        doc_ref = db.collection("data").document(id)
        if not doc_ref.get().exists:
            raise HTTPException(
                status_code=404, detail="데이터를 찾을 수 없습니다."
            )
        doc_ref.delete()
        return {"message": "데이터가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def get_data_summary():
    try:
        docs = list(db.collection("data").stream())
        if not docs:
            return {
                "period": "데이터 없음",
                "count": 0,
                "metrics": {"average": 0, "max": 0, "min": 0},
                "trend": "데이터가 부족합니다.",
            }

        values = []
        dates = []
        for doc in docs:
            d = doc.to_dict()
            values.append(d.get("value", 0))
            dates.append(d.get("date", ""))

        dates.sort()
        count = len(values)
        avg_val = round(sum(values) / count, 1) if count > 0 else 0
        max_val = max(values) if values else 0
        min_val = min(values) if values else 0

        trend = "안정적 유지 중"
        if count >= 4:
            recent_avg = sum(values[-2:]) / 2
            old_avg = sum(values[:2]) / 2
            if recent_avg > old_avg:
                trend = "상승 추세 (최근 기록 향상)"
            elif recent_avg < old_avg:
                trend = "하락/정체 추세"

        return {
            "period": f"{dates[0]} ~ {dates[-1]}",
            "count": count,
            "metrics": {
                "average": avg_val,
                "max": max_val,
                "min": min_val,
            },
            "trend": trend,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-dummy")
def generate_dummy_data():
    try:
        today = datetime.now()
        dummy_count = 0
        
        # 클릭할 때마다 10개의 더미 운동 데이터 생성
        exercises = ["스쿼트", "벤치프레스", "데드리프트", "런닝", "랫풀다운", "플랭크"]
        memos = ["가볍게 완료", "오늘 컨디션 좋음", "조금 힘듦", "자극 좋음", "휴식 단축"]

        for _ in range(10):
            days_ago = random.randint(0, 30)
            target_date = today - timedelta(days=days_ago)
            date_str = target_date.strftime("%Y-%m-%d")
            
            selected_exercise = random.choice(exercises)
            value = float(random.randint(20, 120))
            memo = random.choice(memos)
            
            doc_data = {
                "date": date_str,
                "exercise_type": selected_exercise,
                "value": value,
                "memo": memo
            }
            
            db.collection("data").add(doc_data)
            dummy_count += 1
            
        return {"message": f"성공적으로 {dummy_count}개의 더미 기록이 추가되었습니다!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"더미 생성 실패: {str(e)}")