<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Pet extends Model 
{
    protected $fillable = ['user_id','nama','ras','tanggal_lahir'];
    public function owner() { return $this->belongsTo(User::class); }
}
