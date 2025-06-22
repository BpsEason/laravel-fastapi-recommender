<?php

namespace App\Services;

use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\Log;
use App\Models\Eloquent\Product;
use App\Services\API\RecommenderClient;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache; // 引入 Cache Facade for file fallback

class RecommendationService
{
    protected $recommenderClient;
    protected $redis;

    public function __construct(RecommenderClient $recommenderClient)
    {
        $this->recommenderClient = $recommenderClient;
        $this->redis = Redis::connection();
    }

    /**
     * 從 Redis 或 FastAPI 獲取用戶推薦商品。
     * 考慮到冷啟動和容錯機制。
     *
     * @param int $userId
     * @param int $numRecommendations
     * @return \Illuminate\Support\Collection<Product>
     */
    public function getRecommendations(int $userId, int $numRecommendations = 5): Collection
    {
        $cacheKey = "user:{\}:recommendations";
        $fallbackCacheKey = "user:{\}:recommendations_fallback"; // For file cache

        // 1. 嘗試從 Redis 快取中獲取
        try {
            $cachedProductIdsJson = $this->redis->get($cacheKey);
            if ($cachedProductIdsJson) {
                Log::info("RecommendationService: Fetched recommendations for user {$userId} from Redis cache.");
                $recommendedProductIds = json_decode($cachedProductIdsJson, true);
                return Product::whereIn('id', $recommendedProductIds)->get();
            }
        } catch (\Exception $e) {
            Log::error("RecommendationService: Redis connection error or issue: {$e->getMessage()}. Falling back to file cache/direct API call.");
            // Redis 故障時，嘗試從檔案快取讀取
            $fallbackProductIds = Cache::get($fallbackCacheKey);
            if ($fallbackProductIds) {
                Log::info("RecommendationService: Fetched recommendations for user {$userId} from file fallback cache.");
                return Product::whereIn('id', $fallbackProductIds)->get();
            }
        }

        // 2. 如果 Redis 沒有快取 (或 Redis 故障且無 fallback 檔案快取)，觸發 FastAPI 重新計算
        Log::info("RecommendationService: Cache miss for user {$userId} or Redis issue. Triggering FastAPI recalculation.");

        // 觸發 FastAPI 異步重新計算 (假定 RecommenderClient 內部會處理非同步發送)
        // 在實際生產中，這裡可能會是 dispatch 一個 Laravel Job 到 Queue
        $fastApiCallSuccess = $this->recommenderClient->recalculateRecommendations($userId);

        if (!$fastApiCallSuccess) {
            Log::warning("RecommendationService: Failed to trigger FastAPI recalculation for user {$userId}.");
            // FastAPI 觸發失敗，嘗試返回熱門商品
            return $this->getPopularProducts($numRecommendations);
        }

        // 3. FastAPI 會將結果回寫到 Redis。
        // 由於是異步觸發，Laravel 不會立即拿到結果。
        // 為了演示目的，我們可以再次嘗試從 Redis 讀取（但這是同步行為，實際應避免）
        // 或者更合理的，是返回一個暫時的結果 (如熱門商品)，等待下次請求時快取生效。
        // 這裡暫時仍保留嘗試讀取邏輯，但增加獲取直接推薦作為快速回應
        $directRecommendations = $this->recommenderClient->getDirectRecommendations($userId, $numRecommendations);
        if ($directRecommendations) {
            Log::info("RecommendationService: Got direct recommendations for user {$userId} from FastAPI.");
            // 收到直接推薦後，也快取一份到檔案，以防 Redis 再次故障
            Cache::put($fallbackCacheKey, $directRecommendations, now()->addMinutes(10)); // 檔案快取時間短一點
            return Product::whereIn('id', $directRecommendations)->get();
        }

        Log::warning("RecommendationService: Could not get direct recommendations for user {$userId}. Falling back to popular products.");
        return $this->getPopularProducts($numRecommendations);
    }

    /**
     * 從資料庫獲取熱門商品作為冷啟動或 fallback 推薦。
     * @param int $numRecommendations
     * @return \Illuminate\Support\Collection<Product>
     */
    public function getPopularProducts(int $numRecommendations): Collection
    {
        Log::info("RecommendationService: Falling back to popular products.");
        // 這裡可以查詢 OrderItem 或 Product 的銷量
        // 為簡化，暫時直接取最新的或ID最小的幾個商品
        return Product::orderBy('id', 'asc')->limit($numRecommendations)->get();
    }
}
