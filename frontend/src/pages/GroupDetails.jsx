import React from 'react'
import { useParams } from 'react-router-dom'
import { Typography, Grid } from '@mui/material'
import { api } from '../api/client'
import JobMessageCard from '../components/JobMessageCard'

// Clean URL by removing special characters from start and end
function cleanUrl(url) {
  if (!url) return url
  
  // Remove special characters from start (common markdown/formatting chars)
  url = url.replace(/^[*_~`\[\](){}|\\^<>"']+/, '')
  
  // Remove special characters from end (punctuation and formatting)
  url = url.replace(/[*_~`\[\](){}|\\^<>"',.;:)>]+$/, '')
  
  return url.trim()
}

// Extract apply link from message text
function extractApplyLink(text) {
  if (!text) return null
  const urlMatch = text.match(/(https?:\/\/\S+|www\.\S+)/i)
  if (urlMatch) {
    let link = cleanUrl(urlMatch[1].trim())
    if (link.startsWith('http://') || link.startsWith('https://') || link.startsWith('www.')) {
      if (link.startsWith('www.')) {
        link = 'https://' + link
      }
      return link
    }
  }
  return null
}

export default function GroupDetails() {
  const { name } = useParams()
  const decoded = decodeURIComponent(name)
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    let mounted = true
    api.getGroupDetails(decoded)
      .then(res => { if (mounted) setData(res) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [decoded])

  if (loading) return <Typography>Loading...</Typography>
  if (error) return <Typography color="error">{error}</Typography>
  if (!data) return null

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Typography variant="h6" sx={{ fontWeight: 800 }}>{decoded}</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          First: {data.firstMessage} • Last: {data.lastMessage} • Total: {data.totalCount}
        </Typography>
      </Grid>
      {data.messages.map((m, i) => {
        const applyLink = extractApplyLink(m.text)
        const applyHref = applyLink || `mailto:?subject=Application&body=${encodeURIComponent(m.text || '')}`
        const skills = m.keywords ? m.keywords.split(',').map(s => s.trim()).filter(Boolean) : []
        
        return (
          <Grid key={i} item xs={12} sm={6} md={4}>
            <JobMessageCard
              company={decoded}
              title={m.job_type ? `${m.job_type.replace('_', ' ')} Message` : 'Message'}
              jobType={m.job_type}
              date={m.date}
              skills={skills}
              description={m.text}
              applyLink={applyHref}
              applyText="Apply Now"
            />
          </Grid>
        )
      })}
    </Grid>
  )
}


