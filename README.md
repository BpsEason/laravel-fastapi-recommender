# 🚀 Laravel x FastAPI 推薦系統：跨語言微服務架構

## 💡 專案概述

本專案展示了一個現代化的**跨語言微服務架構**，整合 **Laravel**（PHP）與 **FastAPI**（Python），模擬電商平台的商品推薦功能。Laravel 負責核心業務邏輯，FastAPI 提供高效能推薦服務，並以**唯讀權限**連接到 Laravel 的 MySQL 資料庫獲取數據。**Redis** 作為高效快取層和跨服務通訊橋樑。專案採用 **Docker** 實現容器化部署，並整合 **GitHub Actions** 實現自動化 CI/CD，強調**可擴展性、可維護性與容器化**的設計理念。

**[查看專案源碼](https://github.com/BpsEason/laravel-fastapi-recommender.git)**

## 🎯 專案目標

- **跨語言整合**：透過 Redis 實現 Laravel 與 FastAPI 的無縫通訊。
- **高效能推薦系統**：FastAPI 從共享資料庫讀取數據，執行協同過濾演算法，並將結果快取至 Redis。
- **微服務架構**：明確職責劃分，提升系統靈活性和可維護性。
- **自動化 CI/CD**：使用 GitHub Actions 實現測試與部署自動化。
- **容器化部署**：透過 Docker 和 Docker Compose 簡化環境配置。

## 🏛️ 技術架構圖

```mermaid
graph TD
    A[用戶瀏覽器] -->|HTTP/HTTPS| B(Laravel 應用)
    B -->|請求推薦 (user_id)| C(Redis 快取)
    C -->|快取命中?| B
    C -->|快取未命中| D(FastAPI 推薦服務)
    D -->|唯讀查詢| E(MySQL 資料庫<br/>(Laravel 主資料庫))
    E -->|用戶/商品/互動數據| D
    D -->|計算推薦結果| F(Redis 快取)
    F -->|快取結果 (TTL)| C
    C -->|返回商品 ID| B
    B -->|查詢商品詳情| E
    B -->|顯示推薦商品| A
```

**流程說明**：
1. 用戶透過瀏覽器訪問 Laravel 應用，觸發商品推薦需求。
2. Laravel 向 Redis 查詢用戶的推薦快取。
3. 若快取命中，Laravel 直接獲取商品 ID 並顯示。
4. 若快取未命中，Laravel 呼叫 FastAPI 服務重新計算。
5. FastAPI 以唯讀權限從 MySQL 資料庫獲取用戶、商品和互動數據。
6. FastAPI 執行推薦演算法（如協同過濾），並將結果快取至 Redis（設定 TTL）。
7. Laravel 從 Redis 獲取推薦結果，查詢 MySQL 獲取商品詳情並顯示給用戶。

## 📂 專案結構

```
laravel-fastapi-recommender/
├── laravel-app/                            # Laravel 專案
│   ├── app/
│   │   ├── Http/Controllers/ProductController.php
│   │   ├── Models/Eloquent/                # Eloquent 模型
│   │   │   ├── User.php
│   │   │   ├── Product.php
│   │   │   ├── Category.php
│   │   │   ├── Order.php
│   │   │   ├── OrderItem.php
│   │   │   └── UserInteraction.php
│   │   └── Services/
│   │       ├── API/RecommenderClient.php   # FastAPI API 客戶端
│   │       └── RecommendationService.php   # 推薦邏輯
│   ├── resources/views/
│   │   ├── welcome.blade.php
│   │   └── product_detail.blade.php
│   ├── routes/web.php
│   ├── .env.example
│   └── Dockerfile
├── recommender-service/                    # FastAPI 微服務
│   ├── app/
│   │   ├── api/v1/routes.py               # API 路由
│   │   ├── core/config.py                 # 配置管理
│   │   ├── data/data_loader.py            # 數據載入
│   │   ├── models/                        # SQLAlchemy 模型
│   │   │   ├── db.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── interaction.py
│   │   ├── services/recommender_logic.py  # 推薦演算法
│   │   ├── main.py                        # FastAPI 應用
│   │   └── dependencies.py                # 依賴注入
│   ├── tests/test_routes.py               # FastAPI 測試
│   ├── Dockerfile
│   └── requirements.txt
├── redis/
│   ├── redis.conf                         # Redis 配置
│   └── init-redis-data.sh                 # Redis 數據初始化
├── .github/workflows/deploy.yml           # GitHub Actions CI/CD
├── docker-compose.yml                     # Docker Compose 配置
└── README.md
```

## 🛠️ 技術棧

- **後端框架**：
  - **Laravel 10** (PHP)：核心業務邏輯（用戶、訂單、前台界面）。
  - **FastAPI** (Python)：高效能推薦服務，內建 Swagger UI。
- **資料庫與快取**：
  - **MySQL 8.0**：Laravel 主資料庫，FastAPI 唯讀訪問。
  - **Redis**：高效鍵值儲存，作為快取與跨服務通訊。
- **數據處理與演算法**：
  - **SQLAlchemy**：FastAPI 的 Python ORM，處理資料庫操作。
  - **Pandas & NumPy**：數據處理與數值計算。
  - **scikit-learn**：實現協同過濾（餘弦相似度）。
- **容器化**：
  - **Docker**：確保環境一致性。
  - **Docker Compose**：一鍵啟動多容器服務。
- **CI/CD**：
  - **GitHub Actions**：自動化測試與部署流程。
- **測試**：
  - **PHPUnit**：Laravel 應用測試。
  - **Pytest**：FastAPI 服務測試。

## 🚀 快速開始

### 前置條件
- Docker Desktop
- Git

### 步驟

1. **複製專案**
   ```bash
   git clone https://github.com/BpsEason/laravel-fastapi-recommender.git
   cd laravel-fastapi-recommender
   ```

2. **啟動服務**
   使用 Docker Compose 一鍵啟動：
   ```bash
   docker-compose up --build -d
   ```

3. **配置 Laravel**
   安裝依賴、執行資料庫遷移、填充測試數據並生成應用密鑰：
   ```bash
   docker-compose exec laravel-app composer install
   docker-compose exec laravel-app php artisan migrate --force
   docker-compose exec laravel-app php artisan db:seed
   docker-compose exec laravel-app php artisan key:generate
   ```

4. **（可選）初始化 Redis**
   如需預設數據，執行 Redis 初始化腳本：
   ```bash
   bash ./redis/init-redis-data.sh
   ```

5. **訪問應用**
   - **Laravel 前台**： [http://localhost:8000](http://localhost:8000)
   - **FastAPI Swagger UI**： [http://localhost:8001/docs](http://localhost:8001/docs)

## 🧪 運行測試

### Laravel 測試
```bash
docker-compose exec laravel-app php artisan test
```

### FastAPI 測試
```bash
docker-compose exec recommender-service pytest
```

## 🌐 CI/CD 流程

專案使用 **GitHub Actions** 實現自動化 CI/CD，當程式碼推送或提交至 `main` 分支時，執行以下流程：

- **Laravel CI**：
  - 安裝 Composer 依賴。
  - 運行 PHPUnit 測試。
  - 驗證路由與資料庫遷移。
- **FastAPI CI**：
  - 安裝 Python 依賴。
  - 運行 Pytest 測試。

詳情請參考 `.github/workflows/deploy.yml`。

## ✨ 專案亮點

本專案模擬了**跨語言微服務整合**場景，結合 **Laravel** 處理核心業務邏輯與統一資料庫，透過 **Redis** 串接 **FastAPI** 實現高效能推薦系統。FastAPI 以**唯讀權限**直接連接到 Laravel 的 MySQL 資料庫，確保數據即時性與一致性，無需複雜的數據同步。

專案採用**模組化分層設計**，提升**可讀性與可維護性**，以**可擴展性、可測試性與容器化**為核心，展現了我在異質系統協作、高效快取設計、**CI/CD 自動化**以及資料一致性考量上的技術能力。此專案充分證明了我構建穩定、高效且易於維護的現代化應用程式的綜合實力。