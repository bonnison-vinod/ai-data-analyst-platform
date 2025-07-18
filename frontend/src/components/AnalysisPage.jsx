import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  LinearProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Collapse,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  CloudUpload,
  Analytics,
  Download,
  Send,
  Refresh,
  Help,
  Assessment,
  DataObject,
  InsertChart,
  FilePresent,
  CheckCircle,
  Error,
  Warning,
  Info,
  ExpandMore,
  PlayArrow,
  Stop,
  Visibility,
  Share,
  Settings,
  AutoAwesome,
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

// Sample questions for different analysis types
const SAMPLE_QUESTIONS = {
  sales: [
    "What are the top performing products by revenue?",
    "Show me monthly sales trends and patterns",
    "Which customers generate the most revenue?",
    "What's the seasonal trend in sales performance?",
    "Analyze sales by region and identify opportunities"
  ],
  marketing: [
    "Which marketing channels have the highest ROI?",
    "What's the customer acquisition cost by channel?",
    "Show me conversion rates across different campaigns",
    "Analyze customer lifetime value patterns",
    "What's the impact of marketing spend on revenue?"
  ],
  operations: [
    "What are the main operational bottlenecks?",
    "Show me efficiency metrics and trends",
    "Analyze resource utilization patterns",
    "What's the impact of process changes on performance?",
    "Identify cost reduction opportunities"
  ],
  financial: [
    "What are the key financial performance indicators?",
    "Show me profitability analysis by product/service",
    "Analyze cash flow patterns and forecasts",
    "What are the main cost drivers?",
    "Show me budget vs actual performance"
  ],
  custom: [
    "Provide comprehensive analysis of this data",
    "Show me the most important insights",
    "What patterns and trends do you see?",
    "Identify outliers and anomalies",
    "Generate a complete executive summary"
  ]
};

const analysisSteps = [
  'Upload File',
  'Ask Question',
  'Processing',
  'Review Results',
  'Download Report'
];

function FileUploadArea({ onFileSelect, selectedFile, uploading }) {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const droppedFile = event.dataTransfer.files[0];
    onFileSelect(droppedFile);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    onFileSelect(file);
  };

  return (
    <Box
      sx={{
        border: '2px dashed',
        borderColor: dragOver ? 'primary.main' : selectedFile ? 'success.main' : 'divider',
        borderRadius: 3,
        p: 4,
        textAlign: 'center',
        backgroundColor: dragOver ? 'action.hover' : selectedFile ? 'success.light' : 'background.paper',
        cursor: uploading ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s ease',
        '&:hover': {
          backgroundColor: uploading ? 'inherit' : 'action.hover',
        },
      }}
      onDragOver={(e) => { e.preventDefault(); !uploading && setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => !uploading && document.getElementById('file-input').click()}
    >
      <input
        id="file-input"
        type="file"
        hidden
        accept=".csv,.xlsx,.xls,.json"
        onChange={handleFileChange}
        disabled={uploading}
      />
      
      {selectedFile ? (
        <Box>
          <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            {selectedFile.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Chip 
              label={selectedFile.type || 'Unknown Type'} 
              size="small" 
              color="success" 
              variant="outlined" 
            />
          </Box>
        </Box>
      ) : (
        <Box>
          <CloudUpload sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            Drop your file here or click to browse
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Supports CSV, Excel (XLSX/XLS), and JSON files
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Maximum file size: 100MB
          </Typography>
        </Box>
      )}
    </Box>
  );
}

function QuestionInput({ question, onQuestionChange, onQuestionSuggest, disabled }) {
  const [selectedCategory, setSelectedCategory] = useState('custom');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSuggestionClick = (suggestion) => {
    onQuestionChange(suggestion);
    setShowSuggestions(false);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mr: 2 }}>
          What would you like to analyze?
        </Typography>
        <Tooltip title="Get AI-powered question suggestions">
          <IconButton onClick={() => setShowSuggestions(!showSuggestions)} size="small">
            <AutoAwesome />
          </IconButton>
        </Tooltip>
      </Box>

      <TextField
        fullWidth
        multiline
        rows={4}
        label="Your Analysis Question"
        value={question}
        onChange={(e) => onQuestionChange(e.target.value)}
        placeholder="Ask anything about your data... e.g., 'What are the key trends in sales performance?' or 'Show me the most important insights from this data'"
        disabled={disabled}
        sx={{ mb: 2 }}
      />

      <Collapse in={showSuggestions}>
        <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
            Question Suggestions by Category
          </Typography>
          
          <FormControl size="small" sx={{ mb: 2, minWidth: 200 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              label="Category"
            >
              <MenuItem value="sales">Sales Analysis</MenuItem>
              <MenuItem value="marketing">Marketing Analysis</MenuItem>
              <MenuItem value="operations">Operations Analysis</MenuItem>
              <MenuItem value="financial">Financial Analysis</MenuItem>
              <MenuItem value="custom">General Analysis</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
            {SAMPLE_QUESTIONS[selectedCategory].map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                sx={{ m: 0.5, cursor: 'pointer' }}
                variant="outlined"
                color="primary"
              />
            ))}
          </Box>
        </Paper>
      </Collapse>
    </Box>
  );
}

