import React from 'react'
import { Card, CardContent, Typography, Box } from '@mui/material'

export default function StatCard({ title, value, subtitle, color = 'primary' }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="overline" color={`${color}.main`} sx={{ letterSpacing: 0.6 }}>{title}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 0.5 }}>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>{value}</Typography>
          {subtitle ? <Typography variant="body2" color="text.secondary">{subtitle}</Typography> : null}
        </Box>
      </CardContent>
    </Card>
  )
}


