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

class Recommender:
    def __init__(self, db: Session):
        self.db = db
        self.data_loader = DataLoader(db)

    def get_interaction_matrix_and_mappings(self) -> Tuple[pd.DataFrame, dict, dict]:
        df, user_to_idx, product_to_idx = self.data_loader.load_interaction_data()

        if df.empty:
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
        if matrix.shape[0] < 2 or np.all(matrix == 0):
            return np.array([[]])
        
        return cosine_similarity(matrix)

    def recommend_for_user(self, target_user_id: int, num_recommendations: int = 5) -> List[int]:
        interaction_matrix, all_user_ids, all_product_ids = self.get_interaction_matrix_and_mappings()

        if not all_user_ids or not all_product_ids or target_user_id not in all_user_ids:
            return self.get_popular_products(num_recommendations)

        try:
            target_user_idx = all_user_ids.index(target_user_id)
        except ValueError:
            return self.get_popular_products(num_recommendations)

        user_similarity = self.calculate_similarity(interaction_matrix)

        if user_similarity.size == 0 or target_user_idx >= user_similarity.shape[0]:
            return self.get_popular_products(num_recommendations)

        similar_users_indices = user_similarity[target_user_idx].argsort()[::-1][1:]
        
        recommended_scores: Dict[int, float] = {}
        
        user_interacted_product_indices = np.where(interaction_matrix[target_user_idx] > 0)[0]
        user_interacted_product_ids = {all_product_ids[i] for i in user_interacted_product_indices}

        for sim_user_idx in similar_users_indices:
            similarity_score = user_similarity[target_user_idx, sim_user_idx]
            if similarity_score <= 0.0:
                continue

            sim_user_product_indices = np.where(interaction_matrix[sim_user_idx] > 0)[0]

            for product_idx in sim_user_product_indices:
                product_id = all_product_ids[product_idx]
                
                if product_id in user_interacted_product_ids:
                    continue
                
                if product_id not in recommended_scores:
                    recommended_scores[product_id] = 0.0
                recommended_scores[product_id] += interaction_matrix[sim_user_idx, product_idx] * similarity_score

        sorted_recommendations = sorted(recommended_scores.items(), key=lambda item: item[1], reverse=True)
        
        if not sorted_recommendations:
            return self.get_popular_products(num_recommendations)
            
        return [product_id for product_id, score in sorted_recommendations[:num_recommendations]]

    def get_popular_products(self, num_recommendations: int = 5) -> List[int]:
        popular_products = self.db.query(
                                OrderItem.product_id,
                                func.count(OrderItem.product_id).label('purchase_count')
                            ) \
                            .group_by(OrderItem.product_id) \
                            .order_by(func.count(OrderItem.product_id).desc()) \
                            .limit(num_recommendations) \
                            .all()
        
        if len(popular_products) < num_recommendations:
            existing_popular_ids = [item.product_id for item in popular_products]
            remaining_needed = num_recommendations - len(popular_products)
            
            additional_products = self.db.query(Product.id).filter(Product.id.notin_(existing_popular_ids)).limit(remaining_needed).all()
            
            return existing_popular_ids + [p.id for p in additional_products]

        return [item.product_id for item in popular_products]
