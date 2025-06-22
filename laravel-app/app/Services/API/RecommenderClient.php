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
     * 考慮到這是一個「觸發」而非「等待結果」的場景，可以設定較短的超時。
     *
     * @param int $userId
     * @return bool
     */
    public function recalculateRecommendations(int $userId): bool
    {
        $endpoint = "{\->fastApiUrl}/recommendations/recalculate/{\}";

        try {
            // 使用 timeout(2) 確保不會長時間阻塞 Laravel 請求
            // 如果希望更徹底的「非同步」，則需要結合 Laravel Queue Job
            $response = Http::timeout(2)->post($endpoint);

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
     * 從 FastAPI 服務直接獲取推薦結果。
     *
     * @param int $userId
     * @param int $numRecommendations
     * @return array|null
     */
    public function getDirectRecommendations(int $userId, int $numRecommendations = 5): ?array
    {
        $endpoint = "{\->fastApiUrl}/recommendations/{\}?num_recommendations={$numRecommendations}";

        try {
            $response = Http::timeout(5)->get($endpoint); // 這裡需要等待結果，超時可以稍長

            if ($response->successful()) {
                return $response->json();
            } else {
                Log::error("RecommenderClient: Failed to get direct recommendations for user {$userId}. Status: {$response->status()} Body: {$response->body()}");
                return null;
            }
        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::error("RecommenderClient: Connection error trying to get direct recommendations for user {$userId}: {$e->getMessage()}");
            return null;
        } catch (\Exception $e) {
            Log::error("RecommenderClient: Unexpected error calling FastAPI direct recommendation API for user {$userId}: {$e->getMessage()}");
            return null;
        }
    }
}
