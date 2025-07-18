import React, { useState } from 'react';
import {
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Chip,
  Paper,
  Grid
} from '@mui/material';
import { styled } from '@mui/material/styles';
import axios from 'axios';

const StyledCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
}));

const ResultCard = styled(Card)(({ theme }) => ({
  marginTop: theme.spacing(2),
  padding: theme.spacing(2),
}));

const SmartAnalysis = ({ onAnalysisComplete }) => {
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [tokenUsage, setTokenUsage] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setError(null);
  };

  const handleQueryChange = (event) => {
    setQuery(event.target.value);
  };

  const handleSmartAnalysis = async () => {
    if (!file || !query.trim()) {
      setError('Please select a file and enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setSessionId(null);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('query', query);

    try {
      const response = await axios.post('/api/brain/analyze-smart', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult(response.data.analysis_result); 
        setSessionId(response.data.session_id); 
        setTokenUsage(response.data.token_usage);
        
        if (onAnalysisComplete) {
          onAnalysisComplete(response.data);
        }
      } else {
        setError('Analysis failed');
      }
    } catch (error) {
      console.error('Smart analysis failed:', error);
      setError(error.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const suggestedQueries = [
    "What are the trends in my data?",
    "Show me the correlation between variables",
    "What's the distribution of values?",
    "Compare different categories",
    "Are there any outliers?",
    "What are the key statistics?"
  ];

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', padding: 2 }}>
      <StyledCard>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            🧠 AI Brain Analysis
          </Typography>
          <Typography variant="body1">
            Upload your data and ask any question - our AI brain will automatically 
            choose the best analysis method and create perfect visualizations!
          </Typography>
        </CardContent>
      </StyledCard>

      <Card>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                1. Upload Your Data
              </Typography>
              <input
                type="file"
                accept=".csv,.xlsx,.json"
                onChange={handleFileChange}
                style={{
                  padding: '10px',
                  border: '2px dashed #ccc',
                  borderRadius: '8px',
                  width: '100%',
                  cursor: 'pointer'
                }}
              />
              {file && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Selected: {file.name}
                </Typography>
              )}
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                2. Ask Your Question
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Ask any question about your data..."
                value={query}
                onChange={handleQueryChange}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Try these examples:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {suggestedQueries.map((suggestion, index) => (
                  <Chip
                    key={index}
                    label={suggestion}
                    onClick={() => setQuery(suggestion)}
                    variant="outlined"
                    size="small"
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleSmartAnalysis}
                disabled={!file || !query.trim() || loading}
                size="large"
                sx={{
                  background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                  color: 'white',
                  fontWeight: 'bold',
                  minWidth: 200
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : '🚀 Analyze with AI Brain'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {tokenUsage && (
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            <strong>Token Usage:</strong> {tokenUsage.total_tokens} tokens | 
            <strong> Cost:</strong> ${tokenUsage.cost.toFixed(4)} | 
            <strong> Model:</strong> GPT-4
          </Typography>
        </Alert>
      )}

      {result && (
        <ResultCard>
          <CardContent>
            <Typography variant="h5" gutterBottom color="primary">
              📊 Analysis Results
            </Typography>
            
            {result.insights && result.insights.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Key Insights:
                </Typography>
                {result.insights.map((insight, idx) => (
                  <Paper key={idx} sx={{ p: 2, mb: 1, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body1">{insight}</Typography>
                  </Paper>
                ))}
              </Box>
            )}

            {result?.chart_filename && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Visualization:
                </Typography>
                <iframe
                  src={`http://localhost:8000/api/brain/chart/${result.chart_filename}`}
                  width="100%"
                  height="500px"
                  style={{
                    border: '1px solid #ddd',
                    borderRadius: '8px'
                  }}
                  title="Analysis Chart"
                />
              </Box>
            )}

            {sessionId && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Data Summary:
                </Typography>
                <Paper sx={{ p: 2, maxHeight: 300, overflow: 'auto' }}>
                  <Button
                    variant="contained"
                    color="secondary"
                    sx={{ mt: 2 }}
                    onClick={() => window.open(`http://localhost:8000/api/brain/download-report/${sessionId}`, '_blank')}
                  >
                    Download Report
                  </Button>
                </Paper>
              </Box>
            )}
          </CardContent>
        </ResultCard>
      )}
    </Box>
  );
};

export default SmartAnalysis;
