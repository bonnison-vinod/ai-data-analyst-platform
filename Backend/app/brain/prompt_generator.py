# 🚀 Token-Optimized LLM Prompt Template for SaaS Efficiency

import json
from typing import Dict, Any, List, Optional

class OptimizedPromptGenerator:
    """Generate token-efficient prompts for LLM analysis decisions"""
    
    def __init__(self):
        # Compressed analysis type mappings
        self.analysis_map = {
            'ts': 'time_series', 'corr': 'correlation', 'piv': 'pivot',
            'dist': 'distribution', 'comp': 'comparison', 'out': 'outlier', 'stat': 'statistical'
        }
        
        # Compressed chart type mappings
        self.chart_map = {
            'L': 'line', 'B': 'bar', 'P': 'pie', 'S': 'scatter', 
            'H': 'histogram', 'X': 'box', 'M': 'heatmap'
        }
    
    def compress_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Compress metadata to essential information only"""
        return {
            'cols': metadata.get('columns', [])[:10],  # Limit to first 10 columns
            'nums': metadata.get('numeric_columns', []),
            'cats': metadata.get('categorical_columns', []),
            'dates': metadata.get('date_columns', []),
            'shape': metadata.get('shape', (0, 0)),
            'nulls': {k: v for k, v in metadata.get('missing_values', {}).items() if v > 0},  # Only non-zero nulls
            'stats': self._compress_stats(metadata.get('sample_stats', {}))
        }
    
    def _compress_stats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Compress statistics to essential metrics only"""
        compressed = {}
        for col, data in stats.items():
            if isinstance(data, dict):
                compressed[col] = {
                    'avg': round(data.get('mean', 0), 2),
                    'min': round(data.get('min', 0), 2),
                    'max': round(data.get('max', 0), 2)
                }
        return compressed
    
    def generate_analysis_prompt(self, metadata: Dict[str, Any], user_query: str) -> str:
        """Generate ultra-compact analysis prompt"""
        
        # Compress metadata
        meta = self.compress_metadata(metadata)
        
        prompt = f"""Data Analysis Brain - Choose optimal analysis for SaaS platform.

DATA: {json.dumps(meta, separators=(',', ':'))}
QUERY: "{user_query}"

RULES:
- ts: time trends (need date col)
- corr: relationships (need 2+ nums)  
- piv: group summaries (need cat+num)
- dist: data spread (need 1 num)
- comp: group differences (need cat+num)
- out: anomalies (need 1 num)
- stat: descriptive stats (need 1 num)

CHARTS: L=line, B=bar, P=pie, S=scatter, H=histogram, X=box, M=heatmap

OUTPUT JSON:
{{
  "analysis_type": "ts|corr|piv|dist|comp|out|stat",
  "chart_type": "L|B|P|S|H|X|M",
  "group_by": "col_name|null",
  "aggregation": "sum|mean|count|null",
  "time_column": "col_name|null",
  "value_columns": ["col1","col2"],
  "confidence": 0.9
}}"""

        return prompt
    
    def generate_insight_prompt(self, analysis_result: Dict[str, Any], user_query: str) -> str:
        """Generate compact insight prompt"""
        
        # Extract only essential result data
        essential_data = {
            'data': analysis_result.get('data', [])[:5],  # Limit to first 5 rows
            'insights': analysis_result.get('insights', []),
            'chart_path': analysis_result.get('chart_path', '')
        }
        
        prompt = f"""Generate business insights from analysis.

QUERY: "{user_query}"
RESULTS: {json.dumps(essential_data, separators=(',', ':'))}

OUTPUT JSON:
{{
  "key_findings": ["finding1", "finding2", "finding3"],
  "recommendations": ["action1", "action2"],
  "summary": "one sentence summary"
}}"""

        return prompt
    
    def generate_smart_prompt(self, metadata: Dict[str, Any], user_query: str) -> str:
        """Generate intelligent, context-aware prompt with token optimization"""
        
        # Analyze query to determine focus
        query_lower = user_query.lower()
        
        # Smart metadata filtering based on query
        relevant_meta = self._filter_relevant_metadata(metadata, query_lower)
        
        # Determine likely analysis type from query keywords
        likely_analysis = self._predict_analysis_type(query_lower)
        
        # Enhanced analysis for complex queries
        query_components = self._parse_query_components(query_lower)
        
        prompt = f"""DATA: {json.dumps(relevant_meta, separators=(',', ':'))}
QUERY: "{user_query}"
FOCUS: {query_components.get('focus', 'analysis')}
DIMENSIONS: {query_components.get('dimensions', [])}
MEASURES: {query_components.get('measures', [])}

RULES:
- piv: multi-dimensional breakdown (best for complex queries)
- ts: time trends | corr: relationships | comp: comparisons
- B: bar charts (best for categories) | L: line | P: pie
- For multi-dim queries: use piv + B + "dim1|dim2|dim3" grouping

JSON OUTPUT:
{{
  "analysis_type": "piv",
  "chart_type": "B",
  "group_by": "region|category|product",
  "agg": "sum",
  "time_col": "null",
  "value_cols": ["sales", "profit"],
  "conf": 0.9
}}"""

        return prompt
    
    def _filter_relevant_metadata(self, metadata: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Filter metadata to only relevant information based on query"""
        
        relevant = {'shape': metadata.get('shape', (0, 0))}
        
        # Extract mentioned columns from query
        all_cols = metadata.get('columns', [])
        mentioned_cols = [col for col in all_cols if col.lower() in query]
        
        if mentioned_cols:
            relevant['cols'] = mentioned_cols
        else:
            # Include all column types if no specific columns mentioned
            relevant['nums'] = metadata.get('numeric_columns', [])[:5]
            relevant['cats'] = metadata.get('categorical_columns', [])[:5]
            relevant['dates'] = metadata.get('date_columns', [])
        
        # Include stats only for relevant columns
        stats = metadata.get('sample_stats', {})
        if mentioned_cols:
            relevant['stats'] = {col: self._compress_single_stat(stats.get(col, {})) 
                               for col in mentioned_cols if col in stats}
        elif len(stats) <= 3:
            relevant['stats'] = {col: self._compress_single_stat(data) 
                               for col, data in list(stats.items())[:3]}
        
        return relevant
    
    def _compress_single_stat(self, stat: Dict[str, Any]) -> Dict[str, Any]:
        """Compress single column statistics"""
        if not stat:
            return {}
        return {
            'avg': round(stat.get('mean', 0), 1),
            'range': [round(stat.get('min', 0), 1), round(stat.get('max', 0), 1)]
        }
    
    def _predict_analysis_type(self, query: str) -> str:
        """Predict likely analysis type from query keywords"""
        
        # Time series indicators
        if any(word in query for word in ['trend', 'over time', 'time series', 'change', 'growth']):
            return 'ts'
        
        # Correlation indicators
        if any(word in query for word in ['relationship', 'correlation', 'related', 'affect']):
            return 'corr'
        
        # Pivot indicators
        if any(word in query for word in ['by', 'group', 'category', 'total', 'sum', 'average']):
            return 'piv'
        
        # Distribution indicators
        if any(word in query for word in ['distribution', 'spread', 'histogram', 'pattern']):
            return 'dist'
        
        # Comparison indicators
        if any(word in query for word in ['compare', 'difference', 'vs', 'versus', 'between']):
            return 'comp'
        
        # Outlier indicators
        if any(word in query for word in ['outlier', 'anomaly', 'unusual', 'exception']):
            return 'out'
        
        # Default to pivot for summary questions
        return 'piv'
    
    def _parse_query_components(self, query: str) -> Dict[str, Any]:
        """Parse complex query to identify requested dimensions and measures"""
        components = {
            'focus': 'General analysis',
            'dimensions': [],
            'measures': [],
            'grouping': [],
            'comparison': 'None'
        }
        
        # Common business dimension keywords
        dimension_keywords = {
            'product': ['product', 'item', 'goods', 'merchandise'],
            'category': ['category', 'type', 'class', 'group'],
            'region': ['region', 'area', 'location', 'territory', 'zone'],
            'customer': ['customer', 'client', 'buyer', 'user'],
            'time': ['time', 'date', 'period', 'month', 'quarter', 'year'],
            'channel': ['channel', 'platform', 'medium', 'source']
        }
        
        # Common business measure keywords
        measure_keywords = {
            'sales': ['sales', 'revenue', 'selling', 'sold', 'income'],
            'profit': ['profit', 'profitability', 'margin', 'earnings'],
            'quantity': ['quantity', 'volume', 'amount', 'units'],
            'price': ['price', 'cost', 'value', 'rate'],
            'growth': ['growth', 'increase', 'change', 'trend']
        }
        
        # Identify dimensions
        for dim, keywords in dimension_keywords.items():
            if any(kw in query for kw in keywords):
                components['dimensions'].append(dim)
        
        # Identify measures
        for measure, keywords in measure_keywords.items():
            if any(kw in query for kw in keywords):
                components['measures'].append(measure)
        
        # Determine focus
        if 'best' in query or 'top' in query or 'highest' in query:
            components['focus'] = 'Top performers identification'
        elif 'worst' in query or 'bottom' in query or 'lowest' in query:
            components['focus'] = 'Underperformers identification'
        elif 'compare' in query or 'comparison' in query:
            components['focus'] = 'Comparative analysis'
        elif 'trend' in query or 'over time' in query:
            components['focus'] = 'Trend analysis'
        
        # Determine grouping requirements
        if 'by' in query or 'per' in query or 'each' in query:
            # Extract grouping hints
            if 'by region' in query or 'each region' in query:
                components['grouping'].append('region')
            if 'by category' in query or 'each category' in query:
                components['grouping'].append('category')
            if 'by product' in query or 'each product' in query:
                components['grouping'].append('product')
        
        # Set default grouping if dimensions are mentioned
        if not components['grouping'] and components['dimensions']:
            components['grouping'] = components['dimensions'][:3]  # Limit to 3 levels
        
        # Determine comparison type
        if 'vs' in query or 'versus' in query or 'compared to' in query:
            components['comparison'] = 'Direct comparison'
        elif 'both' in query or 'all' in query:
            components['comparison'] = 'Multiple group comparison'
        
        return components
    
    def generate_followup_prompt(self, previous_analysis: Dict[str, Any], user_query: str) -> str:
        """Generate compact follow-up prompt"""
        
        # Extract minimal context from previous analysis
        context = {
            'type': previous_analysis.get('analysis_type', ''),
            'cols': previous_analysis.get('value_columns', []),
            'insights': previous_analysis.get('insights', [])[:2]  # Max 2 insights
        }
        
        prompt = f"""Follow-up analysis recommendation.

PREV: {json.dumps(context, separators=(',', ':'))}
NEW_Q: "{user_query}"

JSON:
{{
  "next_analysis": "ts|corr|piv|dist|comp|out|stat",
  "reasoning": "brief reason",
  "priority": "H|M|L"
}}"""

        return prompt
    
    def estimate_tokens(self, prompt: str) -> int:
        """Estimate token count for cost calculation"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(prompt) // 4
    
    def optimize_for_model(self, prompt: str, model_type: str = "gpt-4") -> str:
        """Optimize prompt for specific model capabilities"""
        
        if model_type == "gpt-3.5-turbo":
            # More explicit instructions for GPT-3.5
            return prompt.replace("HINT:", "ANALYSIS_HINT:")
        elif model_type == "gpt-4":
            # GPT-4 can handle more compressed format
            return prompt.replace("OUTPUT JSON:", "JSON:")
        
        return prompt

# Token usage tracking for SaaS cost management
class TokenTracker:
    """Track token usage for cost optimization"""
    
    def __init__(self):
        self.total_tokens = 0
        self.requests = 0
        self.costs = {
            'gpt-4': 0.03,  # per 1K tokens
            'gpt-3.5-turbo': 0.002  # per 1K tokens
        }
    
    def track_request(self, prompt: str, response: str, model: str = "gpt-4"):
        """Track tokens used in a request"""
        prompt_tokens = len(prompt) // 4
        response_tokens = len(response) // 4
        total = prompt_tokens + response_tokens
        
        self.total_tokens += total
        self.requests += 1
        
        cost = (total / 1000) * self.costs.get(model, 0.03)
        
        return {
            'prompt_tokens': prompt_tokens,
            'response_tokens': response_tokens,
            'total_tokens': total,
            'cost': cost
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_tokens': self.total_tokens,
            'total_requests': self.requests,
            'avg_tokens_per_request': self.total_tokens / max(self.requests, 1),
            'estimated_cost': self.total_tokens / 1000 * 0.03
        }

# Example usage
def main():
    generator = OptimizedPromptGenerator()
    tracker = TokenTracker()
    
    # Example metadata
    metadata = {
        'columns': ['date', 'sales', 'region', 'category', 'profit'],
        'numeric_columns': ['sales', 'profit'],
        'categorical_columns': ['region', 'category'],
        'date_columns': ['date'],
        'shape': (1000, 5),
        'sample_stats': {
            'sales': {'mean': 5000, 'max': 20000, 'min': 100},
            'profit': {'mean': 1200, 'max': 5000, 'min': 50}
        }
    }
    
    # Generate optimized prompt
    prompt = generator.generate_smart_prompt(metadata, "What are sales trends by category?")
    
    # Estimate tokens
    tokens = generator.estimate_tokens(prompt)
    
    print(f"Optimized Prompt ({tokens} tokens):")
    print(prompt)
    print(f"\nEstimated cost: ${(tokens/1000) * 0.03:.4f}")

if __name__ == "__main__":
    main()
