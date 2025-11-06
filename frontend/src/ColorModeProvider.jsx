import React from 'react'
import { ThemeProvider, CssBaseline } from '@mui/material'
import { getTheme } from './theme'

export const ColorModeContext = React.createContext({ mode: 'light', toggle: () => {} })

export default function ColorModeProvider({ children }) {
  const [mode, setMode] = React.useState(() => localStorage.getItem('color-mode') || 'light')
  const theme = React.useMemo(() => getTheme(mode), [mode])

  const toggle = React.useCallback(() => {
    setMode(m => {
      const next = m === 'light' ? 'dark' : 'light'
      localStorage.setItem('color-mode', next)
      return next
    })
  }, [])

  return (
    <ColorModeContext.Provider value={{ mode, toggle }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  )
}