function ProgressTracker({ sessionId, onComplete, onError }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('initializing');
  const [message, setMessage] = useState('');
  const [currentStep, setCurrentStep] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      console.log('No session ID, skipping progress polling');
      return;
    }

    console.log('Starting progress polling for session:', sessionId);

    const pollProgress = async () => {
      try {
        console.log('Polling progress for:', sessionId);
        const response = await axios.get(`${API_BASE}/report-progress/${sessionId}`);
        const data = response.data;
        
        console.log('Progress data:', data);
        
        setProgress(data.percentage || 0);
        setStatus(data.status || 'unknown');
        setMessage(data.message || '');
        setCurrentStep(data.current_step || '');
        
        if (data.completed) {
          console.log('Analysis completed:', data);
          if (data.error) {
            console.error('Analysis error:', data.error);
            setError(data.error);
            onError(data.error);
          } else {
            console.log('Analysis successful, calling onComplete');
            onComplete(data);
          }
        }
      } catch (err) {
        console.error('Progress polling error:', err);
        setError('Failed to check progress');
        onError('Failed to check progress');
      }
    };

    const interval = setInterval(pollProgress, 2000);
    pollProgress(); // Initial call

    return () => {
      console.log('Cleaning up progress polling');
      clearInterval(interval);
    };
  }, [sessionId, onComplete, onError]);

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Typography variant="h6">Analysis Failed</Typography>
        <Typography variant="body2">{error}</Typography>
      </Alert>
    );
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <CircularProgress size={24} sx={{ mr: 2 }} />
        <Typography variant="h6">Processing Your Analysis...</Typography>
      </Box>
      
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ mb: 2, height: 8, borderRadius: 4 }}
      />
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {message || 'Processing...'}
      </Typography>
      
      <Typography variant="caption" color="text.secondary">
        Step: {currentStep} • {progress.toFixed(1)}% Complete
      </Typography>
    </Box>
  );
}

