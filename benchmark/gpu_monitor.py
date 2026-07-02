import pynvml
import csv
import time
import sys
import os

def monitor(gpu_id=0, interval=0.5, output="gpu_metrics.csv"):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
    
    print(f"[GPU Monitor] Recording GPU {gpu_id} → {output} (Ctrl+C to stop)")
    
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "mem_used_mb", "mem_total_mb", "gpu_util_%", "mem_util_%"])
        
        try:
            while True:
                mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                ts = round(time.time(), 3)
                
                writer.writerow([
                    ts,
                    mem.used // (1024**2),
                    mem.total // (1024**2),
                    util.gpu,
                    util.memory
                ])
                f.flush()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[GPU Monitor] Stopped.")
        finally:
            pynvml.nvmlShutdown()

if __name__ == "__main__":
    gpu_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    output = sys.argv[2] if len(sys.argv) > 2 else "gpu_metrics.csv"
    monitor(gpu_id=gpu_id, output=output)