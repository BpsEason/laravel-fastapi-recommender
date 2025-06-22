<?php

namespace App\Http\Controllers;

use App\Models\Eloquent\Product;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Services\RecommendationService;
use App\Models\Eloquent\UserInteraction; // 引入 UserInteraction 模型
use Illuminate\Support\Facades\Log; // 引入 Log Facade

class ProductController extends Controller
{
    protected $recommendationService;

    public function __construct(RecommendationService $recommendationService)
    {
        $this->recommendationService = $recommendationService;
    }

    public function show(Request $request, $id)
    {
        $product = Product::with('category')->findOrFail($id);
        $recommendedProducts = collect();

        if (Auth::check()) {
            $user = Auth::user();
            try {
                // 記錄用戶互動，自動填充 created_at
                UserInteraction::create([
                    'user_id' => $user->id,
                    'product_id' => $product->id,
                    'interaction_type' => 'view',
                    // 'timestamp' 欄位如果存在且需要自動填充，可以在 migration 中設置 default NOW()
                    // 或者在此手動填充 'timestamp' => now(), 如果模型沒有自動時間戳處理
                ]);
                Log::info("User interaction logged: user {$user->id} viewed product {$product->id}.");
            } catch (\Exception $e) {
                Log::error("Failed to log user interaction: {$e->getMessage()}");
            }

            $recommendedProducts = $this->recommendationService->getRecommendations($user->id);
            
            // 過濾掉當前正在查看的商品
            $recommendedProducts = $recommendedProducts->filter(function($item) use ($product) {
                return $item->id !== $product->id;
            });
        } else {
            Log::info("Guest user viewing product {$product->id}. No personalized recommendations.");
            // 訪客可以提供熱門商品推薦，作為非登入用戶的冷啟動
            $recommendedProducts = $this->recommendationService->getPopularProducts(5); 
            // 再次過濾掉當前正在查看的商品
            $recommendedProducts = $recommendedProducts->filter(function($item) use ($product) {
                return $item->id !== $product->id;
            });
        }

        return view('product_detail', compact('product', 'recommendedProducts'));
    }
}
