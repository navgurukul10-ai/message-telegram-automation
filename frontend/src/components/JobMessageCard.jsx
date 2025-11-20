import React from 'react'
import { Card, CardContent, Typography, Chip, Stack, Box, Button, Grid, Link } from '@mui/material'
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
  applyText = 'Apply Now'
}) {
  // Convert text to JSX with clickable links
  const renderMessageWithLinks = (text) => {
    if (!text) return null
    
    const urlRegex = /(https?:\/\/[^\s]+|www\.[^\s]+)/gi
    const parts = []
    let lastIndex = 0
    let match
    let hasLinks = false
    
    // Reset regex lastIndex to avoid issues with global regex
    urlRegex.lastIndex = 0
    
    while ((match = urlRegex.exec(text)) !== null) {
      hasLinks = true
      // Add text before the link
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index))
      }
      
      // Add the link
      let url = match[0].trim()
      // Remove special characters from start and end
      url = url.replace(/^[*_~`\[\](){}|\\^<>"']+/, '')
      url = url.replace(/[*_~`\[\](){}|\\^<>"',.;:)>]+$/, '')
      url = url.trim()
      // Add protocol if missing
      if (url.startsWith('www.')) {
        url = 'https://' + url
      }
      
      parts.push(
        <Link
          key={match.index}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          sx={{ color: '#1976d2', textDecoration: 'underline' }}
        >
          {match[0].replace(/^[*_~`\[\](){}|\\^<>"']+/, '').replace(/[*_~`\[\](){}|\\^<>"',.;:)>]+$/, '').trim()}
        </Link>
      )
      
      lastIndex = match.index + match[0].length
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex))
    }
    
    // If no links found, return the text as is
    if (!hasLinks) {
      return text
    }
    
    return parts.length > 0 ? parts : text
  }
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
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', p: 2 }}>
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

        {/* Job Description - Full Message with Scrollable Area */}
        {description && (
          <Box 
            sx={{ 
              mb: 2, 
              flexGrow: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              minHeight: 0,
              maxHeight: '300px',
              '&::-webkit-scrollbar': {
                width: '6px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
                borderRadius: '10px',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#888',
                borderRadius: '10px',
                '&:hover': {
                  background: '#555',
                },
              },
            }}
          >
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {renderMessageWithLinks(description)}
            </Typography>
          </Box>
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

