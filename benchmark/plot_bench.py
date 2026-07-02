#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
OUTDIR = os.path.join(os.path.dirname(BASE), "results", os.path.basename(os.path.dirname(BASE)), "plots")
os.makedirs(OUTDIR, exist_ok=True)

def read_history(path):
    df = pd.read_csv(path)
    # keep rows with numeric Timestamp
    df = df[pd.to_numeric(df['Timestamp'], errors='coerce').notna()].copy()
    df['ts'] = pd.to_numeric(df['Timestamp'])
    df['requests_s'] = pd.to_numeric(df['Requests/s'], errors='coerce')
    for col in ['50%','95%','99%']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def plot_stage(history_csv, name):
    df = read_history(history_csv)
    if df.empty:
        return None
    start = df['ts'].min()
    df['t'] = df['ts'] - start

    fig, ax1 = plt.subplots(figsize=(8,3))
    ax1.plot(df['t'], df['requests_s'], label='Requests/s', color='tab:blue')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Requests/s', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    if '50%' in df.columns:
        ax2.plot(df['t'], df['50%'], label='P50 (ms)', color='tab:orange')
    if '95%' in df.columns:
        ax2.plot(df['t'], df['95%'], label='P95 (ms)', color='tab:red')
    ax2.set_ylabel('Latency (ms)', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines+lines2, labels+labels2, loc='upper left')

    out = os.path.join(OUTDIR, f"{name}.png")
    plt.title(name)
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)
    return out

def plot_gpu(gpu_csv):
    df = pd.read_csv(gpu_csv)
    df['ts'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df = df[df['ts'].notna()].copy()
    if df.empty:
        return None
    start = df['ts'].min()
    df['t'] = df['ts'] - start

    fig, ax1 = plt.subplots(figsize=(8,3))
    ax1.plot(df['t'], df['mem_used_mb']/1024, label='GPU mem used (GB)', color='tab:green')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('GPU Mem (GB)', color='tab:green')
    ax1.tick_params(axis='y', labelcolor='tab:green')

    ax2 = ax1.twinx()
    ax2.plot(df['t'], df['gpu_util_%'], label='GPU util %', color='tab:purple')
    ax2.set_ylabel('GPU util %', color='tab:purple')
    ax2.tick_params(axis='y', labelcolor='tab:purple')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines+lines2, labels+labels2, loc='upper left')

    out = os.path.join(OUTDIR, "gpu_metrics.png")
    plt.title('GPU metrics')
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)
    return out

def main():
    # results dir is one level up from repo root structure used here
    results_dir = os.path.join(os.path.dirname(BASE), 'results', '20260609_111233')
    stages = [
        (os.path.join(results_dir,'stage_1u_stats_history.csv'),'stage_1u'),
        (os.path.join(results_dir,'stage_8u_stats_history.csv'),'stage_8u'),
        (os.path.join(results_dir,'stage_20u_stats_history.csv'),'stage_20u'),
    ]
    generated = []
    for path, name in stages:
        if os.path.exists(path):
            out = plot_stage(path, name)
            if out:
                generated.append(out)

    gpu_csv = os.path.join(results_dir, 'gpu_metrics.csv')
    if os.path.exists(gpu_csv):
        g = plot_gpu(gpu_csv)
        if g:
            generated.append(g)

    if generated:
        print('Generated:')
        for p in generated:
            print(p)

if __name__ == '__main__':
    main()
