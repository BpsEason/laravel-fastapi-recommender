<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Laravel x FastAPI Recommender</title>
        <style>
            body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background-color: #f0f2f5; }
            .container { text-align: center; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 20px; }
            p { color: #666; margin-bottom: 30px; }
            .links a {
                display: inline-block;
                padding: 10px 20px;
                margin: 0 10px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }
            .links a:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Laravel x FastAPI Recommender</h1>
            <p>This is a demonstration of a microservice architecture for product recommendations.</p>
            <div class="links">
                <a href="{{ route('products.show', 1) }}">View Product 1</a>
                <a href="{{ route('products.show', 2) }}">View Product 2</a>
                <a href="http://localhost:8001/docs" target="_blank">FastAPI Docs</a>
            </div>
            <p style="margin-top: 30px; font-size: 0.8em; color: #999;">
                To simulate user login for recommendations, navigate to: <br/>
                <code>http://localhost:8000/simulate-login/1</code> (for user ID 1) <br/>
                Then refresh a product page.
            </p>
        </div>
    </body>
</html>
