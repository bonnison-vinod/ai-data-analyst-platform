#!/usr/bin/env python3
"""
Enhanced Report Generator for AI Data Analyst Platform
Creates interactive Excel reports with multiple sheets, visualizations, and custom analysis
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime, timedelta
import json
import sqlite3
import openai
from typing import Dict, List, Any, Optional, Tuple, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportStatus(Enum):
    INITIALIZING = "initializing"
    PROCESSING_DATA = "processing_data"
    GENERATING_VISUALIZATIONS = "generating_visualizations"
    CREATING_PIVOTS = "creating_pivots"
    BUILDING_DASHBOARD = "building_dashboard"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class ProgressUpdate:
    status: ReportStatus
    percentage: float
    message: str
    current_step: str
    total_steps: int
    current_step_number: int

class EnhancedReportGenerator:
    def __init__(self):
        self.progress_callback = None
        self.current_progress = ProgressUpdate(
            status=ReportStatus.INITIALIZING,
            percentage=0.0,
            message="Initializing report generation...",
            current_step="Setup",
            total_steps=6,
            current_step_number=0
        )
        
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        
    def update_progress(self, status: ReportStatus, percentage: float, message: str, step_number: int):
        """Update progress and notify callback"""
        self.current_progress = ProgressUpdate(
            status=status,
            percentage=percentage,
            message=message,
            current_step=status.value.replace('_', ' ').title(),
            total_steps=6,
            current_step_number=step_number
        )
        
        if self.progress_callback:
            self.progress_callback(self.current_progress)
            
        logger.info(f"Progress: {percentage:.1f}% - {message}")

    async def generate_comprehensive_report(
        self, 
        data: pd.DataFrame, 
        question: str = None,
        custom_sheets: List[Dict] = None,
        analysis_type: str = "comprehensive"
    ) -> Tuple[str, Dict]:
        """
        Generate comprehensive Excel report with multiple sheets and interactive elements
        
        Args:
            data: Input DataFrame
            question: User's question for analysis
            custom_sheets: List of custom sheet definitions
            analysis_type: Type of analysis to perform
            
        Returns:
            Tuple of (report_filename, analysis_summary)
        """
        
        try:
            # Step 1: Initialize
            self.update_progress(ReportStatus.INITIALIZING, 5.0, "Setting up report generation...", 1)
            await asyncio.sleep(0.1)  # Allow UI update
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"comprehensive_analysis_report_{timestamp}.xlsx"
            
            # Step 2: Process Data
            self.update_progress(ReportStatus.PROCESSING_DATA, 20.0, "Processing and cleaning data...", 2)
            processed_data = await self._process_data(data)
            analysis_summary = await self._analyze_data(processed_data, question)
            
            # Step 3: Generate Visualizations
            self.update_progress(ReportStatus.GENERATING_VISUALIZATIONS, 40.0, "Creating interactive visualizations...", 3)
            charts_data = await self._generate_interactive_charts(processed_data)
            
            # Step 4: Create Pivots
            self.update_progress(ReportStatus.CREATING_PIVOTS, 60.0, "Building pivot tables and analysis...", 4)
            pivot_data = await self._create_pivot_analysis(processed_data)
            
            # Step 5: Build Dashboard
            self.update_progress(ReportStatus.BUILDING_DASHBOARD, 80.0, "Assembling interactive dashboard...", 5)
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(report_filename, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Create Dashboard Sheet
                await self._create_dashboard_sheet(writer, workbook, processed_data, charts_data, analysis_summary)
                
                # Create Pivots Sheet
                await self._create_pivots_sheet(writer, workbook, pivot_data)
                
                # Create Raw Data Sheet
                await self._create_raw_data_sheet(writer, workbook, processed_data)
                
                # Create Custom Sheets if provided
                if custom_sheets:
                    for sheet_config in custom_sheets:
                        await self._create_custom_sheet(writer, workbook, processed_data, sheet_config)
            
            # Step 6: Finalize
            self.update_progress(ReportStatus.FINALIZING, 95.0, "Finalizing report...", 6)
            await asyncio.sleep(0.1)
            
            self.update_progress(ReportStatus.COMPLETED, 100.0, "Report generation completed successfully!", 6)
            
            return report_filename, analysis_summary
            
        except Exception as e:
            self.update_progress(ReportStatus.ERROR, 0.0, f"Error: {str(e)}", 0)
            logger.error(f"Error generating report: {str(e)}")
            raise

    async def _process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the input data"""
        processed_data = data.copy()
        
        # Basic data cleaning
        processed_data = processed_data.dropna(how='all')  # Remove completely empty rows
        
        # Convert date columns
        for col in processed_data.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    processed_data[col] = pd.to_datetime(processed_data[col])
                except:
                    pass
        
        # Add derived columns if possible
        if 'Sales' in processed_data.columns and 'Profit' in processed_data.columns:
            processed_data['Profit_Margin'] = (processed_data['Profit'] / processed_data['Sales']) * 100
            
        return processed_data

    async def _analyze_data(self, data: pd.DataFrame, question: str = None) -> Dict:
        """Perform comprehensive data analysis"""
        analysis = {
            'summary_stats': data.describe().to_dict(),
            'data_shape': data.shape,
            'columns': list(data.columns),
            'null_counts': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.astype(str).to_dict()
        }
        
        # Numeric columns analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis['correlations'] = data[numeric_cols].corr().to_dict()
            
        # Categorical analysis
        categorical_cols = data.select_dtypes(include=['object']).columns
        analysis['categorical_summary'] = {}
        for col in categorical_cols:
            analysis['categorical_summary'][col] = {
                'unique_count': data[col].nunique(),
                'top_values': data[col].value_counts().head().to_dict()
            }
            
        return analysis

    async def _generate_interactive_charts(self, data: pd.DataFrame) -> Dict:
        """Generate charts and prepare data for Excel embedding"""
        charts_info = {}
        
        # Detect numeric and categorical columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        
        # Store chart data for Excel embedding
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Aggregate data for charts
            agg_data = data.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index()
            charts_info['bar_chart'] = {
                'data': agg_data,
                'x_col': categorical_cols[0],
                'y_col': numeric_cols[0],
                'title': f"Total {numeric_cols[0]} by {categorical_cols[0]}"
            }
            
            # Pie chart data
            if len(agg_data) <= 10:
                charts_info['pie_chart'] = {
                    'data': agg_data,
                    'values_col': numeric_cols[0],
                    'names_col': categorical_cols[0],
                    'title': f"Distribution of {numeric_cols[0]} by {categorical_cols[0]}"
                }
        
        # Time series data if date column exists
        date_cols = [col for col in data.columns if data[col].dtype.name.startswith('datetime')]
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            time_data = data.groupby(date_col)[numeric_col].sum().reset_index()
            charts_info['line_chart'] = {
                'data': time_data,
                'x_col': date_col,
                'y_col': numeric_col,
                'title': f"{numeric_col} Trend Over Time"
            }
        
        # Scatter plot data
        if len(numeric_cols) >= 2:
            charts_info['scatter_chart'] = {
                'data': data[[numeric_cols[0], numeric_cols[1]]],
                'x_col': numeric_cols[0],
                'y_col': numeric_cols[1],
                'title': f"{numeric_cols[0]} vs {numeric_cols[1]}"
            }
            
        return charts_info

    async def _create_pivot_analysis(self, data: pd.DataFrame) -> Dict:
        """Create pivot table analysis"""
        pivots = {}
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Basic pivot table
            try:
                if len(categorical_cols) >= 2:
                    pivot1 = pd.pivot_table(
                        data,
                        values=numeric_cols[0] if numeric_cols else None,
                        index=categorical_cols[0],
                        columns=categorical_cols[1] if len(categorical_cols) > 1 else None,
                        aggfunc='sum',
                        fill_value=0
                    )
                    pivots['basic_pivot'] = pivot1
                
                # Summary by category
                for cat_col in categorical_cols:
                    summary = data.groupby(cat_col)[numeric_cols].agg(['sum', 'mean', 'count']).round(2)
                    pivots[f'summary_by_{cat_col}'] = summary
                    
            except Exception as e:
                logger.warning(f"Could not create pivot analysis: {str(e)}")
                
        return pivots

    async def _create_dashboard_sheet(self, writer, workbook, data, charts_data, analysis_summary):
        """Create the interactive dashboard sheet with embedded charts"""
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center'
        })
        
        metric_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#E8F4F8',
            'align': 'center',
            'border': 1
        })
        
        chart_title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#70AD47',
            'font_color': 'white',
            'align': 'center'
        })
        
        # Create dashboard worksheet
        dashboard_ws = workbook.add_worksheet('📊 Interactive Dashboard')
        dashboard_ws.set_column('A:Z', 15)
        
        row = 0
        
        # Title
        dashboard_ws.merge_range('A1:H1', '🤖 AI Data Analyst - Interactive Dashboard', header_format)
        dashboard_ws.merge_range('A2:H2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', workbook.add_format({'align': 'center'}))
        row = 3
        
        # Key Metrics Section
        dashboard_ws.merge_range(f'A{row+1}:H{row+1}', '📈 Key Metrics', header_format)
        row += 2
        
        # Add key metrics with colors
        metrics = [
            ('Total Records', len(data)),
            ('Total Columns', len(data.columns)),
            ('Numeric Columns', len(data.select_dtypes(include=[np.number]).columns)),
            ('Text Columns', len(data.select_dtypes(include=['object']).columns))
        ]
        
        col = 0
        for metric_name, metric_value in metrics:
            dashboard_ws.write(row, col, metric_name, metric_format)
            dashboard_ws.write(row+1, col, metric_value, metric_format)
            col += 2
            
        row += 4
        
        # Charts Section
        dashboard_ws.merge_range(f'A{row+1}:H{row+1}', '📊 Data Visualizations', header_format)
        row += 2
        
        # Create Excel charts from data
        chart_row = row
        
        # Bar Chart
        if 'bar_chart' in charts_data:
            bar_data = charts_data['bar_chart']
            chart_df = bar_data['data']
            
            # Write chart data
            dashboard_ws.write(chart_row, 0, bar_data['title'], chart_title_format)
            chart_df.to_excel(writer, sheet_name='📊 Interactive Dashboard', 
                              startrow=chart_row+1, startcol=0, index=False)
            
            # Apply filter to chart data
            chart_end_row = chart_row + 1 + len(chart_df)
            chart_filter_range = f'A{chart_row+1}:B{chart_end_row}'
            dashboard_ws.autofilter(chart_filter_range)
            
            # Create Excel bar chart with enhanced formatting
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': bar_data['y_col'],
                'categories': [dashboard_ws.name, chart_row+2, 0, chart_row+1+len(chart_df), 0],
                'values': [dashboard_ws.name, chart_row+2, 1, chart_row+1+len(chart_df), 1],
                'fill': {'color': '#4472C4'},
                'data_labels': {'value': True, 'position': 'outside_end'}
            })
            chart.set_title({
                'name': bar_data['title'] + ' (Interactive - Filter data below)',
                'name_font': {'size': 12, 'bold': True}
            })
            chart.set_x_axis({'name': bar_data['x_col']})
            chart.set_y_axis({'name': bar_data['y_col']})
            chart.set_size({'width': 480, 'height': 288})
            chart.set_legend({'position': 'bottom'})
            dashboard_ws.insert_chart(f'D{chart_row+1}', chart)
            
            chart_row += len(chart_df) + 5
        
        # Pie Chart
        if 'pie_chart' in charts_data:
            pie_data = charts_data['pie_chart']
            chart_df = pie_data['data']
            
            # Write pie chart data
            dashboard_ws.write(chart_row, 0, pie_data['title'], chart_title_format)
            chart_df.to_excel(writer, sheet_name='📊 Interactive Dashboard', 
                              startrow=chart_row+1, startcol=0, index=False)
            
            # Create Excel pie chart
            pie_chart = workbook.add_chart({'type': 'pie'})
            pie_chart.add_series({
                'name': pie_data['values_col'],
                'categories': [dashboard_ws.name, chart_row+2, 0, chart_row+1+len(chart_df), 0],
                'values': [dashboard_ws.name, chart_row+2, 1, chart_row+1+len(chart_df), 1],
                'data_labels': {'percentage': True}
            })
            pie_chart.set_title({'name': pie_data['title']})
            pie_chart.set_size({'width': 480, 'height': 288})
            dashboard_ws.insert_chart(f'D{chart_row+1}', pie_chart)
            
            chart_row += len(chart_df) + 5
        
        # Line Chart (Time Series)
        if 'line_chart' in charts_data:
            line_data = charts_data['line_chart']
            chart_df = line_data['data']
            
            # Write line chart data
            dashboard_ws.write(chart_row, 0, line_data['title'], chart_title_format)
            chart_df.to_excel(writer, sheet_name='📊 Interactive Dashboard', 
                              startrow=chart_row+1, startcol=0, index=False)
            
            # Create Excel line chart
            line_chart = workbook.add_chart({'type': 'line'})
            line_chart.add_series({
                'name': line_data['y_col'],
                'categories': [dashboard_ws.name, chart_row+2, 0, chart_row+1+len(chart_df), 0],
                'values': [dashboard_ws.name, chart_row+2, 1, chart_row+1+len(chart_df), 1],
                'line': {'color': '#70AD47', 'width': 2}
            })
            line_chart.set_title({'name': line_data['title']})
            line_chart.set_x_axis({'name': line_data['x_col']})
            line_chart.set_y_axis({'name': line_data['y_col']})
            line_chart.set_size({'width': 480, 'height': 288})
            dashboard_ws.insert_chart(f'D{chart_row+1}', line_chart)
            
            chart_row += len(chart_df) + 5
        
        # Scatter Chart
        if 'scatter_chart' in charts_data:
            scatter_data = charts_data['scatter_chart']
            chart_df = scatter_data['data']
            
            # Write scatter chart data
            dashboard_ws.write(chart_row, 0, scatter_data['title'], chart_title_format)
            chart_df.to_excel(writer, sheet_name='📊 Interactive Dashboard', 
                              startrow=chart_row+1, startcol=0, index=False)
            
            # Create Excel scatter chart
            scatter_chart = workbook.add_chart({'type': 'scatter'})
            scatter_chart.add_series({
                'name': f"{scatter_data['x_col']} vs {scatter_data['y_col']}",
                'categories': [dashboard_ws.name, chart_row+2, 0, chart_row+1+len(chart_df), 0],
                'values': [dashboard_ws.name, chart_row+2, 1, chart_row+1+len(chart_df), 1],
                'marker': {'type': 'circle', 'size': 5, 'fill': {'color': '#FFC000'}}
            })
            scatter_chart.set_title({'name': scatter_data['title']})
            scatter_chart.set_x_axis({'name': scatter_data['x_col']})
            scatter_chart.set_y_axis({'name': scatter_data['y_col']})
            scatter_chart.set_size({'width': 480, 'height': 288})
            dashboard_ws.insert_chart(f'D{chart_row+1}', scatter_chart)
            
            chart_row += len(chart_df) + 5
        
        # Data Summary Section
        summary_row = chart_row + 2
        dashboard_ws.merge_range(f'A{summary_row+1}:H{summary_row+1}', '📊 Data Summary', header_format)
        summary_row += 2
        
        # Write summary statistics if available
        if 'summary_stats' in analysis_summary:
            summary_df = pd.DataFrame(analysis_summary['summary_stats'])
            summary_df.to_excel(writer, sheet_name='📊 Interactive Dashboard', 
                                startrow=summary_row, startcol=0)
            summary_row += len(summary_df) + 3
        
        # Interactive Features Section
        dashboard_ws.merge_range(f'A{summary_row+1}:H{summary_row+1}', '💡 Interactive Features', header_format)
        summary_row += 2
        
        instructions = [
            "✅ Charts and visualizations are embedded above",
            "✅ Use pivot tables in 'Pivot Analysis' sheet for dynamic filtering",
            "✅ Raw data is available in 'Clean Data' sheet for custom analysis",
            "✅ Custom sheets contain specialized analysis based on your questions",
            "✅ All data is clean, structured, and ready for further analysis"
        ]
        
        for instruction in instructions:
            dashboard_ws.write(summary_row, 0, instruction)
            summary_row += 1

    async def _create_pivots_sheet(self, writer, workbook, pivot_data):
        """Create the pivots analysis sheet with interactive elements"""
        pivots_ws = workbook.add_worksheet('📋 Pivot Analysis')
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#70AD47',
            'font_color': 'white'
        })
        
        filter_format = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'bg_color': '#FFC000',
            'border': 1
        })
        
        # Title section
        pivots_ws.merge_range('A1:H1', '📋 Interactive Pivot Analysis & Filters', header_format)
        pivots_ws.merge_range('A2:H2', 'Use filters and dropdowns below for interactive analysis', workbook.add_format({'align': 'center'}))
        
        row = 3
        
        # Add interactive instructions
        instructions = [
            "💡 Interactive Features:",
            "• Click dropdown arrows in headers to filter data",
            "• Use slicers (if available) for visual filtering",
            "• Sort columns by clicking headers",
            "• Expand/collapse grouped data"
        ]
        
        for instruction in instructions:
            pivots_ws.write(row, 0, instruction)
            row += 1
        
        row += 2
        
        for pivot_name, pivot_df in pivot_data.items():
            # Write pivot title
            pivots_ws.merge_range(f'A{row+1}:H{row+1}', f'📊 {pivot_name.replace("_", " ").title()}', header_format)
            row += 2
            
            # Write pivot data with auto-filter
            if isinstance(pivot_df, pd.DataFrame):
                # Write the data
                pivot_df.to_excel(writer, sheet_name='📋 Pivot Analysis', startrow=row, startcol=0)
                
                # Add auto-filter to the data range
                end_row = row + len(pivot_df)
                end_col = len(pivot_df.columns)
                
                # Convert column numbers to Excel letters
                end_col_letter = chr(ord('A') + end_col)
                filter_range = f'A{row+1}:{end_col_letter}{end_row}'
                
                # Apply auto-filter
                pivots_ws.autofilter(filter_range)
                
                # Format headers with filter styling
                for col_num in range(len(pivot_df.columns) + 1):  # +1 for index column
                    if col_num == 0:
                        header_name = pivot_df.index.name or 'Index'
                    else:
                        header_name = pivot_df.columns[col_num-1]
                        # Handle multi-level columns
                        if isinstance(header_name, tuple):
                            header_name = ' - '.join(str(x) for x in header_name)
                    pivots_ws.write(row, col_num, str(header_name), filter_format)
                
                row += len(pivot_df) + 4
            
    async def _create_raw_data_sheet(self, writer, workbook, data):
        """Create the clean raw data sheet with interactive filters"""
        # Create the worksheet
        worksheet = workbook.add_worksheet('📁 Clean Data')
        
        # Format headers
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFC000',
            'border': 1,
            'align': 'center'
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center'
        })
        
        # Add title and instructions
        worksheet.merge_range('A1:' + chr(ord('A') + len(data.columns) - 1) + '1', 
                             '📁 Interactive Clean Data with Filters', title_format)
        
        # Add filter instructions
        filter_instructions = [
            "💡 Click dropdown arrows in column headers to filter and sort data",
            "🔍 Use Ctrl+F to search for specific values",
            "📊 Select data ranges and create your own charts"
        ]
        
        for i, instruction in enumerate(filter_instructions):
            worksheet.write(2 + i, 0, instruction)
        
        # Starting row for data (after title and instructions)
        start_row = 5
        
        # Write headers
        for col_num, column_name in enumerate(data.columns):
            worksheet.write(start_row, col_num, column_name, header_format)
        
        # Write data
        for row_num, (_, row_data) in enumerate(data.iterrows(), start_row + 1):
            for col_num, value in enumerate(row_data):
                worksheet.write(row_num, col_num, value)
        
        # Apply auto-filter to the entire data range
        end_row = start_row + len(data)
        end_col_letter = chr(ord('A') + len(data.columns) - 1)
        filter_range = f'A{start_row}:{end_col_letter}{end_row}'
        worksheet.autofilter(filter_range)
        
        # Set column widths and add data validation for better UX
        for i, col in enumerate(data.columns):
            max_len = max(data[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(max_len, 50))
            
            # Add data bars for numeric columns
            if pd.api.types.is_numeric_dtype(data[col]):
                worksheet.conditional_format(f'{chr(ord("A") + i)}{start_row+1}:{chr(ord("A") + i)}{end_row}', 
                                            {'type': 'data_bar', 'bar_color': '#4472C4'})

    async def _create_custom_sheet(self, writer, workbook, data, sheet_config):
        """Create custom analysis sheet with interactive filters based on user request"""
        sheet_name = sheet_config.get('name', 'Custom Analysis')
        analysis_type = sheet_config.get('type', 'summary')
        columns = sheet_config.get('columns', list(data.columns))
        
        # Create the worksheet
        worksheet = workbook.add_worksheet(sheet_name)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#70AD47',
            'font_color': 'white',
            'align': 'center'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E8F4F8',
            'border': 1,
            'align': 'center'
        })
        
        # Filter data based on configuration
        filtered_data = data[columns] if columns else data
        
        # Add title
        worksheet.merge_range('A1:F1', f'{sheet_name} - Interactive Analysis', title_format)
        
        row = 2
        
        if analysis_type == 'summary':
            summary = filtered_data.describe()
            
            # Add instructions
            worksheet.write(row, 0, "💡 Summary Statistics with Filters:")
            worksheet.write(row+1, 0, "• Click dropdown arrows to filter specific metrics")
            row += 3
            
            # Write summary with headers
            summary.to_excel(writer, sheet_name=sheet_name, startrow=row, startcol=0)
            
            # Apply auto-filter to summary data
            end_row = row + len(summary)
            end_col = len(summary.columns)
            end_col_letter = chr(ord('A') + end_col)
            filter_range = f'A{row}:{end_col_letter}{end_row}'
            worksheet.autofilter(filter_range)
            
        elif analysis_type == 'correlation':
            numeric_data = filtered_data.select_dtypes(include=[np.number])
            if len(numeric_data.columns) > 1:
                corr_matrix = numeric_data.corr()
                
                # Add instructions
                worksheet.write(row, 0, "💡 Correlation Matrix with Interactive Features:")
                worksheet.write(row+1, 0, "• Higher values indicate stronger correlations")
                worksheet.write(row+2, 0, "• Use filters to focus on specific relationships")
                row += 4
                
                # Write correlation matrix
                corr_matrix.to_excel(writer, sheet_name=sheet_name, startrow=row, startcol=0)
                
                # Apply conditional formatting for correlation values
                for i in range(len(corr_matrix)):
                    for j in range(len(corr_matrix.columns)):
                        cell_ref = f'{chr(ord("B") + j)}{row + 1 + i}'
                        worksheet.conditional_format(cell_ref, {
                            'type': '3_color_scale',
                            'min_color': '#F8CECC',
                            'mid_color': '#FFFFFF', 
                            'max_color': '#D5E8D4'
                        })
                
                # Apply filter
                end_row = row + len(corr_matrix)
                end_col = len(corr_matrix.columns)
                end_col_letter = chr(ord('A') + end_col)
                filter_range = f'A{row}:{end_col_letter}{end_row}'
                worksheet.autofilter(filter_range)
                
        else:
            # Default: write the filtered data with interactive features
            worksheet.write(row, 0, "💡 Interactive Data Analysis:")
            worksheet.write(row+1, 0, "• Click dropdown arrows in headers to filter data")
            worksheet.write(row+2, 0, "• Sort by clicking column headers")
            worksheet.write(row+3, 0, "• Select ranges to create custom charts")
            row += 5
            
            # Write headers
            for col_num, column_name in enumerate(filtered_data.columns):
                worksheet.write(row, col_num, column_name, header_format)
            
            # Write data
            for row_num, (_, row_data) in enumerate(filtered_data.iterrows(), row + 1):
                for col_num, value in enumerate(row_data):
                    worksheet.write(row_num, col_num, value)
            
            # Apply auto-filter
            end_row = row + len(filtered_data)
            end_col_letter = chr(ord('A') + len(filtered_data.columns) - 1)
            filter_range = f'A{row}:{end_col_letter}{end_row}'
            worksheet.autofilter(filter_range)
            
            # Add data bars for numeric columns
            for i, col in enumerate(filtered_data.columns):
                if pd.api.types.is_numeric_dtype(filtered_data[col]):
                    worksheet.conditional_format(f'{chr(ord("A") + i)}{row+1}:{chr(ord("A") + i)}{end_row}', 
                                                {'type': 'data_bar', 'bar_color': '#70AD47'})
        
        # Set column widths
        for i in range(min(10, len(columns) if columns else len(data.columns))):
            worksheet.set_column(i, i, 15)

