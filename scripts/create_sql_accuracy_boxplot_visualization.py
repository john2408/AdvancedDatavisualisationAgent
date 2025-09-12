#!/usr/bin/env python3
"""
SQL Agent Accuracy Evaluation Visualization Generator

This script loads the SQL accuracy evaluation CSV file and creates comprehensive 
visualizations showing the distribution of accuracy scores, robustness patterns,
and detailed component analysis across different questions and runs.

Author: Advanced Data Visualization Agent Team
Date: September 2025
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set up the plotting style
sns.set_style("whitegrid")
sns.set_palette("Set2")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def load_and_process_data(csv_file_path):
    """
    Load and process the SQL accuracy evaluation CSV file.
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed dataframe with question labels and analysis columns
    """
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Filter only successful runs
    df_success = df[df['success'] == True].copy()
    
    # Create question labels (Q1, Q2, etc.)
    df_success['question_label'] = 'Q' + df_success['question_num'].astype(str)
    
    # Create short question descriptions for better readability
    df_success['short_question'] = df_success['question'].str[:50] + '...'
    
    # Calculate accuracy percentages
    df_success['rows_accuracy'] = df_success['rows_score'] / 50 * 100
    df_success['columns_accuracy'] = df_success['columns_count_score'] / 40 * 100
    df_success['names_accuracy'] = df_success['column_names_score'] / 10 * 100
    df_success['total_accuracy'] = df_success['total_score'] / 100 * 100
    
    # Create performance categories
    df_success['performance_category'] = pd.cut(
        df_success['total_score'], 
        bins=[0, 70, 90, 100], 
        labels=['Below Standard', 'Good', 'Excellent'],
        include_lowest=True
    )
    
    print(f"Loaded data: {len(df)} total runs, {len(df_success)} successful runs")
    print(f"Questions: {df_success['question_num'].nunique()}")
    print(f"Runs per question: {df_success.groupby('question_num').size().mean():.1f} average")
    print(f"Overall success rate: {len(df_success)/len(df)*100:.1f}%")
    
    return df_success

def create_total_score_boxplot(df, output_path):
    """
    Create a box plot showing total score distribution by question.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    plt.figure(figsize=(16, 10))
    
    # Create the box plot
    ax = sns.boxplot(
        data=df, 
        x='question_label', 
        y='total_score',
        showfliers=True,
        fliersize=4
    )
    
    # Customize the plot
    plt.title('SQL Accuracy Score Distribution by Question\n10-Run Robustness Evaluation Results', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Question Number', fontsize=12, fontweight='bold')
    plt.ylabel('Total Accuracy Score (0-100 points)', fontsize=12, fontweight='bold')
    
    # Add performance threshold lines
    plt.axhline(y=90, color='green', linestyle='--', alpha=0.7, label='Excellent (≥90)')
    plt.axhline(y=70, color='orange', linestyle='--', alpha=0.7, label='Good (≥70)')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3)
    
    # Add legend
    plt.legend(loc='lower left')
    
    # Add statistical information
    overall_mean = df['total_score'].mean()
    overall_std = df['total_score'].std()
    perfect_scores = len(df[df['total_score'] == 100])
    total_runs = len(df)
    
    plt.figtext(0.02, 0.02, 
                f'Overall Statistics: Mean = {overall_mean:.1f}, Std = {overall_std:.1f}, '
                f'Perfect Scores = {perfect_scores}/{total_runs} ({perfect_scores/total_runs*100:.1f}%)', 
                fontsize=10, ha='left')
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Total score box plot saved to: {output_path}")
    
    # Show basic statistics
    print("\nTotal Score Statistics by Question:")
    stats = df.groupby('question_label')['total_score'].agg(['mean', 'std', 'min', 'max', 'count'])
    print(stats.round(1))

