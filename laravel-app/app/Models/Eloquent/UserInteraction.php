<?php

namespace App\Models\Eloquent;

use Illuminate\Database\Eloquent\Model;

class UserInteraction extends Model
{
    protected $table = 'user_interactions';

    protected $fillable = [
        'user_id',
        'product_id',
        'interaction_type',
        'timestamp', // Optional, as Laravel handles created_at/updated_at by default
    ];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function product()
    {
        return $this->belongsTo(Product::class, 'product_id');
    }
}
