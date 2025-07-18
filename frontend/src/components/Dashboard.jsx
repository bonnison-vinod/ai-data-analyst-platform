import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  LinearProgress,
  Chip,
  Alert,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tab,
  Tabs,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Upload,
  Assessment,
  CloudUpload,
  Analytics,
  Refresh,
  Download,
  Add,
  Close,
} from '@mui/icons-material';
import axios from 'axios';

// API Base URL
const API_BASE = 'http://127.0.0.1:8000/api';

// Test backend connection
const testConnection = async () => {
  try {
    console.log('🔄 Testing backend connection...');
    
    // First try the health endpoint
    console.log('Testing health endpoint:', `${API_BASE}/health`);
    const healthResponse = await axios.get(`${API_BASE}/health`);
    console.log('✅ Health check successful:', healthResponse.data);
    
    // Then try the sessions endpoint
    console.log('Testing sessions endpoint:', `${API_BASE}/sessions/`);
    const sessionsResponse = await axios.get(`${API_BASE}/sessions/`);
    console.log('✅ Sessions endpoint successful:', sessionsResponse.data);
    
    return true;
  } catch (error) {
    console.error('❌ Backend connection failed:', error);
    console.error('Error details:', {
      code: error.code,
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
    
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('❌ Backend server is not running or not accessible on port 8000');
    } else if (error.response) {
      console.error('❌ Server responded with error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('❌ No response from server - possible CORS issue or network problem');
    }
    return false;
  }
};

// Stat Card Component
function StatCard({ title, value, change, trend, icon, color = 'primary' }) {
  const isPositive = trend === 'up';
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${color === 'primary' ? '#1a365d' : '#d69e2e'} 0%, ${color === 'primary' ? '#2d5a85' : '#b7791f'} 100%)`,
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <CardContent sx={{ pb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 600, opacity: 0.9 }}>
            {title}
          </Typography>
          <Box sx={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.2)', 
            borderRadius: '50%', 
            p: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {icon}
          </Box>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          {value}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isPositive ? (
            <TrendingUp sx={{ fontSize: 16, color: '#4ade80' }} />
          ) : (
            <TrendingDown sx={{ fontSize: 16, color: '#f87171' }} />
          )}
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {change}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// Quick Action Card
function QuickActionCard({ title, description, icon, onClick, disabled = false }) {
  return (
    <Card 
      sx={{ 
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s ease',
        opacity: disabled ? 0.6 : 1,
        '&:hover': {
          transform: disabled ? 'none' : 'translateY(-4px)',
          boxShadow: disabled ? 'none' : '0 8px 25px rgba(0, 0, 0, 0.15)',
        },
      }}
      onClick={disabled ? undefined : onClick}
    >
      <CardContent sx={{ textAlign: 'center', py: 3 }}>
        <Box sx={{
          mb: 2,
          color: 'primary.main',
          display: 'flex',
          justifyContent: 'center'
        }}>
          {icon}
        </Box>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
}

// Upload Dialog Component
function UploadDialog({ open, onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState('');
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [progressMessage, setProgressMessage] = useState('');
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const droppedFile = event.dataTransfer.files[0];
    setFile(droppedFile);
  };

  // Poll for progress updates
  const pollProgress = async (sessionId) => {
    try {
      const response = await axios.get(`${API_BASE}/report-progress/${sessionId}`);
      const { progress, status, message } = response.data;
      
      setProgress(progress);
      setProgressMessage(message || `Analysis ${progress}% complete`);
      
      if (status === 'completed') {
        setAnalysisComplete(true);
        setDownloadUrl(`${API_BASE}/download-report/${sessionId}`);
        setProgressMessage('Analysis completed! Ready for download.');
      } else if (status === 'failed') {
        setProgressMessage('Analysis failed. Please try again.');
        setUploading(false);
      } else {
        // Continue polling if not complete
        setTimeout(() => pollProgress(sessionId), 2000);
      }
    } catch (error) {
      console.error('Progress polling failed:', error);
      setProgressMessage('Error checking progress. Please try again.');
      setUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }
    
    console.log('🚀 Starting upload from Dashboard...');
    
    setUploading(true);
    setProgress(0);
    setAnalysisComplete(false);
    setProgressMessage('Starting analysis...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('question', question || 'Analyze this data');
    
    try {
      console.log('📤 Sending request to backend...');
      const response = await axios.post(`${API_BASE}/generate-enhanced-report/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000
      });
      
      console.log('✅ Response received:', response.data);
      
      const { session_id } = response.data;
      if (session_id) {
        setSessionId(session_id);
        setProgressMessage('Analysis started. Processing your data...');
        
        // Start polling for progress
        pollProgress(session_id);
      } else {
        throw new Error('No session ID received from server');
      }
      
    } catch (error) {
      console.error('❌ Upload failed:', error);
      let errorMessage = 'Upload failed. Please try again.';
      
      if (error.response) {
        errorMessage = `Server Error: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`;
      } else if (error.request) {
        errorMessage = 'No response from server. Please check if the backend is running.';
      } else {
        errorMessage = `Error: ${error.message}`;
      }
      
      setProgressMessage(errorMessage);
      setUploading(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank');
    }
  };

  const handleClose = () => {
    onClose();
    setFile(null);
    setQuestion('');
    setProgress(0);
    setSessionId(null);
    setAnalysisComplete(false);
    setProgressMessage('');
    setDownloadUrl(null);
    setUploading(false);
  };

  return (
    <Dialog open={open} onClose={uploading ? undefined : handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {uploading ? 'Processing Analysis...' : 'Upload Data File'}
        <IconButton onClick={handleClose} disabled={uploading}>
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        {/* Debug Panel */}
        <Box sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5', borderRadius: 1, fontFamily: 'monospace', fontSize: '0.8rem' }}>
          <strong>Debug Info:</strong><br/>
          Backend URL: {API_BASE}<br/>
          File: {file ? `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)` : 'None'}<br/>
          Question: {question || 'None'}<br/>
          Uploading: {uploading ? 'Yes' : 'No'}<br/>
          Progress: {progress}%<br/>
          Session ID: {sessionId || 'None'}<br/>
          Analysis Complete: {analysisComplete ? 'Yes' : 'No'}<br/>
          Download URL: {downloadUrl ? 'Ready' : 'Not ready'}<br/>
          <Button 
            size="small" 
            variant="outlined" 
            onClick={() => testConnection()} 
            sx={{ mt: 1, fontSize: '0.7rem' }}
          >
            Test Backend Connection
          </Button>
        </Box>
        
        <Box
          sx={{
            border: '2px dashed',
            borderColor: dragOver ? 'primary.main' : 'divider',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            mb: 3,
            backgroundColor: dragOver ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1 }}>
            {file ? file.name : 'Drop your file here or click to browse'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Supports CSV, Excel, JSON files
          </Typography>
          <input
            id="file-input"
            type="file"
            hidden
            accept=".csv,.xlsx,.xls,.json"
            onChange={handleFileChange}
          />
        </Box>
        
        <TextField
          fullWidth
          label="Analysis Question (Optional)"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What would you like to know about this data?"
          multiline
          rows={3}
          disabled={uploading}
        />
        
        {/* Progress Section */}
        {uploading && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {progressMessage}
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ mb: 2, height: 8, borderRadius: 4 }}
            />
            <Typography variant="body2" color="text.secondary" align="center">
              {progress}% Complete
            </Typography>
          </Box>
        )}
        
        {/* Analysis Complete Section */}
        {analysisComplete && (
          <Box sx={{ mt: 3 }}>
            <Alert severity="success" sx={{ mb: 2 }}>
              🎉 Analysis completed successfully! Your report is ready for download.
            </Alert>
            <Button 
              variant="contained" 
              color="success"
              startIcon={<Download />}
              onClick={handleDownload}
              fullWidth
            >
              Download Analysis Report
            </Button>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={uploading && !analysisComplete}>
          {analysisComplete ? 'Close' : 'Cancel'}
        </Button>
        {!analysisComplete && (
          <Button 
            variant="contained" 
            onClick={handleUpload}
            disabled={!file || uploading}
            startIcon={<Upload />}
          >
            {uploading ? 'Analyzing...' : 'Upload & Analyze'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [tabValue, setTabValue] = useState(0);

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [kpisResponse, sessionsResponse] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/kpis`),
        axios.get(`${API_BASE}/sessions/`)
      ]);
      
      setStats(kpisResponse.data.kpis);
      setRecentAnalyses(sessionsResponse.data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleUploadSuccess = (result) => {
    // Handle successful upload
    fetchDashboardData(); // Refresh data
  };

  const handleDownloadReport = async (sessionId) => {
    try {
      const downloadUrl = `${API_BASE}/download-report/${sessionId}`;
      window.open(downloadUrl, '_blank');
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'upload':
        setUploadDialogOpen(true);
        break;
      case 'reports':
        // Navigate to reports
        break;
      case 'analytics':
        // Navigate to analytics
        break;
      default:
        break;
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Welcome back! 👋
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Here's what's happening with your data today.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchDashboardData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Stats Grid */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <StatCard
                title={stat.title}
                value={stat.value}
                change={stat.change}
                trend={stat.trend}
                icon={<Assessment />}
                color={index % 2 === 0 ? 'primary' : 'secondary'}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Quick Actions */}
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <QuickActionCard
            title="Upload Data"
            description="Upload and analyze your data files instantly"
            icon={<CloudUpload sx={{ fontSize: 40 }} />}
            onClick={() => handleQuickAction('upload')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <QuickActionCard
            title="Generate Report"
            description="Create comprehensive analysis reports"
            icon={<Assessment sx={{ fontSize: 40 }} />}
            onClick={() => handleQuickAction('reports')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <QuickActionCard
            title="Advanced Analytics"
            description="Dive deep into your data insights"
            icon={<Analytics sx={{ fontSize: 40 }} />}
            onClick={() => handleQuickAction('analytics')}
          />
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="Recent Analyses" />
              <Tab label="System Status" />
            </Tabs>
          </Box>
          
          {tabValue === 0 && (
            <Box>
              {recentAnalyses.length === 0 ? (
                <Alert severity="info" sx={{ mb: 2 }}>
                  No recent analyses found. Upload some data to get started!
                </Alert>
              ) : (
                recentAnalyses.map((analysis, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {analysis.name || 'Data Analysis'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {analysis.timestamp || 'Recently completed'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip label="Complete" color="success" size="small" />
                      <IconButton 
                        size="small"
                        onClick={() => handleDownloadReport(analysis.session_id)}
                        title="Download Report"
                      >
                        <Download />
                      </IconButton>
                    </Box>
                  </Box>
                ))
              )}
            </Box>
          )}
          
          {tabValue === 1 && (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                🚀 All systems operational
              </Alert>
              <Typography variant="body2" color="text.secondary">
                Backend: Connected • Analytics Engine: Running • Storage: 85% available
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
        }}
        onClick={() => setUploadDialogOpen(true)}
      >
        <Add />
      </Fab>

      {/* Upload Dialog */}
      <UploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onUpload={handleUploadSuccess}
      />
    </Box>
  );
}

