<?php

namespace App\Services;

use Illuminate\Support\Facades\Redis;
use Illuminate\Support\Facades\Log;
use App\Models\Eloquent\Product;
use App\Services\API\RecommenderClient;
use Illuminate\Support\Collection;

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
     *
     * @param int $userId
     * @param int $numRecommendations
     * @return \Illuminate\Support\Collection<Product>
     */
    public function getRecommendations(int $userId, int $numRecommendations = 5): Collection
    {
        $cacheKey = "user:{\}:recommendations";

        // 1. 嘗試從 Redis 快取中獲取
        $cachedProductIdsJson = $this->redis->get($cacheKey);

        if ($cachedProductIdsJson) {
            Log::info("RecommendationService: Fetched recommendations for user {$userId} from Redis cache.");
            $recommendedProductIds = json_decode($cachedProductIdsJson, true);
            return Product::whereIn('id', $recommendedProductIds)->get();
        }

        // 2. 如果 Redis 沒有快取，觸發 FastAPI 重新計算 (透過 RecommenderClient)
        Log::info("RecommendationService: Cache miss for user {$userId}. Triggering FastAPI recalculation via client.");
        
        $this->recommenderClient->recalculateRecommendations($userId);
        
        // 為了演示，我們可以稍作等待再嘗試從 Redis 讀取，實際生產應考慮非同步處理或事件
        sleep(1); 

        $updatedCachedProductIdsJson = $this->redis->get($cacheKey);
        if ($updatedCachedProductIdsJson) {
            $recommendedProductIds = json_decode($updatedCachedProductIdsJson, true);
            return Product::whereIn('id', $recommendedProductIds)->get();
        }
        
        Log::warning("RecommendationService: No recommendations found for user {$userId} after recalculation.");
        return collect();
    }
}
