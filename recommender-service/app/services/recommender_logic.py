from sqlalchemy.orm import Session
import numpy as np
from typing import List, Dict, Tuple
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from ..data.data_loader import DataLoader
from ..models.product import Product
from ..models.order import OrderItem
from ..models.interaction import UserInteraction
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class Recommender:
    def __init__(self, db: Session):
        self.db = db
        self.data_loader = DataLoader(db)

    def get_interaction_matrix_and_mappings(self) -> Tuple[np.ndarray, List[int], List[int]]:
        df, user_to_idx, product_to_idx = self.data_loader.load_interaction_data()

        if df.empty:
            logger.info("No interaction data loaded. Returning empty matrix and mappings.")
            return np.array([]), [], []

        num_users = len(user_to_idx)
        num_products = len(product_to_idx)
        
        interaction_matrix = np.zeros((num_users, num_products))
        for _, row in df.iterrows():
            user_idx = user_to_idx[row['user_id']]
            product_idx = product_to_idx[row['product_id']]
            interaction_matrix[user_idx, product_idx] = row['value']

        all_user_ids = [user_id for user_id, _ in sorted(user_to_idx.items(), key=lambda item: item[1])]
        all_product_ids = [product_id for product_id, _ in sorted(product_to_idx.items(), key=lambda item: item[1])]

        return interaction_matrix, all_user_ids, all_product_ids

    def calculate_similarity(self, matrix: np.ndarray) -> np.ndarray:
        # Check if matrix is empty or has only one sample
        if matrix.shape[0] < 2 or np.all(matrix == 0):
            logger.info("Matrix too small or all zeros for similarity calculation. Returning empty array.")
            return np.array([[]])
        
        return cosine_similarity(matrix)

    def recommend_for_user(self, target_user_id: int, num_recommendations: int = 5) -> List[int]:
        interaction_matrix, all_user_ids, all_product_ids = self.get_interaction_matrix_and_mappings()

        # Cold start / Fallback if no user data or matrix is empty
        if not all_user_ids or not all_product_ids or target_user_id not in all_user_ids:
            logger.info(f"User {target_user_id} not in interaction data or no data. Falling back to popular products.")
            return self.get_popular_products(num_recommendations)

        try:
            target_user_idx = all_user_ids.index(target_user_id)
        except ValueError:
            logger.warning(f"Target user ID {target_user_id} not found in all_user_ids. This should not happen if previous check passed.")
            return self.get_popular_products(num_recommendations)

        user_similarity = self.calculate_similarity(interaction_matrix)

        if user_similarity.size == 0 or target_user_idx >= user_similarity.shape[0]:
            logger.info("Similarity matrix is empty or target user index out of bounds. Falling back to popular products.")
            return self.get_popular_products(num_recommendations)

        # Get indices of similar users, excluding self
        similar_users_indices = user_similarity[target_user_idx].argsort()[::-1][1:]
        
        recommended_scores: Dict[int, float] = {}
        
        # Get products already interacted by the target user
        user_interacted_product_indices = np.where(interaction_matrix[target_user_idx] > 0)[0]
        user_interacted_product_ids = {all_product_ids[i] for i in user_interacted_product_indices}

        for sim_user_idx in similar_users_indices:
            similarity_score = user_similarity[target_user_idx, sim_user_idx]
            if similarity_score <= 0.0: # Only consider positive similarity
                continue

            sim_user_product_indices = np.where(interaction_matrix[sim_user_idx] > 0)[0]

            for product_idx in sim_user_product_indices:
                product_id = all_product_ids[product_idx]
                
                # Skip products already interacted by the target user
                if product_id in user_interacted_product_ids:
                    continue
                
                if product_id not in recommended_scores:
                    recommended_scores[product_id] = 0.0
                recommended_scores[product_id] += interaction_matrix[sim_user_idx, product_idx] * similarity_score

        sorted_recommendations = sorted(recommended_scores.items(), key=lambda item: item[1], reverse=True)
        
        if not sorted_recommendations:
            logger.info(f"No recommendations found via collaborative filtering for user {target_user_id}. Falling back to popular products.")
            return self.get_popular_products(num_recommendations)
            
        return [product_id for product_id, score in sorted_recommendations[:num_recommendations]]

    def get_popular_products(self, num_recommendations: int = 5) -> List[int]:
        # 嘗試從 OrderItem 中獲取熱門產品
        popular_products_by_purchase = self.db.query(
                                Product.id,
                                func.sum(OrderItem.quantity).label('total_quantity_sold')
                            ) \
                            .join(OrderItem, Product.id == OrderItem.product_id) \
                            .group_by(Product.id) \
                            .order_by(func.sum(OrderItem.quantity).desc()) \
                            .limit(num_recommendations) \
                            .all()
        
        result_ids = [p.id for p in popular_products_by_purchase]
        
        # 如果購買數據不足，則從所有產品中隨機選擇或按 ID 順序選擇補齊
        if len(result_ids) < num_recommendations:
            remaining_needed = num_recommendations - len(result_ids)
            # 獲取所有現有產品 ID
            all_product_ids_in_db = [p.id for p in self.db.query(Product.id).all()]
            
            # 從所有產品中，排除已經在結果中的，並隨機選擇或按 ID 順序選擇補齊
            additional_products = []
            if all_product_ids_in_db:
                # 排除已選中的產品
                available_for_filler = [p_id for p_id in all_product_ids_in_db if p_id not in result_ids]
                # 簡單地取前幾個作為補充，或者可以隨機取樣
                additional_products = available_for_filler[:remaining_needed]

            result_ids.extend(additional_products)
        
        return result_ids[:num_recommendations] # 確保最終返回的數量不多於 num_recommendations
