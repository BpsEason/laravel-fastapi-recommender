<?php

namespace App\Services\API;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class RecommenderClient
{
    protected $fastApiUrl;

    public function __construct()
    {
        $this->fastApiUrl = env('FASTAPI_RECOMMENDER_URL', 'http://localhost:8001/api/v1');
    }

    /**
     * 呼叫 FastAPI 服務，觸發推薦邏輯的重新計算。
     *
     * @param int $userId
     * @return bool
     */
    public function recalculateRecommendations(int $userId): bool
    {
        $endpoint = "{\->fastApiUrl}/recommendations/recalculate/{\}";
        
        try {
            $response = Http::timeout(5)->post($endpoint); // 設定超時時間

            if ($response->successful()) {
                Log::info("RecommenderClient: Successfully triggered FastAPI recalculation for user {$userId}.");
                return true;
            } else {
                Log::error("RecommenderClient: Failed to trigger FastAPI recalculation for user {$userId}. Status: {$response->status()} Body: {$response->body()}");
                return false;
            }
        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::error("RecommenderClient: Connection error to FastAPI for user {$userId}: {$e->getMessage()}");
            return false;
        } catch (\Exception $e) {
            Log::error("RecommenderClient: Unexpected error calling FastAPI recalculate API for user {$userId}: {$e->getMessage()}");
            return false;
        }
    }

    /**
     * (選作) 如果 FastAPI 有直接獲取推薦的 API，可以這樣封裝
     * @param int $userId
     * @param int $numRecommendations
     * @return array|null
     */
    public function getDirectRecommendations(int $userId, int $numRecommendations = 5): ?array
    {
        $endpoint = "{\->fastApiUrl}/recommendations/{\}?num_recommendations={$numRecommendations}";
        
        try {
            $response = Http::timeout(5)->get($endpoint);

            if ($response->successful()) {
                return $response->json();
            } else {
                Log::error("RecommenderClient: Failed to get direct recommendations for user {$userId}. Status: {$response->status()} Body: {$response->body()}");
                return null;
            }
        } catch (\Exception $e) {
            Log::error("RecommenderClient: Error calling FastAPI direct recommendation API for user {$userId}: {$e->getMessage()}");
            return null;
        }
    }
}
