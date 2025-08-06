#!/bin/bash


ROOT_DIR="."


find "$ROOT_DIR" -type d -path "./Experiment_*/*/*/model_and_node_selection" -exec rm -rf {} +

echo "All matching 'model_and_node_selection' folders have been removed."

find "$ROOT_DIR" -type f -name "plot_summaries.py" -exec python3 {} \;

echo "Plot summaries executed"
