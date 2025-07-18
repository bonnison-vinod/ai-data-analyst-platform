import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  Card,
  CardContent,
  Grid,
  LinearProgress
} from '@mui/material';
import {
  Send,
  AttachFile,
  History,
  Download,
  Analytics,
  Close,
  SmartToy,
  Person,
  DeleteOutline,
  Refresh
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';

const ChatContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100vh',
  backgroundColor: '#f8f9fa',
}));

const Sidebar = styled(Box)(({ theme }) => ({
  width: 280,
  backgroundColor: '#202123',
  color: 'white',
  display: 'flex',
  flexDirection: 'column',
}));

const ChatArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
}));

const MessagesContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}));

const MessageBubble = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isUser',
})(({ theme, isUser }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  backgroundColor: isUser ? '#007bff' : '#ffffff',
  color: isUser ? 'white' : 'black',
  borderRadius: '16px',
  maxWidth: '80%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  position: 'relative',
}));

const InputArea = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: 'white',
  borderTop: '1px solid #e0e0e0',
}));

const AnalysisSteps = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  backgroundColor: '#f8f9ff',
  border: '1px solid #e3f2fd',
}));

const ChatGPTStyleAnalysis = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [currentAnalysisSteps, setCurrentAnalysisSteps] = useState([]);
  const [showingResults, setShowingResults] = useState(false);
  const [lastAnalysisResult, setLastAnalysisResult] = useState(null);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      addMessage(`📎 File selected: ${file.name}`, 'user');
    }
  };

  const addMessage = (content, sender, extra = {}) => {
    const message = {
      id: Date.now(),
      content,
      sender,
      timestamp: new Date(),
      ...extra
    };
    setMessages(prev => [...prev, message]);
    return message;
  };

  const simulateAnalysisSteps = (analysisType, query) => {
    const steps = [
      { step: 1, title: "📊 Data Loading", description: "Reading and processing your data file...", completed: false },
      { step: 2, title: "🧠 AI Analysis", description: `Analyzing query: "${query}"...`, completed: false },
      { step: 3, title: "🔍 Pattern Detection", description: `Performing ${analysisType} analysis...`, completed: false },
      { step: 4, title: "📈 Visualization", description: "Creating optimal charts and graphs...", completed: false },
      { step: 5, title: "💡 Insight Generation", description: "Generating actionable insights...", completed: false },
    ];

    setCurrentAnalysisSteps(steps);

    // Simulate step completion
    steps.forEach((step, index) => {
      setTimeout(() => {
        setCurrentAnalysisSteps(prevSteps => 
          prevSteps.map(s => 
            s.step === step.step ? { ...s, completed: true } : s
          )
        );
      }, (index + 1) * 1000);
    });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !selectedFile) {
      if (!selectedFile) {
        addMessage("Please upload a data file first using the 📎 button.", 'assistant');
      }
      return;
    }

    const userMessage = addMessage(inputValue, 'user');
    setInputValue('');
    setIsLoading(true);
    setShowingResults(false);

    try {
      // Add loading message
      const loadingMessage = addMessage("🧠 Analyzing your data...", 'assistant', { isLoading: true });

      // Simulate analysis steps
      simulateAnalysisSteps('Smart Analysis', inputValue);

      const formData = new FormData();
      formData.append('file', selectedFile);
formData.append('query', inputValue);
      formData.append('analysis_type', 'comprehensive');
      formData.append('custom_sheets', '[]');

      const response = await axios.post('http://localhost:8000/api/brain/analyze-smart', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Remove loading message
      setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));

      if (response.data.success) {
        const result = response.data.analysis_result;
        const llmDecision = response.data.llm_decision;
        const sessionId = response.data.session_id;

        // Display analysis result
        const resultMessage = addMessage("", 'assistant', {
          isAnalysisResult: true,
          result: result,
          analysisType: llmDecision.analysis_type,
          tokenUsage: response.data.token_usage,
          query: inputValue,
          sessionId: sessionId
        });

        setLastAnalysisResult({...result, session_id: sessionId});
        setShowingResults(true);

        // Add to history
        const historyItem = {
          id: Date.now(),
          query: inputValue,
          fileName: selectedFile.name,
          timestamp: new Date(),
          result: result,
          analysisType: llmDecision.analysis_type
        };
setAnalysisHistory(prev => [historyItem, ...prev]);

      } else {
        addMessage("❌ Analysis failed. Please try again.", 'assistant');
      }

    } catch (error) {
      console.error('Analysis failed:', error);
      addMessage(`❌ Error: ${error.response?.data?.detail || 'Analysis failed. Please try again.'}`, 'assistant');
    } finally {
      setIsLoading(false);
      setCurrentAnalysisSteps([]);
    }
  };

  const handleHistoryClick = (historyItem) => {
    setMessages([]);
    addMessage(`📎 File: ${historyItem.fileName}`, 'user');
    addMessage(historyItem.query, 'user');
    addMessage("", 'assistant', {
      isAnalysisResult: true,
      result: historyItem.result,
      analysisType: historyItem.analysisType,
      query: historyItem.query
    });
    setLastAnalysisResult(historyItem.result);
    setShowingResults(true);
  };

  const downloadReport = async () => {
    if (!lastAnalysisResult || !lastAnalysisResult.session_id) {
      addMessage('❌ No downloadable report found. Please perform an analysis first.', 'assistant');
      return;
    }

    try {
      // Download Excel report from backend
      const response = await axios.get(`http://localhost:8000/api/brain/download-report/${lastAnalysisResult.session_id}`, {
        responseType: 'blob',
        timeout: 30000, // 30 seconds timeout
        headers: {
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      });

      // Create blob with correct MIME type
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis_report_${lastAnalysisResult.session_id}.xlsx`);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      addMessage('✅ Excel report downloaded successfully!', 'assistant');
      
    } catch (error) {
      console.error('Download failed:', error);
      
      if (error.response?.status === 404) {
        addMessage('❌ Report not found. Please regenerate the analysis.', 'assistant');
      } else if (error.response?.status === 202) {
        addMessage('⏳ Report is still being generated. Please wait and try again.', 'assistant');
      } else {
        addMessage('❌ Error downloading the report. Please try again.', 'assistant');
      }
    }
  };

  const clearHistory = () => {
    setAnalysisHistory([]);
  };

  const newAnalysis = () => {
    setMessages([]);
    setSelectedFile(null);
    setCurrentAnalysisSteps([]);
    setShowingResults(false);
    setLastAnalysisResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const AnalysisResultComponent = ({ result, analysisType, tokenUsage, query }) => (
    <Box>
      <Typography variant="h6" gutterBottom color="primary">
        📊 Analysis Complete: {analysisType?.replace('_', ' ').toUpperCase()}
      </Typography>
      
      {/* Analysis Steps Progress */}
      {currentAnalysisSteps.length > 0 && (
        <AnalysisSteps>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Analysis Steps:
            </Typography>
            {currentAnalysisSteps.map((step) => (
              <Box key={step.step} display="flex" alignItems="center" mb={1}>
                <Box mr={2}>
                  {step.completed ? '✅' : '⏳'}
                </Box>
                <Box flex={1}>
                  <Typography variant="body2" fontWeight="bold">
                    {step.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {step.description}
                  </Typography>
                </Box>
              </Box>
            ))}
          </CardContent>
        </AnalysisSteps>
      )}

      {/* Key Insights */}
      {result.insights && result.insights.length > 0 && (
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            💡 Key Insights:
          </Typography>
          {result.insights.map((insight, idx) => (
            <Alert key={idx} severity="info" sx={{ mb: 1 }}>
              {insight}
            </Alert>
          ))}
        </Box>
      )}

      {/* Visualization */}
      {result.chart_filename && (
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            📈 Visualization:
          </Typography>
          <iframe
            src={`http://localhost:8000/api/brain/chart/${result.chart_filename}`}
            width="100%"
            height="400px"
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              backgroundColor: 'white'
            }}
            title="Analysis Chart"
          />
        </Box>
      )}

      {/* Token Usage */}
      {tokenUsage && (
        <Box mb={2}>
          <Chip 
            label={`Tokens: ${tokenUsage.total_tokens} | Cost: $${tokenUsage.cost.toFixed(4)}`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
      )}

      {/* Download Button */}
      <Button
        variant="contained"
        startIcon={<Download />}
        onClick={downloadReport}
        color="primary"
        size="small"
      >
        Download Report
      </Button>
    </Box>
  );

  return (
    <ChatContainer>
      {/* Sidebar */}
      <Sidebar>
        <Box p={2}>
          <Typography variant="h6" gutterBottom>
            🧠 AI Data Analyst
          </Typography>
          <Button
            variant="contained"
            fullWidth
            startIcon={<Analytics />}
            onClick={newAnalysis}
            sx={{ mb: 2, backgroundColor: '#10a37f' }}
          >
            New Analysis
          </Button>
        </Box>

        <Divider sx={{ backgroundColor: '#4a4a4a' }} />

        {/* History */}
        <Box flex={1} overflow="auto">
          <Box p={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle2">
                <History fontSize="small" sx={{ mr: 1 }} />
                History
              </Typography>
              {analysisHistory.length > 0 && (
                <IconButton size="small" onClick={clearHistory} sx={{ color: 'white' }}>
                  <DeleteOutline fontSize="small" />
                </IconButton>
              )}
            </Box>
            <List dense>
              {analysisHistory.map((item) => (
                <ListItem
                  key={item.id}
                  button
                  onClick={() => handleHistoryClick(item)}
                  sx={{
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': { backgroundColor: '#3a3a3a' }
                  }}
                >
                  <ListItemText
                    primary={item.query.substring(0, 40) + '...'}
                    secondary={item.fileName}
                    primaryTypographyProps={{ fontSize: '0.9rem' }}
                    secondaryTypographyProps={{ fontSize: '0.8rem', color: '#9ca3af' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>

        <Divider sx={{ backgroundColor: '#4a4a4a' }} />

        {/* User Info */}
        <Box p={2}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center">
              <Avatar sx={{ width: 32, height: 32, mr: 1 }}>
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
              <Typography variant="body2">{user?.username}</Typography>
            </Box>
            <IconButton size="small" onClick={onLogout} sx={{ color: 'white' }}>
              <Close fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </Sidebar>

      {/* Main Chat Area */}
      <ChatArea>
        <MessagesContainer>
          {messages.length === 0 ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              height="100%"
              textAlign="center"
            >
              <SmartToy sx={{ fontSize: 80, color: '#10a37f', mb: 2 }} />
              <Typography variant="h4" gutterBottom>
                AI Data Analyst
              </Typography>
              <Typography variant="body1" color="text.secondary" mb={4}>
                Upload your data and ask any question. I'll analyze it and provide insights with visualizations.
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap" justifyContent="center">
                <Chip label="📊 Sales trends over time" variant="outlined" />
                <Chip label="🔍 Correlation analysis" variant="outlined" />
                <Chip label="📈 Performance by category" variant="outlined" />
                <Chip label="🎯 Outlier detection" variant="outlined" />
              </Box>
            </Box>
          ) : (
            messages.map((message) => (
              <Box
                key={message.id}
                display="flex"
                justifyContent={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                mb={2}
              >
                <Box display="flex" alignItems="flex-start" maxWidth="80%">
                  {message.sender === 'assistant' && (
                    <Avatar sx={{ mr: 1, bgcolor: '#10a37f' }}>
                      <SmartToy />
                    </Avatar>
                  )}
                  <MessageBubble isUser={message.sender === 'user'}>
                    {message.isLoading ? (
                      <Box display="flex" alignItems="center">
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        {message.content}
                      </Box>
                    ) : message.isAnalysisResult ? (
                      <AnalysisResultComponent
                        result={message.result}
                        analysisType={message.analysisType}
                        tokenUsage={message.tokenUsage}
                        query={message.query}
                      />
                    ) : (
                      <Typography variant="body1">{message.content}</Typography>
                    )}
                  </MessageBubble>
                  {message.sender === 'user' && (
                    <Avatar sx={{ ml: 1, bgcolor: '#007bff' }}>
                      <Person />
                    </Avatar>
                  )}
                </Box>
              </Box>
            ))
          )}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        {/* Input Area */}
        <InputArea>
          <Box display="flex" alignItems="center" gap={2}>
            <input
              type="file"
              accept=".csv,.xlsx,.json"
              onChange={handleFileSelect}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
            <Tooltip title="Upload data file">
              <IconButton
                onClick={() => fileInputRef.current?.click()}
                color={selectedFile ? 'primary' : 'default'}
              >
                <AttachFile />
              </IconButton>
            </Tooltip>
            
            <TextField
              fullWidth
              variant="outlined"
              placeholder={selectedFile ? "Ask anything about your data..." : "Upload a data file first..."}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              disabled={isLoading || !selectedFile}
              multiline
              maxRows={4}
            />
            
            <Button
              variant="contained"
              endIcon={<Send />}
              onClick={handleSendMessage}
              disabled={isLoading || !selectedFile || !inputValue.trim()}
              sx={{ minWidth: 100 }}
            >
              {isLoading ? <CircularProgress size={20} /> : 'Send'}
            </Button>
          </Box>
          
          {selectedFile && (
            <Box mt={1}>
              <Chip
                label={`📎 ${selectedFile.name}`}
                onDelete={() => setSelectedFile(null)}
                size="small"
                color="primary"
              />
            </Box>
          )}
        </InputArea>
      </ChatArea>
    </ChatContainer>
  );
};

export default ChatGPTStyleAnalysis;
