#!/usr/bin/env python3
"""
TensorRT vs PyTorch Benchmark Script - 3-Way Comparison
Tests: TensorRT GPU, PyTorch GPU, PyTorch CPU
"""

import time
import numpy as np
import torch

def benchmark_yolo(model, num_frames=100, warmup_frames=10):
    """Benchmark YOLO detection speed."""
    # Create test frame (640x480 RGB)
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    # Warm up
    for _ in range(warmup_frames):
        model(test_frame, verbose=False)

    # Benchmark
    start_time = time.time()
    for _ in range(num_frames):
        model(test_frame, verbose=False)
    elapsed = time.time() - start_time

    avg_ms = (elapsed / num_frames) * 1000
    fps = num_frames / elapsed

    return avg_ms, fps

def main():
    from ultralytics import YOLO

    print("=" * 70)
    print("TensorRT vs PyTorch GPU vs PyTorch CPU Benchmark")
    print("=" * 70)
    print()

    # Check hardware
    print("Hardware Detection:")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA version: {torch.version.cuda}")
    print(f"  PyTorch version: {torch.__version__}")
    print()

    # Download model if needed
    print("Downloading YOLO model if needed...")
    YOLO("yolo26m.pt")
    print()

    results = {}

    # Test 1: TensorRT (if NVIDIA GPU available)
    if torch.cuda.is_available():
        print("-" * 70)
        print("Test 1: TensorRT on NVIDIA GPU")
        print("-" * 70)
        print("  Initializing TensorRT (will export on first run, ~1-2 min)...")

        model_tensorrt = YOLO("yolo26m.pt")
        # Export to TensorRT
        try:
            model_tensorrt.export(format='engine', device=0, half=True, workspace=4)
            print("  ✅ TensorRT export complete!")

            # Load the TensorRT engine
            model_tensorrt = YOLO("yolo26m.engine")
            print("  ✅ Loaded TensorRT engine")
        except Exception as e:
            print(f"  ⚠️  TensorRT export failed: {e}")
            print("  Falling back to PyTorch GPU...")
            model_tensorrt = YOLO("yolo26m.pt")

        print("  Warming up (10 frames)...")
        print("  Running benchmark (100 frames)...")
        avg_ms, fps = benchmark_yolo(model_tensorrt)
        results['tensorrt'] = (fps, avg_ms)

        print()
        print("  Results:")
        print(f"    FPS: {fps:.1f}")
        print(f"    Latency: {avg_ms:.1f}ms")
        print()

    # Test 2: PyTorch on GPU (without TensorRT)
    if torch.cuda.is_available():
        print("-" * 70)
        print("Test 2: PyTorch on NVIDIA GPU (no TensorRT)")
        print("-" * 70)
        print("  Loading PyTorch model on GPU...")

        # Load fresh model, force to GPU without TensorRT
        model_pytorch_gpu = YOLO("yolo26m.pt")
        # Make sure it's on GPU
        model_pytorch_gpu.to('cuda')

        print("  Warming up (10 frames)...")
        print("  Running benchmark (100 frames)...")
        avg_ms, fps = benchmark_yolo(model_pytorch_gpu)
        results['pytorch_gpu'] = (fps, avg_ms)

        print()
        print("  Results:")
        print(f"    FPS: {fps:.1f}")
        print(f"    Latency: {avg_ms:.1f}ms")
        print()

    # Test 3: PyTorch on CPU
    print("-" * 70)
    print("Test 3: PyTorch on CPU (baseline)")
    print("-" * 70)
    print("  Loading PyTorch model on CPU...")

    # Load model explicitly on CPU
    model_cpu = YOLO("yolo26m.pt")
    model_cpu.to('cpu')

    print("  Warming up (10 frames)...")
    print("  Running benchmark (100 frames)...")
    avg_ms, fps = benchmark_yolo(model_cpu)
    results['cpu'] = (fps, avg_ms)

    print()
    print("  Results:")
    print(f"    FPS: {fps:.1f}")
    print(f"    Latency: {avg_ms:.1f}ms")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    if 'tensorrt' in results and 'pytorch_gpu' in results and 'cpu' in results:
        fps_tensorrt, ms_tensorrt = results['tensorrt']
        fps_pytorch_gpu, ms_pytorch_gpu = results['pytorch_gpu']
        fps_cpu, ms_cpu = results['cpu']

        # Calculate speedups
        tensorrt_vs_pytorch = fps_tensorrt / fps_pytorch_gpu
        tensorrt_vs_cpu = fps_tensorrt / fps_cpu
        gpu_vs_cpu = fps_pytorch_gpu / fps_cpu

        print(f"  TensorRT (NVIDIA GPU):  {fps_tensorrt:6.1f} FPS ({ms_tensorrt:6.1f}ms)")
        print(f"  PyTorch GPU:            {fps_pytorch_gpu:6.1f} FPS ({ms_pytorch_gpu:6.1f}ms)")
        print(f"  PyTorch CPU:            {fps_cpu:6.1f} FPS ({ms_cpu:6.1f}ms)")
        print()
        print(f"  🚀 TensorRT vs PyTorch GPU: {tensorrt_vs_pytorch:.2f}x faster")
        print(f"  📊 GPU vs CPU (PyTorch):    {gpu_vs_cpu:.1f}x faster")
        print(f"  🎯 TensorRT vs CPU (total): {tensorrt_vs_cpu:.1f}x faster")
        print()
        print("=" * 70)
        print("📋 Add this table to your README:")
        print("=" * 70)
        print()
        print("| Backend | Hardware | FPS | Latency | TensorRT Speedup | vs CPU |")
        print("|---------|----------|-----|---------|------------------|--------|")
        print(f"| **TensorRT** | NVIDIA GPU | **{fps_tensorrt:.1f}** | {ms_tensorrt:.1f}ms | **{tensorrt_vs_pytorch:.2f}x** | {tensorrt_vs_cpu:.1f}x |")
        print(f"| PyTorch | NVIDIA GPU | {fps_pytorch_gpu:.1f} | {ms_pytorch_gpu:.1f}ms | 1.0x | {gpu_vs_cpu:.1f}x |")
        print(f"| PyTorch | CPU | {fps_cpu:.1f} | {ms_cpu:.1f}ms | - | 1.0x |")
        print()
        print(f"**TensorRT provides {tensorrt_vs_pytorch:.2f}x speedup over PyTorch on the same NVIDIA GPU!**")

    elif 'tensorrt' in results and 'cpu' in results:
        fps_tensorrt, ms_tensorrt = results['tensorrt']
        fps_cpu, ms_cpu = results['cpu']
        speedup = fps_tensorrt / fps_cpu

        print(f"  TensorRT (NVIDIA GPU): {fps_tensorrt:.1f} FPS ({ms_tensorrt:.1f}ms)")
        print(f"  PyTorch (CPU):         {fps_cpu:.1f} FPS ({ms_cpu:.1f}ms)")
        print()
        print(f"  🚀 SPEEDUP: {speedup:.2f}x faster with TensorRT!")

    else:
        fps_cpu, ms_cpu = results['cpu']
        print(f"  PyTorch (CPU only): {fps_cpu:.1f} FPS ({ms_cpu:.1f}ms)")
        print()
        print("  ⚠️  Run on NVIDIA GPU to measure TensorRT speedup!")

if __name__ == "__main__":
    main()
