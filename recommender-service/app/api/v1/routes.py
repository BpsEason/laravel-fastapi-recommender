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
        cached_recommendations = redis_client.get(redis_key)
        if cached_recommendations:
            logger.info(f"Returning cached recommendations for user {user_id}")
            return json.loads(cached_recommendations)

    logger.info(f"Cache miss for user {user_id}. Calculating recommendations...")
    start_time = time.time()
    
    recommender = Recommender(db)
    recommended_product_ids = recommender.recommend_for_user(user_id, num_recommendations)
    
    end_time = time.time()
    logger.info(f"Recommendation calculation for user {user_id} took {end_time - start_time:.4f} seconds.")

    if redis_client:
        redis_client.setex(redis_key, 3600, json.dumps(recommended_product_ids))
        logger.info(f"Recommendations for user {user_id} cached in Redis.")

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
    recommended_product_ids = recommender.recommend_for_user(user_id, 5)
    
    if redis_client:
        redis_key = f"user:{user_id}:recommendations"
        redis_client.setex(redis_key, 3600, json.dumps(recommended_product_ids))
        logger.info(f"Recommendations for user {user_id} re-calculated and updated in Redis.")

    return {"message": f"Recommendations for user {user_id} re-calculated and cached."}
