<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens; // ← Tambahan penting untuk API Token

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * Kolom yang bisa diisi (mass assignable)
     */
    protected $fillable = [
        'nama_pengguna',
        'email',
        'kata_sandi',
        'role',
        'nama_lengkap',
    ];

    public function owner()
    {
        return $this->belongsTo(Owner::class, 'user_id');
    }

    /**
     * Kolom yang disembunyikan dari JSON
     */
    protected $hidden = [
        'kata_sandi',
        'remember_token',
    ];

    /**
     * Konversi otomatis tipe data kolom
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
        ];
    }

    /**
     * Relasi ke model lain (contoh)
     */
    public function pets()
    {
        return $this->hasMany(Pet::class);
    }

    public function devices()
    {
        return $this->hasMany(Device::class);
    }
}
