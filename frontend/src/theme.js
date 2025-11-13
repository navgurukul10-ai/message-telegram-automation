import { createTheme } from '@mui/material/styles'

export function getTheme(mode = 'light') {
  return createTheme({
    palette: {
      mode,
      primary: { main: '#1976d2' },
      secondary: { main: '#9c27b0' },
      background: mode === 'light' ? { default: '#f7f9fc', paper: '#ffffff' } : { default: '#0f1115', paper: '#111418' }
    },
    shape: { borderRadius: 12 },
    typography: {
      fontFamily: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(',')
    },
    components: {
      MuiCard: { styleOverrides: { root: { boxShadow: mode === 'light' ? '0 2px 12px rgba(0,0,0,0.06)' : '0 2px 12px rgba(0,0,0,0.4)' } } },
      MuiAppBar: { styleOverrides: { root: { boxShadow: 'none' } } }
    }
  })
}



