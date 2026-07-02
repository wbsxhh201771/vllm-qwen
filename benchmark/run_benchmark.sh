#!/bin/bash
set -e

HOST="http://localhost:8000"
RESULTS_DIR="./results/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo "=========================================="
echo " vLLM Benchmark | Qwen3-4B-GPTQ | 16GB"
echo " Results → $RESULTS_DIR"
echo "=========================================="

# 启动 GPU 监控（后台）
python /home/crh/vllm-qwen/benchmark/gpu_monitor.py 0 "$RESULTS_DIR/gpu_metrics.csv" &
GPU_PID=$!
sleep 2

run_stage() {
    local users=$1
    local spawn=$2
    local duration=$3
    local label=$4
    
    echo ""
    echo "▶ [$label] Users=$users | Spawn=$spawn/s | Duration=$duration"
    echo "─────────────────────────────────────────"
    
    locust -f /home/crh/vllm-qwen/benchmark/locustfile.py \
        --host "$HOST" \
        --users "$users" \
        --spawn-rate "$spawn" \
        --run-time "$duration" \
        --headless \
        --csv="$RESULTS_DIR/stage_${users}u" \
        --csv-full-history \
        --logfile="$RESULTS_DIR/stage_${users}u.log"
    
    echo "⏳ Cooling down 15s..."
    sleep 15
}

# ===== 阶梯测试 =====
run_stage 1  1  "2m"  "Baseline 单请求基线"
run_stage 8  2  "3m"  "Medium   中等并发"
run_stage 20 5  "3m"  "Stress   满载压力(max-num-seqs=16)"

# 停止 GPU 监控
kill $GPU_PID 2>/dev/null || true
wait $GPU_PID 2>/dev/null || true

echo ""
echo "✅ All stages complete!"
echo "📊 CSV reports: $RESULTS_DIR/"
echo "📈 GPU metrics: $RESULTS_DIR/gpu_metrics.csv"
echo ""
echo "Tip: 用以下命令快速查看各阶段摘要:"
echo "  cat $RESULTS_DIR/stage_*_stats.csv"