def create_consistency_analysis_plot(df, output_path):
    """
    Create a coefficient of variation analysis plot for SQL accuracy.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    # Calculate coefficient of variation for each question
    cv_stats = df.groupby('question_label')['total_score'].agg(['mean', 'std']).reset_index()
    cv_stats['cv'] = (cv_stats['std'] / cv_stats['mean']) * 100
    cv_stats = cv_stats.sort_values('cv', ascending=True)
    
    plt.figure(figsize=(14, 8))
    
    # Create bar plot of coefficient of variation
    colors = ['green' if cv < 10 else 'orange' if cv < 25 else 'red' for cv in cv_stats['cv']]
    
    bars = plt.bar(cv_stats['question_label'], cv_stats['cv'], color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, cv in zip(bars, cv_stats['cv']):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{cv:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Customize the plot
    plt.title('SQL Accuracy Consistency Analysis\nCoefficient of Variation by Question', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Question Number', fontsize=12, fontweight='bold')
    plt.ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    
    # Add horizontal lines for consistency thresholds
    plt.axhline(y=10, color='green', linestyle='--', alpha=0.5, label='High Consistency (CV < 10%)')
    plt.axhline(y=25, color='orange', linestyle='--', alpha=0.5, label='Moderate Consistency (10% ≤ CV < 25%)')
    
    # Add legend
    plt.legend(loc='upper right')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add summary statistics
    high_consistency = len(cv_stats[cv_stats['cv'] < 10])
    moderate_consistency = len(cv_stats[(cv_stats['cv'] >= 10) & (cv_stats['cv'] < 25)])
    variable_performance = len(cv_stats[cv_stats['cv'] >= 25])
    
    plt.figtext(0.02, 0.02, 
                f'Consistency Summary: High={high_consistency}, Moderate={moderate_consistency}, Variable={variable_performance}',
                fontsize=10, ha='left')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Consistency analysis plot saved to: {output_path}")
    
    print("\nCoefficient of Variation Analysis:")
    print(cv_stats[['question_label', 'mean', 'std', 'cv']].round(2))

def create_robustness_heatmap(df, output_path):
    """
    Create a robustness heatmap showing score patterns across questions and runs.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(
        values='total_score', 
        index='question_label', 
        columns='run_num', 
        fill_value=0
    )
    
    plt.figure(figsize=(12, 16))
    
    # Create the heatmap
    ax = sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.0f',
        cmap='RdYlGn',
        center=75,
        cbar_kws={'label': 'Accuracy Score (0-100)'},
        linewidths=0.5,
        square=False
    )
    
    # Customize the plot
    plt.title('SQL Accuracy Robustness Heatmap\nScore Distribution Across Questions and Runs', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Run Number', fontsize=12, fontweight='bold')
    plt.ylabel('Question Number', fontsize=12, fontweight='bold')
    
    # Add colorbar label
    cbar = ax.collections[0].colorbar
    cbar.set_label('Accuracy Score (0-100)', rotation=270, labelpad=20, fontweight='bold')
    
    # Rotate y-axis labels for better readability
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Robustness heatmap saved to: {output_path}")

def main():
    """Main function to generate all SQL accuracy visualizations."""
    
    # Define file paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    csv_file_path = project_root / "tests" / "evaluation_results_crewai" / "sql_agent_evaluation_20250909_222625_all_runs.csv"
    output_dir = project_root / "tests" / "evaluation_results_crewai"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Define output file paths
    total_score_plot = output_dir / "sql_accuracy_boxplot_total_scores.png"
    consistency_analysis_plot = output_dir / "sql_accuracy_consistency_analysis.png"
    robustness_heatmap_plot = output_dir / "sql_accuracy_robustness_heatmap.png"
    
    try:
        # Load and process the data
        print("Loading and processing SQL accuracy evaluation data...")
        df = load_and_process_data(csv_file_path)
        
        # Generate visualizations
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 1: Total Score Box Plot")
        print("="*60)
        create_total_score_boxplot(df, total_score_plot)
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 3: Consistency Analysis")
        print("="*60)
        create_consistency_analysis_plot(df, consistency_analysis_plot)
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 4: Robustness Heatmap")
        print("="*60)
        create_robustness_heatmap(df, robustness_heatmap_plot)
        
        print("\n" + "="*60)
        print("SQL ACCURACY VISUALIZATION GENERATION COMPLETE")
        print("="*60)
        print(f"All plots saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
