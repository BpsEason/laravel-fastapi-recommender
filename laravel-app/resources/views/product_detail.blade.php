<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Detail - {{ $product->name }}</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { max-width: 960px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .product-info { display: flex; gap: 20px; margin-bottom: 30px; }
        .product-image { flex: 1; text-align: center; }
        .product-image img { max-width: 100%; height: auto; border-radius: 5px; }
        .product-details { flex: 2; }
        .product-details p { margin: 5px 0; }
        .price { font-size: 1.5em; color: #e44d26; font-weight: bold; }
        .recommendations { margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px; }
        .recommendations h2 { margin-bottom: 20px; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .product-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; text-align: center; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .product-card img { max-width: 100%; height: 150px; object-fit: contain; margin-bottom: 10px; }
        .product-card h3 { font-size: 1.1em; margin: 10px 0; }
        .product-card .price { font-size: 1.2em; color: #e44d26; }
        .product-card a { text-decoration: none; color: inherit; }
        .product-card a:hover h3 { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ $product->name }}</h1>

        <div class="product-info">
            <div class="product-image">
                <img src="{{ $product->image_url ?? 'https://via.placeholder.com/250x250?text=Product+Image' }}" alt="{{ $product->name }}">
            </div>
            <div class="product-details">
                <p><strong>Category:</strong> {{ $product->category->name ?? 'N/A' }}</p>
                <p><strong>Description:</strong> {{ $product->description }}</p>
                <p class="price">$ {{ number_format($product->price, 2) }}</p>
                <p><strong>In Stock:</strong> {{ $product->stock }}</p>
                <button style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">Add to Cart</button>
            </div>
        </div>

        @if($recommendedProducts->isNotEmpty())
            <div class="recommendations">
                <h2>Recommended for You</h2>
                <div class="product-grid">
                    @foreach($recommendedProducts as $recProduct)
                        <div class="product-card">
                            <a href="{{ route('products.show', $recProduct->id) }}">
                                <img src="{{ $recProduct->image_url ?? 'https://via.placeholder.com/150x150?text=Product+Image' }}" alt="{{ $recProduct->name }}">
                                <h3>{{ $recProduct->name }}</h3>
                                <p class="price">$ {{ number_format($recProduct->price, 2) }}</p>
                            </a>
                        </div>
                    @endforeach
                </div>
            </div>
        @else
            @auth
                <div class="recommendations">
                    <h2>No Recommendations Yet</h2>
                    <p>We couldn't find any specific recommendations for you right now. Keep exploring!</p>
                </div>
            @else
                <div class="recommendations">
                    <h2>Login for Personalized Recommendations</h2>
                    <p>Login to get personalized product recommendations!</p>
                    <a href="/login" style="display: inline-block; padding: 10px 15px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Login Now</a>
                </div>
            @endauth
        @endif

        <div style="margin-top: 40px; text-align: center;">
            <a href="/" style="text-decoration: none; color: #007bff;">← Back to Home</a>
        </div>
    </div>
</body>
</html>
