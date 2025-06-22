from sqlalchemy.orm import Session
from ..models.order import OrderItem
from ..models.interaction import UserInteraction
from ..models.user import User
from ..models.product import Product
import pandas as pd
import numpy as np
from typing import Tuple, List
from sqlalchemy import func

class DataLoader:
    def __init__(self, db: Session):
        self.db = db

    def load_interaction_data(self) -> Tuple[pd.DataFrame, dict, dict]:
        """
        從資料庫載入用戶互動數據，並轉換為 Pandas DataFrame。
        同時返回 ID 到索引的映射，便於矩陣操作。
        """
        order_items_data = self.db.query(OrderItem.user_id, OrderItem.product_id).all()
        user_interactions_data = self.db.query(UserInteraction.user_id, UserInteraction.product_id, UserInteraction.interaction_type).all()

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
            elif interaction_type == 'purchase':
                score = 5
            all_interactions.append({'user_id': user_id, 'product_id': product_id, 'interaction_type': interaction_type, 'value': score})

        if not all_interactions:
            return pd.DataFrame(columns=['user_id', 'product_id', 'value']), {}, {}

        df = pd.DataFrame(all_interactions)
        df = df.groupby(['user_id', 'product_id'])['value'].max().reset_index()

        unique_users = df['user_id'].unique()
        unique_products = df['product_id'].unique()

        user_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}
        product_to_idx = {product_id: idx for idx, product_id in enumerate(unique_products)}

        return df, user_to_idx, product_to_idx

    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()
