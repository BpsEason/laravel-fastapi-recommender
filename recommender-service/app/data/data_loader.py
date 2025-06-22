from sqlalchemy.orm import Session
from ..models.order import OrderItem
from ..models.interaction import UserInteraction
from ..models.user import User
from ..models.product import Product
import pandas as pd
import numpy as np
from typing import Tuple, List
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, db: Session):
        self.db = db

    def load_interaction_data(self) -> Tuple[pd.DataFrame, dict, dict]:
        """
        從資料庫載入用戶互動數據，並轉換為 Pandas DataFrame。
        同時返回 ID 到索引的映射，便於矩陣操作。
        """
        try:
            order_items_data = self.db.query(OrderItem.user_id, OrderItem.product_id).all()
            user_interactions_data = self.db.query(UserInteraction.user_id, UserInteraction.product_id, UserInteraction.interaction_type).all()
        except Exception as e:
            logger.error(f"Error loading interaction data from DB: {e}")
            return pd.DataFrame(columns=['user_id', 'product_id', 'value']), {}, {}


        all_interactions = []
        for user_id, product_id in order_items_data:
            all_interactions.append({'user_id': user_id, 'product_id': product_id, 'interaction_type': 'purchase', 'value': 5})

        for user_id, product_id, interaction_type in user_interactions_data:
            score = 1
            if interaction_type == 'favorite':
                score = 4
            elif interaction_type == 'add_to_cart':
                score = 3
            elif interaction_type == 'click':
                score = 2
            elif interaction_type == 'purchase': # 如果同時有購買和 view 這種，以最高分算
                score = 5
            all_interactions.append({'user_id': user_id, 'product_id': product_id, 'interaction_type': interaction_type, 'value': score})

        if not all_interactions:
            logger.info("No interaction data found in database.")
            return pd.DataFrame(columns=['user_id', 'product_id', 'value']), {}, {}

        df = pd.DataFrame(all_interactions)
        # 對相同的 user_id, product_id，取最高的互動分數
        df = df.groupby(['user_id', 'product_id'])['value'].max().reset_index()

        unique_users = df['user_id'].unique()
        unique_products = df['product_id'].unique()

        user_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}
        product_to_idx = {product_id: idx for idx, product_id in enumerate(unique_products)}

        logger.info(f"Loaded {len(df)} unique interactions for {len(unique_users)} users and {len(unique_products)} products.")
        return df, user_to_idx, product_to_idx

    def get_all_products(self) -> List[Product]:
        try:
            return self.db.query(Product).all()
        except Exception as e:
            logger.error(f"Error loading all products from DB: {e}")
            return []

    def get_all_users(self) -> List[User]:
        try:
            return self.db.query(User).all()
        except Exception as e:
            logger.error(f"Error loading all users from DB: {e}")
            return []
