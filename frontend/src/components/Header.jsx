import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications,
  Settings,
  Logout,
  Person,
} from '@mui/icons-material';
import { useState } from 'react';

export default function Header({ user, onLogout, onToggleSidebar, sidebarOpen }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);

  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    onLogout();
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: 'background.paper',
        borderBottom: '1px solid',
        borderBottomColor: 'divider',
        color: 'text.primary',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            edge="start"
            color="inherit"
            onClick={onToggleSidebar}
            sx={{
              mr: 1,
              color: 'text.secondary',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography
            variant="h6"
            component="h1"
            sx={{
              fontWeight: 600,
              color: 'primary.main',
              display: { xs: 'none', sm: 'block' },
            }}
          >
            AI Data Analyst Platform
          </Typography>
          
          <Chip
            label="v2.0"
            size="small"
            color="secondary"
            sx={{
              ml: 1,
              fontSize: '0.75rem',
              height: 24,
              display: { xs: 'none', md: 'flex' },
            }}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <IconButton
            color="inherit"
            onClick={handleNotificationOpen}
            sx={{
              color: 'text.secondary',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <Notifications />
          </IconButton>

          <Menu
            anchorEl={notificationAnchor}
            open={Boolean(notificationAnchor)}
            onClose={handleNotificationClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 280,
                maxWidth: 320,
              },
            }}
          >
            <Box sx={{ p: 2, pb: 1 }}>
              <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                Notifications
              </Typography>
            </Box>
            <Divider />
            <MenuItem onClick={handleNotificationClose} sx={{ py: 1.5 }}>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  Analysis Complete
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Your data analysis report is ready
                </Typography>
              </Box>
            </MenuItem>
            <MenuItem onClick={handleNotificationClose} sx={{ py: 1.5 }}>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  New Data Source
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Database connection established
                </Typography>
              </Box>
            </MenuItem>
          </Menu>

          {/* User Profile */}
          <IconButton
            onClick={handleUserMenuOpen}
            sx={{
              ml: 1,
              p: 0.5,
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                backgroundColor: 'primary.main',
                fontSize: '1rem',
                fontWeight: 600,
              }}
            >
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleUserMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
              },
            }}
          >
            <Box sx={{ p: 2, pb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {user?.username || 'User'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.role || 'Administrator'}
              </Typography>
            </Box>
            <Divider />
            <MenuItem onClick={handleUserMenuClose} sx={{ py: 1 }}>
              <Person sx={{ mr: 2, fontSize: 20 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={handleUserMenuClose} sx={{ py: 1 }}>
              <Settings sx={{ mr: 2, fontSize: 20 }} />
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout} sx={{ py: 1, color: 'error.main' }}>
              <Logout sx={{ mr: 2, fontSize: 20 }} />
              Sign Out
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

