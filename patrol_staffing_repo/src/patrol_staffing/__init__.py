
"""Patrol staffing optimization package."""
from .data_prep import load_calls, build_features, build_map_data
from .optimization import optimize_staffing, summarize_results
