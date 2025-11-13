import React from 'react'
import { Card, CardContent, Typography, Chip, Stack, Box, Button, Grid } from '@mui/material'
import BusinessIcon from '@mui/icons-material/Business'
import WorkIcon from '@mui/icons-material/Work'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'

export default function JobMessageCard({
  company,
  title,
  jobType,
  score,
  salary,
  experience,
  location,
  date,
  skills,
  description,
  applyLink,
  applyText = 'View Details'
}) {
  // Format job type for display
  const formatJobType = (type) => {
    if (!type) return null
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ')
  }

  // Score color logic
  const getScoreColor = (score) => {
    if (score >= 80) return { bg: '#e8f5e9', text: '#2e7d32' } // Light green
    if (score >= 60) return { bg: '#fff3e0', text: '#ed6c02' } // Light orange
    return { bg: '#f5f5f5', text: '#424242' } // Light grey
  }

  const scoreColors = score !== undefined ? getScoreColor(score) : null
  const displayJobType = formatJobType(jobType)

  return (
    <Card sx={{ 
      borderRadius: 2, 
      boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Company Name & Job Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <BusinessIcon color="action" sx={{ mr: 1, fontSize: '1.2rem' }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
            {company || 'Company Not Specified'}
          </Typography>
        </Box>
        {title && (
          <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1.5 }}>
            {title}
          </Typography>
        )}

        {/* Job Tags/Score */}
        {(displayJobType || score !== undefined) && (
          <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
            {displayJobType && (
              <Chip
                label={displayJobType.toUpperCase() + ' JOB'}
                size="small"
                sx={{ 
                  bgcolor: '#f5f5f5', 
                  color: '#424242', 
                  fontWeight: 600,
                  fontSize: '0.75rem'
                }}
              />
            )}
            {score !== undefined && (
              <Chip
                label={`Score: ${score}%`}
                size="small"
                sx={{ 
                  bgcolor: scoreColors.bg, 
                  color: scoreColors.text, 
                  fontWeight: 600,
                  fontSize: '0.75rem'
                }}
              />
            )}
          </Stack>
        )}

        {/* Details Grid */}
        {(salary || location || experience || date) && (
          <Grid container spacing={1.5} sx={{ mb: 2 }}>
            {salary && (
              <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
                <AttachMoneyIcon color="action" sx={{ mr: 1, fontSize: '1rem' }} />
                <Typography variant="body2" color="text.secondary">{salary}</Typography>
              </Grid>
            )}
            {location && (
              <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
                <LocationOnIcon color="action" sx={{ mr: 1, fontSize: '1rem' }} />
                <Typography variant="body2" color="text.secondary">{location}</Typography>
              </Grid>
            )}
            {experience && (
              <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
                <WorkIcon color="action" sx={{ mr: 1, fontSize: '1rem' }} />
                <Typography variant="body2" color="text.secondary">{experience}</Typography>
              </Grid>
            )}
            {date && (
              <Grid item xs={12} sm={6} sx={{ display: 'flex', alignItems: 'center' }}>
                <CalendarMonthIcon color="action" sx={{ mr: 1, fontSize: '1rem' }} />
                <Typography variant="body2" color="text.secondary">
                  {new Date(date).toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                </Typography>
              </Grid>
            )}
          </Grid>
        )}

        {/* Skills/Keywords */}
        {skills && skills.length > 0 && (
          <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
            {skills.slice(0, 5).map((skill, i) => (
              <Chip 
                key={i} 
                label={skill} 
                size="small" 
                sx={{ 
                  bgcolor: '#e0e0e0', 
                  color: '#424242',
                  fontSize: '0.75rem'
                }} 
              />
            ))}
          </Stack>
        )}

        {/* Job Description Snippet */}
        {description && (
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              mb: 2, 
              whiteSpace: 'pre-wrap',
              flexGrow: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical'
            }}
          >
            {description.length > 200 ? `${description.slice(0, 200)}...` : description}
          </Typography>
        )}

        {/* Action Button */}
        {applyLink && (
          <Button
            variant="contained"
            color="primary"
            href={applyLink}
            target="_blank"
            rel="noopener noreferrer"
            endIcon={<OpenInNewIcon />}
            sx={{ 
              width: '100%',
              mt: 'auto',
              bgcolor: '#1976d2',
              '&:hover': {
                bgcolor: '#1565c0'
              }
            }}
          >
            {applyText}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

