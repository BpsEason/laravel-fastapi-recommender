<?php

namespace App\Http\Controllers;

use App\Models\Eloquent\Product;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Services\RecommendationService;

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
            \App\Models\Eloquent\UserInteraction::create([
                'user_id' => $user->id,
                'product_id' => $product->id,
                'interaction_type' => 'view',
            ]);

            $recommendedProducts = $this->recommendationService->getRecommendations($user->id);
            
            $recommendedProducts = $recommendedProducts->filter(function($item) use ($product) {
                return $item->id !== $product->id;
            });
        }

        return view('product_detail', compact('product', 'recommendedProducts'));
    }
}
