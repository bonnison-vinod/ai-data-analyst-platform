import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Business,
  Person,
  Analytics,
  TrendingUp,
  Assessment,
  Security,
} from '@mui/icons-material';
import ChatGPTStyleAnalysis from './components/ChatGPTStyleAnalysis';

// Create a sophisticated, classy theme
const classyTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1a365d', // Deep navy blue
      light: '#2d5a85',
      dark: '#0f2a44',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#d69e2e', // Elegant gold
      light: '#f6e05e',
      dark: '#b7791f',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f7fafc', // Very light gray
      paper: '#ffffff',
    },
    text: {
      primary: '#2d3748',
      secondary: '#4a5568',
    },
    divider: '#e2e8f0',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      letterSpacing: '-0.025em',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      letterSpacing: '-0.025em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.125rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
          borderRadius: 12,
          '&:hover': {
            boxShadow: '0 4px 25px rgba(0, 0, 0, 0.12), 0 2px 10px rgba(0, 0, 0, 0.08)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
});

function LoginScreen({ onLogin }) {
  const [tabValue, setTabValue] = useState(0);
  const [accountType, setAccountType] = useState('corporate');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    profession: '',
    company: '',
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);

  const professions = [
    'Data Analyst', 'Data Scientist', 'Business Analyst', 'Marketing Manager',
    'Financial Analyst', 'Operations Manager', 'Product Manager', 'Research Analyst',
    'Consultant', 'Executive', 'Other'
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Simulate authentication
    setTimeout(() => {
      if (formData.username && formData.password) {
        onLogin({ 
          username: formData.username, 
          role: 'admin',
          accountType,
          profession: formData.profession,
          company: formData.company
        });
      } else {
        setError('Please fill in all required fields');
        setLoading(false);
      }
    }, 1000);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        overflow: 'hidden',
      }}
    >
      {/* Left Side - Platform Branding */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          p: 6,
          background: 'linear-gradient(135deg, #1a365d 0%, #2d5a85 100%)',
          color: 'white',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background Pattern */}
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='10' cy='10' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            opacity: 0.1,
          }}
        />
        
        {/* Logo and Branding */}
        <Box sx={{ textAlign: 'center', zIndex: 1 }}>
          <Avatar
            sx={{
              width: 120,
              height: 120,
              mb: 4,
              margin: '0 auto 32px auto',
              background: 'rgba(255, 255, 255, 0.1)',
              fontSize: '3rem',
              fontWeight: 'bold',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            }}
          >
            <Analytics sx={{ fontSize: '4rem' }} />
          </Avatar>
          
          <Typography variant="h2" sx={{ mb: 2, fontWeight: 700 }}>
            AI Data Analyst Platform
          </Typography>
          
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9, fontWeight: 400 }}>
            Enterprise Analytics Solution
          </Typography>
          
          <Box sx={{ maxWidth: 400, mx: 'auto', mb: 6 }}>
            <Typography variant="body1" sx={{ opacity: 0.8, lineHeight: 1.6 }}>
              Transform your data into actionable insights with our advanced AI-powered analytics platform.
              Perfect for both corporate teams and individual professionals.
            </Typography>
          </Box>

          {/* Feature Highlights */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 300, mx: 'auto' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <TrendingUp sx={{ fontSize: 24 }} />
              <Typography variant="body2">Advanced Analytics & Insights</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Assessment sx={{ fontSize: 24 }} />
              <Typography variant="body2">Comprehensive Reporting</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Security sx={{ fontSize: 24 }} />
              <Typography variant="body2">Enterprise-Grade Security</Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Right Side - Login/Signup Form */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4,
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <Card
          sx={{
            width: '100%',
            maxWidth: 480,
            p: 4,
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
          }}
        >
          <CardContent>
            {/* Tab Navigation */}
            <Tabs
              value={tabValue}
              onChange={(e, newValue) => {
                setTabValue(newValue);
                setIsSignUp(newValue === 1);
              }}
              variant="fullWidth"
              sx={{ mb: 4 }}
            >
              <Tab label="Sign In" />
              <Tab label="Sign Up" />
            </Tabs>

            {/* Account Type Selection */}
            <Box sx={{ mb: 4 }}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Account Type
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant={accountType === 'corporate' ? 'contained' : 'outlined'}
                  startIcon={<Business />}
                  onClick={() => setAccountType('corporate')}
                  sx={{ flex: 1 }}
                >
                  Corporate
                </Button>
                <Button
                  variant={accountType === 'personal' ? 'contained' : 'outlined'}
                  startIcon={<Person />}
                  onClick={() => setAccountType('personal')}
                  sx={{ flex: 1 }}
                >
                  Personal
                </Button>
              </Box>
            </Box>

            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                {/* Username/Email */}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label={isSignUp ? "Email Address" : "Username or Email"}
                    type={isSignUp ? "email" : "text"}
                    value={isSignUp ? formData.email : formData.username}
                    onChange={(e) => handleInputChange(isSignUp ? 'email' : 'username', e.target.value)}
                    required
                    variant="outlined"
                  />
                </Grid>

                {/* Username for Sign Up */}
                {isSignUp && (
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Username"
                      value={formData.username}
                      onChange={(e) => handleInputChange('username', e.target.value)}
                      required
                      variant="outlined"
                    />
                  </Grid>
                )}

                {/* Password */}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    required
                    variant="outlined"
                  />
                </Grid>

                {/* Profession - for both types */}
                {isSignUp && (
                  <Grid item xs={12}>
                    <FormControl fullWidth required>
                      <InputLabel>Profession</InputLabel>
                      <Select
                        value={formData.profession}
                        onChange={(e) => handleInputChange('profession', e.target.value)}
                        label="Profession"
                      >
                        {professions.map((prof) => (
                          <MenuItem key={prof} value={prof}>
                            {prof}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                )}

                {/* Corporate Fields */}
                {isSignUp && accountType === 'corporate' && (
                  <>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Company Name"
                        value={formData.company}
                        onChange={(e) => handleInputChange('company', e.target.value)}
                        required
                        variant="outlined"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Department"
                        value={formData.department}
                        onChange={(e) => handleInputChange('department', e.target.value)}
                        variant="outlined"
                      />
                    </Grid>
                  </>
                )}

                {/* Error Message */}
                {error && (
                  <Grid item xs={12}>
                    <Box
                      sx={{
                        p: 2,
                        backgroundColor: '#fed7d7',
                        borderRadius: 1,
                        color: '#e53e3e',
                        fontSize: '0.875rem',
                      }}
                    >
                      {error}
                    </Box>
                  </Grid>
                )}

                {/* Submit Button */}
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{
                      py: 1.5,
                      background: 'linear-gradient(135deg, #1a365d 0%, #2d5a85 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #0f2a44 0%, #1a365d 100%)',
                      },
                    }}
                  >
                    {loading 
                      ? 'Please wait...' 
                      : isSignUp 
                        ? `Create ${accountType} Account` 
                        : 'Sign In'
                    }
                  </Button>
                </Grid>
              </Grid>
            </form>

            {/* Account Type Badge */}
            <Box sx={{ textAlign: 'center', mt: 3 }}>
              <Chip
                icon={accountType === 'corporate' ? <Business /> : <Person />}
                label={`${accountType === 'corporate' ? 'Corporate' : 'Personal'} Account`}
                color="primary"
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Check for existing user session
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  return (
    <ThemeProvider theme={classyTheme}>
      <CssBaseline />
      <Router>
        {!user ? (
          <LoginScreen onLogin={handleLogin} />
        ) : (
          <ChatGPTStyleAnalysis user={user} onLogout={handleLogout} />
        )}
      </Router>
    </ThemeProvider>
  );
}
