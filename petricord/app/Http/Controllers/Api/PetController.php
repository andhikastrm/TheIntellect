<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Pet;
use Illuminate\Http\Request;

class PetController extends Controller
{
    /**
     * Tampilkan semua data hewan.
     */
    public function index()
    {
        return response()->json(Pet::with('owner')->get());
    }

    /**
     * Tambah data hewan baru.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'nama' => 'required|string|max:100',
            'ras' => 'nullable|string|max:100',
            'tanggal_lahir' => 'nullable|date',
        ]);

        $pet = Pet::create([
            'user_id' => auth()->id(),
            'nama' => $validated['nama'],
            'ras' => $validated['ras'] ?? null,
            'tanggal_lahir' => $validated['tanggal_lahir'] ?? null,
        ]);

        return response()->json($pet, 201);
    }

    /**
     * Update data hewan.
     */
    public function update(Request $request, Pet $pet)
    {
        $validated = $request->validate([
            'nama' => 'sometimes|required|string|max:100',
            'ras' => 'nullable|string|max:100',
            'tanggal_lahir' => 'nullable|date',
        ]);

        $pet->update($validated);

        return response()->json($pet);
    }

    /**
     * Hapus data hewan.
     */
    public function destroy($id)
    {
        $pet = Pet::findOrFail($id);
        $pet->delete();

        return response()->json(['message' => 'Data hewan berhasil dihapus']);
    }
}
