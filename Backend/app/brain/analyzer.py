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
        if df.empty:
            raise ValueError("The DataFrame cannot be empty")
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
        """Time series analysis template - handles any data with time-like columns"""
        # Auto-detect time column if not provided
        if not request.time_column:
            # Look for common time column names
            time_candidates = ['date', 'time', 'timestamp', 'created_at', 'updated_at', 'day', 'month', 'year']
            detected_time_col = None
            
            for col in df.columns:
                if col.lower() in time_candidates or 'date' in col.lower() or 'time' in col.lower():
                    detected_time_col = col
                    break
            
            if not detected_time_col:
                # If no time column is found, create a simple index-based analysis
                return self._statistical_analysis(df, request)
            
            request.time_column = detected_time_col
        
        # Ensure time column exists in dataframe
        if request.time_column not in df.columns:
            return self._statistical_analysis(df, request)
        
        # Auto-detect value columns if not provided
        if not request.value_columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                request.value_columns = numeric_cols[:3]  # Take first 3 numeric columns
            else:
                return self._statistical_analysis(df, request)
        
        # Ensure value columns exist and are numeric
        valid_value_cols = [col for col in request.value_columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        if not valid_value_cols:
            return self._statistical_analysis(df, request)
        
        # Prepare time series data
        try:
            ts_data = df.groupby(request.time_column)[valid_value_cols].agg(request.aggregation or 'sum').reset_index()
        except Exception:
            # If groupby fails, try a different approach
            ts_data = df[[request.time_column] + valid_value_cols].copy()
        
        # Create visualization
        fig = go.Figure()
        for col in valid_value_cols:
            if col in ts_data.columns:
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
        
        # Save chart with unique filename
        import uuid
        chart_filename = f"time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
        charts_dir = os.path.abspath(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, chart_filename)
        fig.write_html(chart_path)
        
        return {
            'chart_filename': chart_filename,
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
        
        import uuid
        chart_filename = f"correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
        charts_dir = os.path.abspath(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, chart_filename)
        fig.write_html(chart_path)
        
        return {
            'chart_filename': chart_filename,
            'correlation_matrix': corr_matrix.to_dict(),
            'insights': self._generate_correlation_insights(corr_matrix)
        }
    
    def _pivot_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Enhanced pivot analysis for multi-dimensional business queries"""
        if not request.group_by:
            # Auto-detect grouping columns for general insight queries
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                request.group_by = categorical_cols[0]  # Use first categorical column
            else:
                # If no categorical columns, create a simple summary
                return self._statistical_analysis(df, request)

        # Parse group_by columns - handle multiple dimensions
        if isinstance(request.group_by, str):
            group_by_cols = [col.strip() for col in request.group_by.split('|') if col.strip() and col.strip().lower() != 'null']
        elif isinstance(request.group_by, list):
            group_by_cols = [col for col in request.group_by if col and col.lower() != 'null']
        else:
            group_by_cols = []

        if not group_by_cols:
             raise ValueError("Group by column(s) are invalid or not provided")
        
        # Map common business terms to actual column names
        available_cols = [col.lower() for col in df.columns]
        mapped_cols = []
        
        for col in group_by_cols:
            col_lower = col.lower()
            # Direct match first
            if col_lower in available_cols:
                mapped_cols.append(df.columns[available_cols.index(col_lower)])
            # Fuzzy matching for common business terms
            elif any(term in col_lower for term in ['region', 'area', 'territory']):
                region_col = next((c for c in df.columns if any(term in c.lower() for term in ['region', 'area', 'territory'])), None)
                if region_col: mapped_cols.append(region_col)
            elif any(term in col_lower for term in ['category', 'type', 'class']):
                category_col = next((c for c in df.columns if any(term in c.lower() for term in ['category', 'type', 'class'])), None)
                if category_col: mapped_cols.append(category_col)
            elif any(term in col_lower for term in ['product', 'item', 'name']):
                product_col = next((c for c in df.columns if any(term in c.lower() for term in ['product', 'item', 'name'])), None)
                if product_col: mapped_cols.append(product_col)
        
        # Use mapped columns or fallback to original if no mapping found
        final_group_cols = mapped_cols if mapped_cols else [col for col in group_by_cols if col in df.columns]
        
        if not final_group_cols:
            raise ValueError(f"None of the group by columns {group_by_cols} found in data columns: {df.columns.tolist()}")
        
        # Map value columns similarly
        value_cols = []
        for col in request.value_columns:
            col_lower = col.lower()
            if col_lower in available_cols:
                value_cols.append(df.columns[available_cols.index(col_lower)])
            elif any(term in col_lower for term in ['sales', 'revenue', 'selling']):
                sales_col = next((c for c in df.columns if any(term in c.lower() for term in ['sales', 'revenue', 'selling'])), None)
                if sales_col and pd.api.types.is_numeric_dtype(df[sales_col]):
                    value_cols.append(sales_col)
            elif any(term in col_lower for term in ['profit', 'margin', 'earnings']):
                profit_col = next((c for c in df.columns if any(term in c.lower() for term in ['profit', 'margin', 'earnings'])), None)
                if profit_col and pd.api.types.is_numeric_dtype(df[profit_col]):
                    value_cols.append(profit_col)
        
        # Fallback to first numeric column if no value columns found
        if not value_cols:
            numeric_fallback = df.select_dtypes(include=np.number).columns
            if not numeric_fallback.empty:
                value_cols = [numeric_fallback[0]]
            else:
                raise ValueError("No valid numeric columns found for pivot analysis")

        # Check if we have any data left to analyze
        if df.empty or len(df) == 0:
            raise ValueError("No data available after filtering and column mapping")
        
        # Check if we have the required columns in the dataframe
        missing_cols = [col for col in final_group_cols + value_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in data: {missing_cols}")
        
        # Create comprehensive multi-dimensional analysis
        try:
            # Filter out rows with null values in key columns
            clean_df = df.dropna(subset=final_group_cols + value_cols)
            
            if clean_df.empty:
                raise ValueError("No data available after removing null values")
                
            pivot_result = clean_df.groupby(final_group_cols, as_index=False)[value_cols].agg(request.aggregation or 'sum')
        except Exception as e:
            # Fallback approach
            try:
                clean_df = df[final_group_cols + value_cols].copy().dropna()
                if clean_df.empty:
                    raise ValueError("No valid data available for analysis")
                pivot_result = clean_df.groupby(final_group_cols, as_index=False).sum()
            except Exception as fallback_e:
                raise ValueError(f"Analysis failed: {str(e)}. Fallback also failed: {str(fallback_e)}")
        
        # Sort by the first value column to show top performers
        pivot_result = pivot_result.sort_values(by=value_cols[0], ascending=False)
        
        insights = self._generate_pivot_insights(pivot_result, final_group_cols[0], value_cols[0])
        chart_filenames = []

        # Create separate visualizations for each insight
        for i, insight in enumerate(insights):
            chart_title = f"Insight {i+1}: {insight}"
            
            if len(final_group_cols) == 1:
                # Single dimension - simple bar chart
                fig = px.bar(pivot_result.head(20), x=final_group_cols[0], y=value_cols[0], 
                            title=chart_title, text=value_cols[0])
            elif len(final_group_cols) == 2:
                # Two dimensions - grouped bar chart
                fig = px.bar(pivot_result.head(30), x=final_group_cols[0], y=value_cols[0], 
                            color=final_group_cols[1], title=chart_title, text=value_cols[0],
                            barmode='group')
            else:
                # Three+ dimensions - create a hierarchical view
                # Combine lower-level dimensions into a single label
                pivot_result['combined_label'] = pivot_result[final_group_cols[1:]].apply(
                    lambda x: ' | '.join(x.astype(str)), axis=1
                )
                fig = px.bar(pivot_result.head(40), x=final_group_cols[0], y=value_cols[0], 
                            color='combined_label', title=chart_title, text=value_cols[0],
                            barmode='group')
            
            # Enhance chart appearance
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(
                xaxis_title=final_group_cols[0].replace('_', ' ').title(),
                yaxis_title=value_cols[0].replace('_', ' ').title(),
                showlegend=len(final_group_cols) > 1,
                height=600
            )
            
            import uuid
            chart_filename = f"pivot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}_{i}.html"
            charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
            charts_dir = os.path.abspath(charts_dir)
            os.makedirs(charts_dir, exist_ok=True)
            chart_path = os.path.join(charts_dir, chart_filename)
            fig.write_html(chart_path)
            chart_filenames.append(chart_filename)
        
        # Create detailed summary data
        summary_data = {
            'total_records': len(pivot_result),
            'dimensions_analyzed': final_group_cols,
            'metrics_analyzed': value_cols,
            'top_performers': pivot_result.head(10).to_dict('records'),
            'summary_stats': {
                col: {
                    'total': float(pivot_result[col].sum()),
                    'average': float(pivot_result[col].mean()),
                    'top_value': float(pivot_result[col].max()),
                    'bottom_value': float(pivot_result[col].min())
                } for col in value_cols
            }
        }
        
        return {
            'chart_filenames': chart_filenames,
            'pivot_data': pivot_result.to_dict('records'),
            'summary_data': summary_data,
            'insights': insights
        }
    
    def _distribution_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Distribution analysis template"""
        col = request.value_columns[0]
        
        # Create histogram
        fig = px.histogram(df, x=col, title=f"Distribution of {col}")
        
        import uuid
        chart_filename = f"distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
        charts_dir = os.path.abspath(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, chart_filename)
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
            'chart_filename': chart_filename,
            'statistics': stats,
            'insights': self._generate_distribution_insights(stats, col)
        }
    
    def _comparison_analysis(self, df: pd.DataFrame, request: AnalysisRequest) -> Dict[str, Any]:
        """Comparison analysis template"""
        if not request.group_by:
            raise ValueError("Group by field is required for comparison analysis")
        
        # Create box plot for comparison
        fig = px.box(df, x=request.group_by, y=request.value_columns[0])
        
        import uuid
        chart_filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
        charts_dir = os.path.abspath(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, chart_filename)
        fig.write_html(chart_path)
        
        # Calculate group statistics
        group_stats = df.groupby(request.group_by)[request.value_columns[0]].describe()
        
        return {
            'chart_filename': chart_filename,
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
        
        import uuid
        chart_filename = f"outliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.html"
        charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "charts")
        charts_dir = os.path.abspath(charts_dir)
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, chart_filename)
        fig.write_html(chart_path)
        
        return {
            'chart_filename': chart_filename,
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
        """Generate comprehensive storytelling insights for pivot analysis"""
        insights = []
        
        # Check if data is empty
        if data.empty or len(data) == 0:
            insights.append("⚠️ No data available for analysis after filtering")
            return insights
        
        # Check if required columns exist
        if group_col not in data.columns or value_col not in data.columns:
            insights.append(f"⚠️ Required columns not found: {group_col} or {value_col}")
            return insights
        
        # Check if value column has any non-null values
        if data[value_col].isnull().all() or data[value_col].count() == 0:
            insights.append(f"⚠️ No valid data found in {value_col} column")
            return insights
        
        try:
            # Find highest and lowest values
            max_idx = data[value_col].idxmax()
            min_idx = data[value_col].idxmin()
            
            if pd.isna(max_idx) or pd.isna(min_idx):
                insights.append(f"⚠️ Cannot determine min/max values for {value_col}")
                return insights
            
            max_row = data.loc[max_idx]
            min_row = data.loc[min_idx]
            
            # Calculate metrics
            avg_value = data[value_col].mean()
            total_value = data[value_col].sum()
            std_dev = data[value_col].std()
            
            # Performance insights
            if total_value > 0:
                insights.append(f"🏆 Top Performer: {max_row[group_col]} leads with {max_row[value_col]:,.0f} in {value_col}, representing {(max_row[value_col]/total_value*100):.1f}% of total")
            else:
                insights.append(f"🏆 Top Performer: {max_row[group_col]} with {max_row[value_col]:,.0f} in {value_col}")
            
            if avg_value > 0:
                insights.append(f"📉 Underperformer: {min_row[group_col]} shows lowest {value_col} at {min_row[value_col]:,.0f}, {((avg_value-min_row[value_col])/avg_value*100):.1f}% below average")
            else:
                insights.append(f"📉 Underperformer: {min_row[group_col]} with {min_row[value_col]:,.0f} in {value_col}")
            
            # Distribution insights
            above_avg = data[data[value_col] > avg_value]
            insights.append(f"📊 Distribution: {len(above_avg)} out of {len(data)} categories perform above average ({avg_value:,.0f})")
            
            # Variance insights
            if pd.notna(std_dev) and avg_value > 0:
                if std_dev > avg_value * 0.3:  # High variance
                    insights.append(f"⚠️ High Variance: {value_col} shows significant variation (std dev: {std_dev:,.0f}), indicating uneven performance across {group_col}")
                else:
                    insights.append(f"✅ Consistent Performance: {value_col} shows relatively stable performance across different {group_col} (std dev: {std_dev:,.0f})")
            
            # Performance gap insights
            performance_gap = max_row[value_col] - min_row[value_col]
            if avg_value > 0:
                insights.append(f"📈 Performance Gap: {performance_gap:,.0f} difference between top and bottom performers - {(performance_gap/avg_value*100):.1f}% of average")
            else:
                insights.append(f"📈 Performance Gap: {performance_gap:,.0f} difference between top and bottom performers")
            
            # Market share insights (if applicable)
            if len(data) > 2 and total_value > 0:
                top_3 = data.nlargest(3, value_col)
                top_3_share = (top_3[value_col].sum() / total_value * 100)
                insights.append(f"🎯 Market Concentration: Top 3 categories account for {top_3_share:.1f}% of total {value_col}")
            
        except Exception as e:
            insights.append(f"⚠️ Error generating insights: {str(e)}")
            insights.append(f"📊 Basic info: {len(data)} records found with {value_col} values")
        
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