function ResultsPanel({ sessionId, analysisData, onDownload }) {
  const [tabValue, setTabValue] = useState(0);

  const handleDownload = async () => {
    try {
      const downloadUrl = `${API_BASE}/download-report/${sessionId}`;
      window.open(downloadUrl, '_blank');
      onDownload();
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <Box>
      <Alert severity="success" sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h6">Analysis Complete! 🎉</Typography>
            <Typography variant="body2">
              Your comprehensive analysis report is ready for download.
            </Typography>
          </Box>
          <Button 
            variant="contained" 
            color="success"
            startIcon={<Download />}
            onClick={handleDownload}
          >
            Download Report
          </Button>
        </Box>
      </Alert>

      <Paper elevation={1} sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Summary" />
          <Tab label="Data Overview" />
          <Tab label="Next Steps" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Analysis Summary</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Your data analysis has been completed successfully. The report includes:
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><InsertChart /></ListItemIcon>
                  <ListItemText 
                    primary="Interactive Dashboard" 
                    secondary="Visual charts and graphs of your data"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Assessment /></ListItemIcon>
                  <ListItemText 
                    primary="Statistical Analysis" 
                    secondary="Detailed statistical insights and trends"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><DataObject /></ListItemIcon>
                  <ListItemText 
                    primary="Data Cleaning & Processing" 
                    secondary="Clean, structured data ready for use"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><FilePresent /></ListItemIcon>
                  <ListItemText 
                    primary="Executive Summary" 
                    secondary="Key findings and recommendations"
                  />
                </ListItem>
              </List>
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Data Overview</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        Session Information
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Session ID: {sessionId}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Generated: {new Date().toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        Report Format
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Excel (.xlsx) with multiple sheets
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Interactive charts and pivot tables
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Next Steps</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Now that your analysis is complete, here are some suggested next steps:
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><Download /></ListItemIcon>
                  <ListItemText 
                    primary="Download the Report" 
                    secondary="Open the Excel file to explore interactive charts and detailed analysis"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Share /></ListItemIcon>
                  <ListItemText 
                    primary="Share with Team" 
                    secondary="Share insights with stakeholders and team members"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><PlayArrow /></ListItemIcon>
                  <ListItemText 
                    primary="Take Action" 
                    secondary="Implement recommendations based on the insights"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><Refresh /></ListItemIcon>
                  <ListItemText 
                    primary="Analyze More Data" 
                    secondary="Upload additional datasets for comparison"
                  />
                </ListItem>
              </List>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
}

export default function AnalysisPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    if (file) {
      setActiveStep(1);
    }
  };

  const handleQuestionChange = (newQuestion) => {
    setQuestion(newQuestion);
    setError(null);
  };

  const handleStartAnalysis = async () => {
    console.log('🚀 Starting analysis...', { 
      selectedFile: selectedFile ? selectedFile.name : 'null', 
      question: question.substring(0, 100) + (question.length > 100 ? '...' : ''),
      uploading,
      activeStep
    });
    
    if (!selectedFile || !question.trim()) {
      console.log('❌ Validation failed:', { selectedFile: !!selectedFile, question: !!question.trim() });
      setError('Please select a file and enter a question');
      return;
    }

    console.log('✅ Validation passed, setting uploading to true');
    setUploading(true);
    setError(null);

    try {
      console.log('📦 Creating FormData...');
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('question', question);
      
      console.log('🌐 Making API call to:', `${API_BASE}/generate-enhanced-report/`);
      console.log('📋 FormData contents:', {
        file: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type,
        question: question.substring(0, 100) + '...'
      });
      
      const response = await axios.post(`${API_BASE}/generate-enhanced-report/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000, // 60 seconds timeout
      });
      
      console.log('✅ API Response received:', response.data);
      
      if (response.data && response.data.session_id) {
        console.log('📝 Setting session ID and moving to step 2:', response.data.session_id);
        setSessionId(response.data.session_id);
        setActiveStep(2); // Move to processing step only after getting session ID
      } else {
        throw new Error('No session ID received from server');
      }
      
    } catch (err) {
      console.error('❌ Analysis failed:', err);
      
      let errorMessage = 'Failed to start analysis. Please try again.';
      
      if (err.response) {
        // Server responded with error status
        console.error('Server error response:', err.response.data);
        errorMessage = `Server Error: ${err.response.status} - ${err.response.data?.detail || err.response.statusText}`;
      } else if (err.request) {
        // Request was made but no response received
        console.error('No response received:', err.request);
        errorMessage = 'No response from server. Please check if the backend is running.';
      } else {
        // Something else happened
        console.error('Request setup error:', err.message);
        errorMessage = `Error: ${err.message}`;
      }
      
      setError(errorMessage);
      setActiveStep(1);
    } finally {
      // Always reset uploading state
      console.log('🔄 Resetting uploading state to false');
      setUploading(false);
    }
  };

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setActiveStep(3);
    setUploading(false);
  };

  const handleAnalysisError = (errorMessage) => {
    setError(errorMessage);
    setActiveStep(1);
    setUploading(false);
  };

  const handleDownload = () => {
    setActiveStep(4);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedFile(null);
    setQuestion('');
    setSessionId(null);
    setAnalysisData(null);
    setError(null);
    setUploading(false);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 2 }}>
          AI Data Analysis Platform
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Upload your data, ask questions, and get comprehensive analysis reports
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 4 }}>
          <Chip 
            icon={<CloudUpload />} 
            label="Upload Files" 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            icon={<AutoAwesome />} 
            label="Ask Questions" 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            icon={<Analytics />} 
            label="Get Insights" 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            icon={<Download />} 
            label="Download Report" 
            color="primary" 
            variant="outlined" 
          />
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Debug Panel */}
      <Paper elevation={1} sx={{ p: 2, mb: 3, backgroundColor: '#f5f5f5' }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>Debug Info:</Typography>
        <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
          Current Step: {activeStep} ({analysisSteps[activeStep]}){"\n"}
          File Selected: {selectedFile ? `${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)` : 'None'}{"\n"}
          Question: {question ? `"${question.substring(0, 50)}${question.length > 50 ? '...' : ''}"` : 'None'}{"\n"}
          Session ID: {sessionId || 'None'}{"\n"}
          Uploading: {uploading ? 'Yes' : 'No'}{"\n"}
          Error: {error ? 'Yes' : 'No'}
        </Typography>
      </Paper>

      {/* Main Content */}
      <Grid container spacing={4}>
        {/* Left Side - Steps */}
        <Grid item xs={12} md={4}>
          <Paper elevation={1} sx={{ p: 3, position: 'sticky', top: 20 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Analysis Steps
            </Typography>
            <Stepper activeStep={activeStep} orientation="vertical">
              {analysisSteps.map((label, index) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                  <StepContent>
                    <Typography variant="body2" color="text.secondary">
                      {index === 0 && "Select your data file to analyze"}
                      {index === 1 && "Ask a specific question about your data"}
                      {index === 2 && "AI is processing your data and generating insights"}
                      {index === 3 && "Review your analysis results and insights"}
                      {index === 4 && "Download your comprehensive report"}
                    </Typography>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
            
            {activeStep === 4 && (
              <Box sx={{ mt: 3 }}>
                <Button 
                  variant="outlined" 
                  onClick={handleReset}
                  fullWidth
                  startIcon={<Refresh />}
                >
                  Start New Analysis
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right Side - Main Content */}
        <Grid item xs={12} md={8}>
          <Paper elevation={1} sx={{ p: 4 }}>
            {/* Step 1: File Upload */}
            {activeStep === 0 && (
              <Box>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  Upload Your Data File
                </Typography>
                <FileUploadArea 
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile}
                  uploading={uploading}
                />
              </Box>
            )}

            {/* Step 2: Question Input */}
            {activeStep === 1 && (
              <Box>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  Ask Your Question
                </Typography>
                <QuestionInput 
                  question={question}
                  onQuestionChange={handleQuestionChange}
                  disabled={uploading}
                />
                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button 
                    variant="outlined" 
                    onClick={() => setActiveStep(0)}
                    disabled={uploading}
                  >
                    Back
                  </Button>
                  <Button 
                    variant="contained" 
                    onClick={handleStartAnalysis}
                    disabled={!question.trim() || uploading}
                    startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <Send />}
                    sx={{ 
                      minWidth: 200,
                      position: 'relative',
                      '&:disabled': {
                        opacity: 0.7
                      }
                    }}
                  >
                    {uploading ? 'Starting Analysis...' : 'Upload & Analyze'}
                  </Button>
                </Box>
              </Box>
            )}

            {/* Step 3: Processing */}
            {activeStep === 2 && (
              <Box>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  Processing Your Analysis
                </Typography>
                <ProgressTracker 
                  sessionId={sessionId}
                  onComplete={handleAnalysisComplete}
                  onError={handleAnalysisError}
                />
              </Box>
            )}

            {/* Step 4: Results */}
            {activeStep === 3 && (
              <Box>
                <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                  Analysis Results
                </Typography>
                <ResultsPanel 
                  sessionId={sessionId}
                  analysisData={analysisData}
                  onDownload={handleDownload}
                />
              </Box>
            )}

            {/* Step 5: Complete */}
            {activeStep === 4 && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                  Analysis Complete!
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Your comprehensive analysis report has been downloaded successfully.
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={handleReset}
                  startIcon={<Refresh />}
                  size="large"
                >
                  Start New Analysis
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
