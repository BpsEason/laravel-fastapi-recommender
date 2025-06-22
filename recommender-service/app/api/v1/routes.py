from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import json
import logging
import time

from ...dependencies import get_db, get_redis_client
from ...services.recommender_logic import Recommender
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recommendations/{user_id}", response_model=List[int])
async def get_recommendations_for_user(
    user_id: int,
    num_recommendations: int = 5,
    db: Depends(get_db),
    redis_client: Depends(get_redis_client)
):
    logger.info(f"Received recommendation request for user_id: {user_id}")

    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    redis_key = f"user:{user_id}:recommendations"
    if redis_client:
        try:
            cached_recommendations = redis_client.get(redis_key)
            if cached_recommendations:
                logger.info(f"Returning cached recommendations for user {user_id}")
                return json.loads(cached_recommendations)
        except Exception as e:
            logger.error(f"Error accessing Redis for user {user_id}: {e}")
            # 如果 Redis 讀取失敗，繼續計算推薦

    logger.info(f"Cache miss for user {user_id} or Redis error. Calculating recommendations...")
    start_time = time.time()
    
    recommender = Recommender(db)
    recommended_product_ids = recommender.recommend_for_user(user_id, num_recommendations)
    
    end_time = time.time()
    logger.info(f"Recommendation calculation for user {user_id} took {end_time - start_time:.4f} seconds. Result: {recommended_product_ids}")

    if redis_client and recommended_product_ids:
        try:
            redis_client.setex(redis_key, 3600, json.dumps(recommended_product_ids))
            logger.info(f"Recommendations for user {user_id} cached in Redis.")
        except Exception as e:
            logger.error(f"Error writing recommendations to Redis for user {user_id}: {e}")

    return recommended_product_ids

@router.post("/recommendations/recalculate/{user_id}")
async def recalculate_user_recommendations(
    user_id: int,
    db: Depends(get_db),
    redis_client: Depends(get_redis_client)
):
    logger.info(f"Forcing recalculation for user_id: {user_id}")
    
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    recommender = Recommender(db)
    recommended_product_ids = recommender.recommend_for_user(user_id, 5) # 可以傳遞數量參數，或使用默認值
    
    if redis_client and recommended_product_ids:
        try:
            redis_key = f"user:{user_id}:recommendations"
            redis_client.setex(redis_key, 3600, json.dumps(recommended_product_ids))
            logger.info(f"Recommendations for user {user_id} re-calculated and updated in Redis.")
        except Exception as e:
            logger.error(f"Error writing re-calculated recommendations to Redis for user {user_id}: {e}")
            return {"message": f"Recommendations calculated for user {user_id} but failed to cache.", "status": "error"}

    return {"message": f"Recommendations for user {user_id} re-calculated and cached."}