class DataSourceConnector:
    """Handles connections to various data sources"""
    
    @staticmethod
    async def connect_to_database(connection_string: str, query: str) -> pd.DataFrame:
        """Connect to SQL database and execute query"""
        try:
            # Support for SQLite, PostgreSQL, MySQL, etc.
            if 'sqlite' in connection_string.lower():
                conn = sqlite3.connect(connection_string.replace('sqlite:///', ''))
                return pd.read_sql_query(query, conn)
            else:
                # For other databases, you would use appropriate connectors
                # This is a placeholder for future implementation
                raise NotImplementedError("Only SQLite supported currently")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    @staticmethod
    async def connect_to_api(api_url: str, headers: Dict = None) -> pd.DataFrame:
        """Connect to REST API and fetch data"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    data = await response.json()
                    return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"API connection error: {str(e)}")
            raise

    @staticmethod
    async def process_file_upload(file_content: bytes, file_type: str) -> pd.DataFrame:
        """Process uploaded file and return DataFrame"""
        if file_type.lower() in ['csv']:
            return pd.read_csv(BytesIO(file_content))
        elif file_type.lower() in ['xlsx', 'xls']:
            return pd.read_excel(BytesIO(file_content))
        elif file_type.lower() == 'json':
            import json
            data = json.loads(file_content.decode('utf-8'))
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

class MagicQuestionProcessor:
    """Processes natural language questions and generates appropriate analysis"""
    
    def __init__(self, openai_client=None):
        self.openai_client = openai_client or openai.ChatCompletion.create
        
    async def process_question(self, question: str, data: pd.DataFrame) -> Dict:
        """Process natural language question and determine analysis type"""
        
        # Use ChatGPT to analyze the question and determine analysis type
        try:
            response = await self.openai_client(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a data analyst. Analyze the user's question and suggest what type of analysis would be most appropriate. Consider: summary statistics, correlation analysis, time series analysis, comparison analysis, etc."},
                    {"role": "user", "content": f"Question: {question}. Data columns: {list(data.columns)}"}
                ]
            )
            
            # Use the response from ChatGPT to determine analysis type
            generated_text = response['choices'][0]['message']['content']
            analysis_config = self._parse_analysis_config(generated_text)
        except Exception as e:
            # Fallback to basic analysis if ChatGPT fails
            analysis_config = self._basic_analysis_config(question, data)
        
        question_lower = question.lower()
        
        analysis_config = {
            'type': 'comprehensive',
            'custom_sheets': [],
            'sql_queries': [],
            'visualizations': []
        }
        
        # Detect request for custom sheets
        if 'comparison' in question_lower or 'compare' in question_lower:
            analysis_config['custom_sheets'].append({
                'name': '🔍 Comparison Analysis',
                'type': 'correlation',
                'columns': list(data.select_dtypes(include=[np.number]).columns)
            })
            
        if 'internal' in question_lower or 'detailed' in question_lower:
            analysis_config['custom_sheets'].append({
                'name': '🔬 Detailed Analysis',
                'type': 'summary',
                'columns': list(data.columns)
            })
            
        # Detect SQL requirements
        if any(word in question_lower for word in ['group by', 'sum', 'count', 'average', 'max', 'min']):
            analysis_config['sql_queries'].append(self._generate_sql_from_question(question, data))
            
        return analysis_config
    
    def _generate_sql_from_question(self, question: str, data: pd.DataFrame) -> str:
        """Generate SQL query from natural language question"""
        # This is a simplified version - in production you'd use more sophisticated NLP
        
        table_name = "data_table"
        columns = list(data.columns)
        
        question_lower = question.lower()
        
        if 'total' in question_lower and 'by' in question_lower:
            # Find columns mentioned in the question
            mentioned_cols = [col for col in columns if col.lower() in question_lower]
            if len(mentioned_cols) >= 2:
                return f"SELECT {mentioned_cols[1]}, SUM({mentioned_cols[0]}) as total FROM {table_name} GROUP BY {mentioned_cols[1]}"
                
        return f"SELECT * FROM {table_name} LIMIT 100"

    def _parse_analysis_config(self, generated_text: str) -> Dict:
        """Parse the analysis configuration from generated text"""
        # Parse ChatGPT response to determine analysis type
        analysis_config = {
            'type': 'comprehensive',
            'custom_sheets': [],
            'sql_queries': [],
            'visualizations': []
        }
        
        text_lower = generated_text.lower()
        
        if 'correlation' in text_lower or 'relationship' in text_lower:
            analysis_config['custom_sheets'].append({
                'name': '🔍 Correlation Analysis',
                'type': 'correlation',
                'columns': []
            })
            
        if 'summary' in text_lower or 'statistics' in text_lower:
            analysis_config['custom_sheets'].append({
                'name': '📊 Summary Statistics',
                'type': 'summary',
                'columns': []
            })
            
        if 'time' in text_lower or 'trend' in text_lower:
            analysis_config['custom_sheets'].append({
                'name': '📈 Time Series Analysis',
                'type': 'time_series',
                'columns': []
            })
            
        return analysis_config
    
    def _basic_analysis_config(self, question: str, data: pd.DataFrame) -> Dict:
        """Basic fallback analysis configuration"""
        return {
            'type': 'comprehensive',
            'custom_sheets': [],
            'sql_queries': [],
            'visualizations': []
        }

async def demo_report_generation():
    """Demo function showing how to use the enhanced report generator"""
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'Date': dates,
        'Product': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor'], 100),
        'Category': np.random.choice(['Electronics', 'Accessories'], 100),
        'Sales': np.random.randint(100, 2000, 100),
        'Profit': np.random.randint(20, 500, 100),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    })
    
    # Initialize report generator
    generator = EnhancedReportGenerator()
    
    # Set up progress callback
    def progress_callback(progress: ProgressUpdate):
        print(f"Progress: {progress.percentage:.1f}% - {progress.message}")
    
    generator.set_progress_callback(progress_callback)
    
    # Define custom sheets
    custom_sheets = [
        {
            'name': '🔍 Comparison Analysis',
            'type': 'correlation',
            'columns': ['Sales', 'Profit']
        },
        {
            'name': '📈 Regional Performance',
            'type': 'summary',
            'columns': ['Region', 'Sales', 'Profit']
        }
    ]
    
    # Generate comprehensive report
    report_filename, analysis_summary = await generator.generate_comprehensive_report(
        data=sample_data,
        question="What are the sales trends by region and product category?",
        custom_sheets=custom_sheets,
        analysis_type="comprehensive"
    )
    
    print(f"Report generated: {report_filename}")
    return report_filename, analysis_summary

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_report_generation())
