<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Device;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class DeviceController extends Controller
{
    // Tampilkan semua perangkat
    public function index()
    {
        return response()->json(Device::with('owner')->get());
    }

    // Tambah perangkat baru
    public function store(Request $request)
    {
            $validated = $request->validate([
                'nomor_seri' => 'required|string|unique:devices,nomor_seri|max:100',
                'status' => 'nullable|string|max:50',
                'lokasi' => 'nullable|string|max:255',
            ]);

            $validated['user_id'] = auth()->id();

            $device = Device::create($validated);
        return response()->json($device, 201);
    }
    // Tampilkan satu perangkat
    public function show($id)
    {
        $device = Device::with('owner')->findOrFail($id);
        return response()->json($device);
    }

    // Update data perangkat
    public function update(Request $request, $id)
    {
         $validated = $request->validate([
            'nomor_seri' => 'sometimes|required|string|max:100|unique:devices,nomor_seri,' . $device->id,
            'status' => 'nullable|string|max:50',
            'lokasi' => 'nullable|string|max:255',
        ]);
        $device->update($validated);
        return response()->json($device);
    }

    // Hapus perangkat
    public function destroy($id)
    {
        $device = Device::findOrFail($id);
        $device->delete();
        return response()->json(['message' => 'Perangkat berhasil dihapus']);
    }
}
