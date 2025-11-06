import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItemButton,
  ListItemIcon, ListItemText, Box, Divider
} from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import InsightsIcon from '@mui/icons-material/Insights'
import WorkIcon from '@mui/icons-material/Work'
import StarIcon from '@mui/icons-material/Star'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import GroupsIcon from '@mui/icons-material/Groups'
import MenuIcon from '@mui/icons-material/Menu'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import LightModeIcon from '@mui/icons-material/LightMode'
import { ColorModeContext } from '../ColorModeProvider'

const drawerWidth = 260

const nav = [
  { to: '/', icon: <DashboardIcon />, label: 'Dashboard' },
  { to: '/best-jobs', icon: <StarIcon />, label: 'Best Jobs' },
  { to: '/messages', icon: <WorkIcon />, label: 'Messages' },
  { to: '/fresher-analysis', icon: <InsightsIcon />, label: 'Fresher Analysis' },
  { to: '/by-date', icon: <CalendarMonthIcon />, label: 'By Date' },
  { to: '/groups', icon: <GroupsIcon />, label: 'Groups by Date' },
]

export default function Layout({ children }) {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const { mode, toggle } = React.useContext(ColorModeContext)

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ px: 2, py: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 700 }}>Jobs Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">Telegram Collector</Typography>
      </Box>
      <Divider />
      <List sx={{ px: 1, py: 1, flexGrow: 1 }}>
        {nav.map(item => (
          <ListItemButton
            key={item.to}
            component={Link}
            to={item.to}
            selected={location.pathname === item.to}
            sx={{ borderRadius: 2, mb: 0.5 }}
            onClick={() => setMobileOpen(false)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2, color: 'text.secondary' }}>
        <Typography variant="caption">© {new Date().getFullYear()} Telegram Jobs</Typography>
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" color="inherit" sx={{ borderBottom: '1px solid #eef1f5' }}>
        <Toolbar>
          <IconButton edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 2, display: { md: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>Jobs Intelligence</Typography>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton onClick={toggle} aria-label="toggle color mode">
            {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - ${drawerWidth}px)` } }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}


