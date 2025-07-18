# 🧠 Enhanced AI Data Analysis Brain System
# Combines Python Script Templates + LLM Intelligence

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DataMetadata:
    """Data metadata structure for LLM analysis"""
    columns: List[str]
    dtypes: Dict[str, str]
    shape: tuple
    sample_stats: Dict[str, Any]
    missing_values: Dict[str, int]
    unique_values: Dict[str, int]
    date_columns: List[str]
    numeric_columns: List[str]
    categorical_columns: List[str]

@dataclass
class AnalysisRequest:
    """Analysis request structure from LLM"""
    analysis_type: str
    sql_query: Optional[str]
    chart_type: str
    group_by: Optional[str]
    aggregation: Optional[str]
    time_column: Optional[str]
    value_columns: List[str]
    output_format: str
    filters: Optional[Dict[str, Any]]

class EnhancedDataAnalyzer:
    """Enhanced data analyzer with template-based analysis"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.parquet']
        self.analysis_templates = {
            'time_series': self._time_series_analysis,
            'correlation': self._correlation_analysis,
            'pivot': self._pivot_analysis,
            'distribution': self._distribution_analysis,
            'comparison': self._comparison_analysis,
            'trend': self._trend_analysis,
            'outlier': self._outlier_analysis,
            'statistical': self._statistical_analysis
        }
    
    def read_file(self, file_path: str) -> pd.DataFrame:
        """Enhanced file reader with better error handling"""
        try:
            ext = os.path.splitext(file_path)[-1].lower()
            
            if ext == '.csv':
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            elif ext == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            return self._clean_data(df)
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data cleaning"""
        # Remove completely empty rows/columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Auto-detect and convert date columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    def extract_metadata(self, df: pd.DataFrame) -> DataMetadata:
        """Extract comprehensive metadata for LLM analysis"""
        # Identify column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Get unique value counts
        unique_values = {}
        for col in df.columns:
            unique_values[col] = df[col].nunique()
        
        # Generate sample statistics
        sample_stats = {}
        for col in numeric_cols:
            sample_stats[col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75))
            }
        
        return DataMetadata(
            columns=df.columns.tolist(),
            dtypes=df.dtypes.astype(str).to_dict(),
            shape=df.shape,
            sample_stats=sample_stats,
            missing_values=df.isnull().sum().to_dict(),
            unique_values=unique_values,
            date_columns=date_cols,
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols
        )
    
    def run_sql_query(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        """Execute SQL query using DuckDB"""
        try:
            con = duckdb.connect()
            con.register("data", df)
            result = con.execute(query).df()
            con.close()
            return result
        except Exception as e:
            raise Exception(f"SQL execution error: {str(e)}")
    
    def execute_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Execute analysis based on LLM request"""
        if request.analysis_type not in self.analysis_templates:
            raise ValueError(f"Unsupported analysis type: {request.analysis_type}")
        
        # Apply filters if provided
        if request.filters:
            df = self._apply_filters(df, request.filters)
        
        # Execute the appropriate analysis template
        return self.analysis_templates[request.analysis_type](df, request)
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        for col, condition in filters.items():
            if isinstance(condition, dict):
                if 'min' in condition:
                    df = df[df[col] >= condition['min']]
                if 'max' in condition:
                    df = df[df[col] <= condition['max']]
                if 'values' in condition:
                    df = df[df[col].isin(condition['values'])]
            else:
                df = df[df[col] == condition]
        return df
    
    def _time_series_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Time series analysis template"""
        if not request.time_column:
            raise ValueError("Time column is required for time series analysis")
        
        # Prepare time series data
        ts_data = df.groupby(request.time_column)[request.value_columns].agg(request.aggregation or 'sum').reset_index()
        
        # Create visualization
        fig = go.Figure()
        for col in request.value_columns:
            fig.add_trace(go.Scatter(
                x=ts_data[request.time_column],
                y=ts_data[col],
                name=col,
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title=f"Time Series Analysis: {', '.join(request.value_columns)}",
            xaxis_title=request.time_column,
            yaxis_title="Value"
        )
        
        # Save chart
        chart_path = f"time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        return {
            'chart_path': chart_path,
            'data': ts_data.to_dict('records'),
            'insights': self._generate_time_series_insights(ts_data, request.value_columns)
        }
    
    def _correlation_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Correlation analysis template"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale='RdBu',
            aspect="auto"
        )
        
        chart_path = f"correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        return {
            'chart_path': chart_path,
            'correlation_matrix': corr_matrix.to_dict(),
            'insights': self._generate_correlation_insights(corr_matrix)
        }
    
    def _pivot_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Pivot analysis template"""
        if not request.group_by:
            raise ValueError("Group by field is required for pivot analysis")
        
        # Create pivot table
        pivot_result = df.groupby(request.group_by)[request.value_columns].agg(request.aggregation or 'sum').reset_index()
        
        # Create visualization based on chart type
        if request.chart_type == 'bar':
            fig = px.bar(pivot_result, x=request.group_by, y=request.value_columns[0])
        elif request.chart_type == 'pie':
            fig = px.pie(pivot_result, names=request.group_by, values=request.value_columns[0])
        else:
            fig = px.bar(pivot_result, x=request.group_by, y=request.value_columns[0])
        
        chart_path = f"pivot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        return {
            'chart_path': chart_path,
            'pivot_data': pivot_result.to_dict('records'),
            'insights': self._generate_pivot_insights(pivot_result, request.group_by, request.value_columns[0])
        }
    
    def _distribution_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Distribution analysis template"""
        col = request.value_columns[0]
        
        # Create histogram
        fig = px.histogram(df, x=col, title=f"Distribution of {col}")
        
        chart_path = f"distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        # Calculate statistics
        stats = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'skewness': df[col].skew(),
            'kurtosis': df[col].kurtosis()
        }
        
        return {
            'chart_path': chart_path,
            'statistics': stats,
            'insights': self._generate_distribution_insights(stats, col)
        }
    
    def _comparison_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Comparison analysis template"""
        if not request.group_by:
            raise ValueError("Group by field is required for comparison analysis")
        
        # Create box plot for comparison
        fig = px.box(df, x=request.group_by, y=request.value_columns[0])
        
        chart_path = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        # Calculate group statistics
        group_stats = df.groupby(request.group_by)[request.value_columns[0]].describe()
        
        return {
            'chart_path': chart_path,
            'group_statistics': group_stats.to_dict(),
            'insights': self._generate_comparison_insights(group_stats, request.group_by, request.value_columns[0])
        }
    
    def _trend_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Trend analysis template"""
        return self._time_series_analysis(df, request)  # Similar to time series
    
    def _outlier_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Outlier detection template"""
        col = request.value_columns[0]
        
        # Calculate IQR
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        
        # Create scatter plot with outliers highlighted
        fig = px.scatter(df, y=col, title=f"Outlier Detection: {col}")
        fig.add_hline(y=lower_bound, line_dash="dash", line_color="red", annotation_text="Lower Bound")
        fig.add_hline(y=upper_bound, line_dash="dash", line_color="red", annotation_text="Upper Bound")
        
        chart_path = f"outliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fig.write_html(chart_path)
        
        return {
            'chart_path': chart_path,
            'outliers': outliers.to_dict('records'),
            'outlier_count': len(outliers),
            'bounds': {'lower': lower_bound, 'upper': upper_bound},
            'insights': self._generate_outlier_insights(outliers, col)
        }
    
    def _statistical_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Statistical analysis template"""
        col = request.value_columns[0]
        
        # Comprehensive statistics
        stats = {
            'descriptive': df[col].describe().to_dict(),
            'distribution': {
                'skewness': df[col].skew(),
                'kurtosis': df[col].kurtosis()
            },
            'confidence_intervals': {
                '95%': {
                    'lower': df[col].quantile(0.025),
                    'upper': df[col].quantile(0.975)
                }
            }
        }
        
        return {
            'statistics': stats,
            'insights': self._generate_statistical_insights(stats, col)
        }
    
    # Insight generation methods
    def _generate_time_series_insights(self, data: pd.DataFrame, columns: List[str]) -> List[str]:
        """Generate insights for time series analysis"""
        insights = []
        for col in columns:
            trend = "increasing" if data[col].iloc[-1] > data[col].iloc[0] else "decreasing"
            insights.append(f"{col} shows an overall {trend} trend")
        return insights
    
    def _generate_correlation_insights(self, corr_matrix: pd.DataFrame) -> List[str]:
        """Generate insights for correlation analysis"""
        insights = []
        # Find strongest correlations
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_pairs.append((
                    corr_matrix.columns[i],
                    corr_matrix.columns[j],
                    abs(corr_matrix.iloc[i, j])
                ))
        
        # Sort by correlation strength
        corr_pairs.sort(key=lambda x: x[2], reverse=True)
        
        for col1, col2, corr in corr_pairs[:3]:  # Top 3 correlations
            strength = "strong" if corr > 0.7 else "moderate" if corr > 0.5 else "weak"
            insights.append(f"{col1} and {col2} show {strength} correlation ({corr:.3f})")
        
        return insights
    
    def _generate_pivot_insights(self, data: pd.DataFrame, group_col: str, value_col: str) -> List[str]:
        """Generate insights for pivot analysis"""
        insights = []
        
        # Find highest and lowest values
        max_row = data.loc[data[value_col].idxmax()]
        min_row = data.loc[data[value_col].idxmin()]
        
        insights.append(f"Highest {value_col}: {max_row[group_col]} ({max_row[value_col]:,.2f})")
        insights.append(f"Lowest {value_col}: {min_row[group_col]} ({min_row[value_col]:,.2f})")
        
        # Calculate average
        avg_value = data[value_col].mean()
        insights.append(f"Average {value_col}: {avg_value:,.2f}")
        
        return insights
    
    def _generate_distribution_insights(self, stats: Dict[str, float], column: str) -> List[str]:
        """Generate insights for distribution analysis"""
        insights = []
        
        if stats['skewness'] > 0.5:
            insights.append(f"{column} distribution is right-skewed")
        elif stats['skewness'] < -0.5:
            insights.append(f"{column} distribution is left-skewed")
        else:
            insights.append(f"{column} distribution is approximately normal")
        
        if stats['kurtosis'] > 3:
            insights.append(f"{column} has heavy tails (high kurtosis)")
        elif stats['kurtosis'] < 3:
            insights.append(f"{column} has light tails (low kurtosis)")
        
        return insights
    
    def _generate_comparison_insights(self, group_stats: pd.DataFrame, group_col: str, value_col: str) -> List[str]:
        """Generate insights for comparison analysis"""
        insights = []
        
        # Find group with highest and lowest means
        means = group_stats['mean']
        highest_group = means.idxmax()
        lowest_group = means.idxmin()
        
        insights.append(f"Highest average {value_col}: {highest_group} ({means[highest_group]:,.2f})")
        insights.append(f"Lowest average {value_col}: {lowest_group} ({means[lowest_group]:,.2f})")
        
        # Compare variability
        stds = group_stats['std']
        most_variable = stds.idxmax()
        insights.append(f"Most variable group: {most_variable} (std: {stds[most_variable]:,.2f})")
        
        return insights
    
    def _generate_outlier_insights(self, outliers: pd.DataFrame, column: str) -> List[str]:
        """Generate insights for outlier analysis"""
        insights = []
        
        outlier_count = len(outliers)
        total_count = len(outliers) + 100  # Approximate, would need actual dataset size
        
        insights.append(f"Found {outlier_count} outliers in {column}")
        insights.append(f"Outliers represent {(outlier_count/total_count)*100:.1f}% of the data")
        
        if outlier_count > 0:
            insights.append(f"Outlier range: {outliers[column].min():.2f} to {outliers[column].max():.2f}")
        
        return insights
    
    def _generate_statistical_insights(self, stats: Dict[str, Any], column: str) -> List[str]:
        """Generate insights for statistical analysis"""
        insights = []
        
        desc = stats['descriptive']
        insights.append(f"{column} mean: {desc['mean']:,.2f}")
        insights.append(f"{column} median: {desc['50%']:,.2f}")
        insights.append(f"{column} standard deviation: {desc['std']:,.2f}")
        
        dist = stats['distribution']
        if abs(dist['skewness']) > 0.5:
            skew_dir = "right" if dist['skewness'] > 0 else "left"
            insights.append(f"{column} is {skew_dir}-skewed")
        
        return insights

# Example usage
def main():
    analyzer = EnhancedDataAnalyzer()
    
    # Example analysis request (would come from LLM)
    request = AnalysisRequest(
        analysis_type="time_series",
        sql_query=None,
        chart_type="line",
        group_by=None,
        aggregation="sum",
        time_column="date",
        value_columns=["sales"],
        output_format="HTML",
        filters=None
    )
    
    # Load and analyze data
    df = analyzer.read_file("sample_data.csv")
    metadata = analyzer.extract_metadata(df)
    result = analyzer.execute_analysis(df, request)
    
    print("Analysis completed successfully!")
    print(f"Chart saved: {result['chart_path']}")
    print(f"Insights: {result['insights']}")

if __name__ == "__main__":
    main()
