#!/usr/bin/env python3
"""
Latency Evaluation Box Plot Visualization Generator

This script loads the latency evaluation CSV file and creates comprehensive box plot 
visualizations showing the distribution of response times across different questions
and pipeline steps.

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
    Load and process the latency evaluation CSV file.
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed dataframe with question labels
    """
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Filter only successful runs
    df_success = df[df['success'] == True].copy()
    
    # Create question labels (Q1, Q2, etc.)
    df_success['question_label'] = 'Q' + df_success['question_num'].astype(str)
    
    # Create short question descriptions for better readability
    df_success['short_question'] = df_success['question'].str[:50] + '...'
    
    print(f"Loaded data: {len(df)} total runs, {len(df_success)} successful runs")
    print(f"Questions: {df_success['question_num'].nunique()}")
    print(f"Runs per question: {df_success.groupby('question_num').size().mean():.1f} average")
    
    return df_success

def create_total_duration_boxplot(df, output_path):
    """
    Create a box plot showing total duration distribution by question.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    plt.figure(figsize=(16, 10))
    
    # Create the box plot
    ax = sns.boxplot(
        data=df, 
        x='question_label', 
        y='total_duration',
        showfliers=True,
        fliersize=4
    )
    
    # Customize the plot
    plt.title('System Latency Distribution by Question\n10-Run Robustness Evaluation Results', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Question Number', fontsize=12, fontweight='bold')
    plt.ylabel('Total Duration (seconds)', fontsize=12, fontweight='bold')
    
    # Add mean markers
    # means = df.groupby('question_label')['total_duration'].mean()
    # for i, (label, mean_val) in enumerate(means.items()):
    #     ax.scatter(i, mean_val, color='red', s=50, marker='D', zorder=10, alpha=0.8)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3)
    
    # Add statistical information
    overall_mean = df['total_duration'].mean()
    overall_std = df['total_duration'].std()
    plt.figtext(0.02, 0.02, 
                f'Overall Statistics: Mean = {overall_mean:.2f}s, Std = {overall_std:.2f}s, '
                f'Success Rate = {len(df)}/{len(df)}', 
                fontsize=10, ha='left')
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Total duration box plot saved to: {output_path}")
    
    # Show basic statistics
    print("\nTotal Duration Statistics by Question:")
    stats = df.groupby('question_label')['total_duration'].agg(['mean', 'std', 'min', 'max', 'count'])
    print(stats.round(2))
    
    #plt.show()

def create_pipeline_steps_boxplot(df, output_path):
    """
    Create a box plot showing duration distribution for each pipeline step by question.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    # Melt the dataframe to have step durations in a single column
    step_columns = ['step_1_generate_sql', 'step_2_review_sql', 'step_3_execute_query', 'step_4_generate_visualization']
    step_names = ['SQL Generation', 'SQL Review', 'Query Execution', 'Visualization']
    
    df_melted = pd.melt(
        df, 
        id_vars=['question_label'], 
        value_vars=step_columns,
        var_name='step',
        value_name='duration'
    )
    
    # Map step names
    step_mapping = dict(zip(step_columns, step_names))
    df_melted['step_name'] = df_melted['step'].map(step_mapping)
    
    plt.figure(figsize=(20, 12))
    
    # Create the box plot
    ax = sns.boxplot(
        data=df_melted, 
        x='question_label', 
        y='duration',
        hue='step_name',
        showfliers=True,
        fliersize=3
    )
    
    # Customize the plot
    plt.title('Pipeline Step Duration Distribution by Question\n10-Run Robustness Evaluation - Detailed Step Analysis', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Question Number', fontsize=12, fontweight='bold')
    plt.ylabel('Step Duration (seconds)', fontsize=12, fontweight='bold')
    
    # Customize legend
    plt.legend(title='Pipeline Step', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Add statistical summary
    step_stats = df_melted.groupby('step_name')['duration'].agg(['mean', 'std']).round(2)
    stats_text = '\n'.join([f'{step}: μ={stats["mean"]:.2f}s, σ={stats["std"]:.2f}s' 
                           for step, stats in step_stats.iterrows()])
    plt.figtext(0.02, 0.02, f'Step Statistics:\n{stats_text}', 
                fontsize=9, ha='left', va='bottom')
    
    # Tight layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Pipeline steps box plot saved to: {output_path}")
    
    #plt.show()

def create_variance_analysis_plot(df, output_path):
    """
    Create a coefficient of variation analysis plot.
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path for the PNG
    """
    # Calculate coefficient of variation for each question
    cv_stats = df.groupby('question_label')['total_duration'].agg(['mean', 'std']).reset_index()
    cv_stats['cv'] = (cv_stats['std'] / cv_stats['mean']) * 100
    cv_stats = cv_stats.sort_values('cv', ascending=True)
    
    plt.figure(figsize=(14, 8))
    
    # Create bar plot of coefficient of variation
    colors = ['green' if cv < 15 else 'orange' if cv < 25 else 'red' for cv in cv_stats['cv']]
    
    bars = plt.bar(cv_stats['question_label'], cv_stats['cv'], color=colors, alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar, cv in zip(bars, cv_stats['cv']):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{cv:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Customize the plot
    plt.title('Performance Consistency Analysis\nCoefficient of Variation by Question', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Question Number', fontsize=12, fontweight='bold')
    plt.ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    
    # Add horizontal lines for consistency thresholds
    plt.axhline(y=15, color='green', linestyle='--', alpha=0.5, label='High Consistency (CV < 15%)')
    plt.axhline(y=25, color='orange', linestyle='--', alpha=0.5, label='Moderate Consistency (15% ≤ CV < 25%)')
    
    # Add legend
    plt.legend(loc='upper right')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add summary statistics
    high_consistency = len(cv_stats[cv_stats['cv'] < 15])
    moderate_consistency = len(cv_stats[(cv_stats['cv'] >= 15) & (cv_stats['cv'] < 25)])
    variable_performance = len(cv_stats[cv_stats['cv'] >= 25])
    
    plt.figtext(0.02, 0.02, 
                f'Consistency Summary: High={high_consistency}, Moderate={moderate_consistency}, Variable={variable_performance}',
                fontsize=10, ha='left')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Variance analysis plot saved to: {output_path}")
    
    print("\nCoefficient of Variation Analysis:")
    print(cv_stats[['question_label', 'mean', 'std', 'cv']].round(2))
    
    #plt.show()

def main():
    """Main function to generate all visualizations."""
    
    # Define file paths
    # Get the script's directory and navigate to the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    csv_file_path = project_root / "tests" / "evaluation_results_crewai" / "app_agents_latency_evaluation_20250909_234513.csv"
    output_dir = project_root / "tests" / "evaluation_results_crewai"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Define output file paths
    total_duration_plot = output_dir / "latency_boxplot_total_duration.png"
    pipeline_steps_plot = output_dir / "latency_boxplot_pipeline_steps.png"
    variance_analysis_plot = output_dir / "latency_variance_analysis.png"
    
    try:
        # Load and process the data
        print("Loading and processing latency evaluation data...")
        df = load_and_process_data(csv_file_path)
        
        # Generate visualizations
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 1: Total Duration Box Plot")
        print("="*60)
        create_total_duration_boxplot(df, total_duration_plot)
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 2: Pipeline Steps Box Plot")
        print("="*60)
        create_pipeline_steps_boxplot(df, pipeline_steps_plot)
        
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION 3: Variance Analysis")
        print("="*60)
        create_variance_analysis_plot(df, variance_analysis_plot)
        
        print("\n" + "="*60)
        print("VISUALIZATION GENERATION COMPLETE")
        print("="*60)
        print(f"All plots saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
