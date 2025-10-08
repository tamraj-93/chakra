#!/usr/bin/env python
"""
Visualize Healthcare RAG Test Results

This script visualizes the results from the healthcare RAG tests,
providing insights into how well the RAG system is performing
for healthcare-specific queries.

Usage:
    python visualize_healthcare_rag_results.py [results_file]
"""

import os
import sys
import json
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def load_latest_results():
    """Load the latest healthcare RAG test results."""
    results_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "backend",
        "tests",
        "results"
    )
    
    if not os.path.exists(results_dir):
        print(f"Results directory not found: {results_dir}")
        return None
    
    # Find all healthcare RAG test result files
    result_files = glob.glob(os.path.join(results_dir, "healthcare_rag_test_*.json"))
    
    if not result_files:
        print(f"No healthcare RAG test results found in {results_dir}")
        return None
    
    # Sort by creation time (most recent first)
    result_files.sort(key=os.path.getmtime, reverse=True)
    
    # Load the most recent file
    with open(result_files[0], 'r') as f:
        results = json.load(f)
    
    return results

def load_specific_results(file_path):
    """Load healthcare RAG test results from a specific file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    with open(file_path, 'r') as f:
        results = json.load(f)
    
    return results

def create_keyword_coverage_chart(results):
    """Create a bar chart showing keyword coverage by query."""
    queries = []
    coverage_pcts = []
    
    for result in results['results']:
        # Shorten query for display
        query = result['query']
        if len(query) > 50:
            query = query[:47] + "..."
        queries.append(query)
        
        # Calculate keyword coverage
        total_keywords = len(result['found_keywords']) + len(result['missing_keywords'])
        coverage = len(result['found_keywords']) / total_keywords * 100
        coverage_pcts.append(coverage)
    
    # Create bar chart
    plt.figure(figsize=(12, 6))
    
    # Create bars with color based on coverage
    bars = plt.bar(range(len(queries)), coverage_pcts)
    
    # Color the bars based on coverage
    for i, bar in enumerate(bars):
        if coverage_pcts[i] >= 80:
            bar.set_color('green')
        elif coverage_pcts[i] >= 50:
            bar.set_color('orange')
        else:
            bar.set_color('red')
    
    plt.title("Healthcare RAG - Keyword Coverage by Query")
    plt.xlabel("Query")
    plt.ylabel("Keyword Coverage (%)")
    plt.xticks(range(len(queries)), queries, rotation=45, ha='right')
    plt.tight_layout()
    
    # Add a horizontal line at 80%
    plt.axhline(y=80, color='green', linestyle='--', alpha=0.5)
    
    # Save the chart
    plt.savefig("healthcare_rag_keyword_coverage.png")
    print("Saved keyword coverage chart to healthcare_rag_keyword_coverage.png")

def create_summary_pie_chart(results):
    """Create a pie chart showing the distribution of test results."""
    passes = results['passes']
    partials = results['partials']
    failures = results['failures']
    
    # Create pie chart
    plt.figure(figsize=(8, 8))
    
    labels = [f'Pass ({passes})', f'Partial ({partials})', f'Fail ({failures})']
    sizes = [passes, partials, failures]
    colors = ['green', 'orange', 'red']
    explode = (0.1, 0, 0)  # explode the 1st slice (Pass)
    
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Healthcare RAG Test Results")
    
    # Save the chart
    plt.savefig("healthcare_rag_results_summary.png")
    print("Saved summary pie chart to healthcare_rag_results_summary.png")

def display_results_summary(results):
    """Display a text summary of the results."""
    timestamp = datetime.fromisoformat(results['timestamp'])
    
    print("=" * 80)
    print(f"Healthcare RAG Test Results - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Total test cases: {results['test_cases']}")
    print(f"Passed: {results['passes']} ({results['passes']/results['test_cases']*100:.1f}%)")
    print(f"Partial: {results['partials']} ({results['partials']/results['test_cases']*100:.1f}%)")
    print(f"Failed: {results['failures']} ({results['failures']/results['test_cases']*100:.1f}%)")
    print(f"Overall score: {results['overall_score']:.1f}%")
    print("-" * 80)
    
    # Display detailed results
    print("\nDetailed Results:")
    print("-" * 80)
    
    for i, result in enumerate(results['results'], 1):
        status_color = "\033[92m" if result['status'] == "PASS" else "\033[93m" if result['status'] == "PARTIAL" else "\033[91m"
        reset_color = "\033[0m"
        
        print(f"{i}. {result['description']}")
        print(f"   Query: {result['query']}")
        print(f"   Status: {status_color}{result['status']}{reset_color} - Score: {result['score']:.1f}%")
        print(f"   Found keywords: {', '.join(result['found_keywords'])}")
        
        if result['missing_keywords']:
            print(f"   Missing keywords: {', '.join(result['missing_keywords'])}")
        
        print("-" * 80)

def main():
    """Main function to visualize the results."""
    if len(sys.argv) > 1:
        results = load_specific_results(sys.argv[1])
    else:
        results = load_latest_results()
    
    if not results:
        print("No results to visualize.")
        return
    
    # Display text summary
    display_results_summary(results)
    
    # Create visualizations
    try:
        import matplotlib
        create_keyword_coverage_chart(results)
        create_summary_pie_chart(results)
    except ImportError:
        print("\nMatplotlib not installed. Skipping visualizations.")
        print("To install: pip install matplotlib")

if __name__ == "__main__":
    main()