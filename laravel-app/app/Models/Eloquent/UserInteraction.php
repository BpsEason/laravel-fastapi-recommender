<?php

namespace App\Models\Eloquent;

use Illuminate\Database\Eloquent\Model;

class UserInteraction extends Model
{
    protected $table = 'user_interactions';

    // Laravel 預設會自動管理 created_at 和 updated_at
    // 如果資料庫有 timestamp 欄位，但你希望 Laravel 自動填充它，
    // 且不使用 created_at/updated_at，你可以設定：
    // public $timestamps = false;
    // protected $dates = ['timestamp']; // 確保 timestamp 被視為日期時間
    // 但通常建議使用 Laravel 默認的 created_at/updated_at。
    // 如果 timestamp 欄位僅為額外記錄，且 created_at 已經記錄了創建時間，
    // 則不需要特別處理 timestamp 欄位的自動填充。
    // 這裡我們假設資料庫 Migration 會包含 created_at/updated_at。
    // 如果資料表有 'timestamp' 欄位，且希望自動更新為當前時間，請確保 migration 中有設置 default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP。
    // 否則，在 create 時手動傳入 。
    protected $fillable = [
        'user_id',
        'product_id',
        'interaction_type',
        // 'timestamp', // 只有在明確需要，且不同於 created_at 時才放在這裡，並手動填充或通過 DB 默認值
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
