#!/bin/bash

# Process all split DNS list files in parallel
# Usage: ./process_dns_chunks_parallel.sh [max_parallel_jobs]

# Configuration
PYTHON_SCRIPT="dnstt_resolver_probe.py"
TUNNEL_DOMAIN="NS.DOMAIN_NAME.com"
DNSTT_CLIENT="dnstt-client-windows-amd64.exe"
PUBKEY_FILE="pubkey.pub"
SPLIT_DIR="./split"
COMBINED_OUTPUT="working_configs_combined.csv"

# Number of parallel jobs (default: number of CPU cores)
# MAX_JOBS=${1:-$(nproc 2>/dev/null || echo 4)}
MAX_JOBS=32
echo "Processing files with up to $MAX_JOBS parallel jobs..."

# Function to process a single file
process_file() {
    local dns_file=$1
    local chunk_output="working_configs_${dns_file%.txt}.csv"
    
    echo "[$(date +%H:%M:%S)] Processing: $dns_file"
    
    python "$PYTHON_SCRIPT" \
        --dns-list "$dns_file" \
        --tunnel-domain "$TUNNEL_DOMAIN" \
        --out "$chunk_output" \
        --run-deep \
        --dnstt-client-path "$DNSTT_CLIENT" \
        --dnstt-pubkey-file "$PUBKEY_FILE" \
        --dnstt-mode ssh
    
    if [ $? -eq 0 ]; then
        echo "[$(date +%H:%M:%S)] ✓ Completed: $dns_file"
    else
        echo "[$(date +%H:%M:%S)] ✗ Failed: $dns_file"
    fi
}

# Export function and variables for parallel execution
export -f process_file
export PYTHON_SCRIPT TUNNEL_DOMAIN DNSTT_CLIENT PUBKEY_FILE

# Process files in parallel using GNU parallel or xargs
if command -v parallel &> /dev/null; then
    # Use GNU parallel if available (better progress tracking)
    ls "$SPLIT_DIR"/*_*.txt | parallel -j "$MAX_JOBS" --bar process_file {}
else
    # Fallback to xargs
    ls "$SPLIT_DIR"/*_*.txt | xargs -n 1 -P "$MAX_JOBS" -I {} bash -c 'process_file "$@"' _ {}
fi

# Combine all results
echo ""
echo "Combining results..."

first=true
for chunk_output in working_configs_*_*.csv; do
    if [ -f "$chunk_output" ]; then
        if [ "$first" = true ]; then
            cat "$chunk_output" > "$COMBINED_OUTPUT"
            first=false
        else
            tail -n +2 "$chunk_output" >> "$COMBINED_OUTPUT"
        fi
    fi
done

echo "✓ Combined results saved to: $COMBINED_OUTPUT"