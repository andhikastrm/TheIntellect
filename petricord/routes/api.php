<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\PetController;
use App\Http\Controllers\Api\DeviceController;

// ✅ Route untuk tes API (publik)
Route::get('/ping', fn() => response()->json(['message' => 'API aktif dan berjalan!']));

// ✅ Route publik (register & login)
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);

// ✅ Semua route ini butuh login token (Sanctum)
Route::middleware('auth:sanctum')->group(function () {
    // Info user login
    Route::get('/user', fn() => auth()->user());

    // Logout
    Route::post('/logout', [AuthController::class, 'logout']);

    // CRUD Devices
    Route::apiResource('devices', DeviceController::class);

    // CRUD Pets
    Route::apiResource('pets', PetController::class);
});
