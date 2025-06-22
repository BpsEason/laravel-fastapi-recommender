<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth; # Added for Auth facade
use App\Http\Controllers\ProductController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/

Route::get('/', function () {
    return view('welcome');
});

Route::get('/products/{id}', [ProductController::class, 'show'])->name('products.show');

// Dummy auth routes for testing purposes (you'd use Laravel Breeze/Jetstream normally)
Route::get('/login', function () { return 'Login Page'; })->name('login');
Route::get('/register', function () { return 'Register Page'; })->name('register');
Route::get('/logout', function () { return 'Logged Out'; })->name('logout');
// Simulating a logged-in user for testing
Route::get('/simulate-login/{userId}', function ($userId) {
    $user = App\Models\Eloquent\User::find($userId);
    if ($user) {
        Auth::login($user);
        return "User $user->name (ID: $user->id) logged in.";
    }
    return "User not found.";
});
