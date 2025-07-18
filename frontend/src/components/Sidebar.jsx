import React from 'react';
import {
  Drawer,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Dashboard,
  Analytics,
  Storage,
  CloudUpload,
  Assessment,
  Settings,
  Help,
  TrendingUp,
  DataUsage,
  BarChart,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const sidebarWidth = 280;

const menuItems = [
  {
    text: 'Dashboard',
    icon: <Dashboard />,
    path: '/dashboard',
    badge: null,
  },
  {
    text: 'Analytics',
    icon: <Analytics />,
    path: '/analytics',
    badge: 'Pro',
  },
  {
    text: 'Data Sources',
    icon: <Storage />,
    path: '/data-sources',
    badge: null,
  },
  {
    text: 'Upload Data',
    icon: <CloudUpload />,
    path: '/upload',
    badge: null,
  },
  {
    text: 'AI Analysis',
    icon: <Assessment />,
    path: '/analysis',
    badge: 'New',
  },
  {
    text: '🧠 AI Brain Analysis',
    icon: <TrendingUp />,
    path: '/smart-analysis',
    badge: 'Smart',
  },
  {
    text: 'Reports',
    icon: <Assessment />,
    path: '/reports',
    badge: '3',
  },
  {
    text: 'Insights',
    icon: <TrendingUp />,
    path: '/insights',
    badge: 'New',
  },
  {
    text: 'Visualizations',
    icon: <BarChart />,
    path: '/visualizations',
    badge: null,
  },
  {
    text: 'Data Usage',
    icon: <DataUsage />,
    path: '/usage',
    badge: null,
  },
];

const bottomMenuItems = [
  {
    text: 'Settings',
    icon: <Settings />,
    path: '/settings',
  },
  {
    text: 'Help & Support',
    icon: <Help />,
    path: '/help',
  },
];

export default function Sidebar({ open, onToggle }) {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    return location.pathname === path || 
           (path === '/dashboard' && location.pathname === '/');
  };

  const sidebarContent = (
    <Box
      sx={{
        width: sidebarWidth,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.paper',
      }}
    >
      {/* Logo and Brand */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          borderBottom: '1px solid',
          borderBottomColor: 'divider',
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #1a365d 0%, #2d5a85 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '1.2rem',
          }}
        >
          AI
        </Box>
        <Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              fontSize: '1.1rem',
              color: 'text.primary',
              lineHeight: 1.2,
            }}
          >
            Data Analyst
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: 'text.secondary',
              fontSize: '0.75rem',
            }}
          >
            Enterprise Platform
          </Typography>
        </Box>
      </Box>

      {/* Main Navigation */}
      <Box sx={{ flex: 1, pt: 2 }}>
        <Box sx={{ px: 2, mb: 2 }}>
          <Typography
            variant="overline"
            sx={{
              color: 'text.secondary',
              fontSize: '0.7rem',
              fontWeight: 600,
              letterSpacing: '0.1em',
            }}
          >
            Main Menu
          </Typography>
        </Box>
        
        <List sx={{ px: 2 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  px: 2,
                  backgroundColor: isActive(item.path) 
                    ? 'primary.main' 
                    : 'transparent',
                  color: isActive(item.path) 
                    ? 'primary.contrastText' 
                    : 'text.primary',
                  '&:hover': {
                    backgroundColor: isActive(item.path) 
                      ? 'primary.dark' 
                      : 'action.hover',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive(item.path) 
                      ? 'primary.contrastText' 
                      : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isActive(item.path) ? 600 : 500,
                  }}
                />
                {item.badge && (
                  <Chip
                    label={item.badge}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      backgroundColor: isActive(item.path) 
                        ? 'secondary.main' 
                        : 'secondary.light',
                      color: isActive(item.path) 
                        ? 'secondary.contrastText' 
                        : 'secondary.dark',
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Bottom Section */}
      <Box>
        <Divider sx={{ mx: 2, mb: 2 }} />
        <List sx={{ px: 2, pb: 2 }}>
          {bottomMenuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1,
                  px: 2,
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        {/* Status Card */}
        <Box
          sx={{
            mx: 2,
            mb: 2,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
            border: '1px solid #b3e5fc',
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: 'primary.main',
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          >
            🚀 System Status
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              fontSize: '0.75rem',
              mt: 0.5,
            }}
          >
            All systems operational
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: open ? sidebarWidth : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: sidebarWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderRightColor: 'divider',
          transition: theme.transitions.create(['width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      }}
    >
      {sidebarContent}
    </Drawer>
  );
}

