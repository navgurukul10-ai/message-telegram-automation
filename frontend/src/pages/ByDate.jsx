import React from 'react'
import { Grid, Typography, TextField, MenuItem, FormControl, Select, InputLabel, Box } from '@mui/material'
import { api } from '../api/client'
import JobMessageCard from '../components/JobMessageCard'

const TYPES = [
  { key: 'all', label: 'All' },
  { key: 'tech', label: 'Tech' },
  { key: 'non_tech', label: 'Non-Tech' },
  { key: 'freelance', label: 'Freelance' },
  { key: 'fresher', label: 'Fresher' },
]

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

export default function ByDate() {
  const [dates, setDates] = React.useState([])
  const [selectedDate, setSelectedDate] = React.useState('')
  const [type, setType] = React.useState('all')
  const [locationFilter, setLocationFilter] = React.useState('')
  const [skillsFilter, setSkillsFilter] = React.useState('')
  const [availableSkills, setAvailableSkills] = React.useState([])
  const [data, setData] = React.useState([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    // Load available skills on mount
    api.getSkills()
      .then(skills => setAvailableSkills(skills))
      .catch(err => console.error('Error loading skills:', err))
  }, [])

  React.useEffect(() => {
    let mounted = true
    api.getAvailableDates()
      .then(res => { if (mounted) { setDates(res); if (res[0]) setSelectedDate(res[0].date) } })
      .catch(e => setError(e.message))
    return () => { mounted = false }
  }, [])

  React.useEffect(() => {
    if (!selectedDate) return
    let mounted = true
    setLoading(true)
    api.getMessagesByDate(selectedDate, type, locationFilter || undefined, skillsFilter || undefined)
      .then(res => { if (mounted) setData(res) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [selectedDate, type, locationFilter, skillsFilter])

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={3}>
        <TextField select fullWidth label="Date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}>
          {dates.map(d => <MenuItem key={d.date} value={d.date}>{d.date} ({d.count})</MenuItem>)}
        </TextField>
      </Grid>
      <Grid item xs={12} md={3}>
        <TextField select fullWidth label="Type" value={type} onChange={e => setType(e.target.value)}>
          {TYPES.map(t => <MenuItem key={t.key} value={t.key}>{t.label}</MenuItem>)}
        </TextField>
      </Grid>
      <Grid item xs={12} md={3}>
        <FormControl fullWidth>
          <InputLabel id="location-filter-label">Location</InputLabel>
          <Select
            labelId="location-filter-label"
            id="location-filter"
            value={locationFilter}
            label="Location"
            onChange={(e) => setLocationFilter(e.target.value)}
          >
            <MenuItem value="">All Locations</MenuItem>
            <MenuItem value="pan_india">Pan India</MenuItem>
            <MenuItem value="remote">Remote</MenuItem>
            <MenuItem value="international">International</MenuItem>
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} md={3}>
        <FormControl fullWidth>
          <InputLabel id="skills-filter-label">Skills</InputLabel>
          <Select
            labelId="skills-filter-label"
            id="skills-filter"
            value={skillsFilter}
            label="Skills"
            onChange={(e) => setSkillsFilter(e.target.value)}
          >
            <MenuItem value="">All Skills</MenuItem>
            {availableSkills.map((skill, idx) => (
              <MenuItem key={idx} value={skill}>
                {skill.charAt(0).toUpperCase() + skill.slice(1)}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>

      <Grid item xs={12}>
        {loading ? <Typography>Loading...</Typography> : null}
        {error ? <Typography color="error">{error}</Typography> : null}
        <Grid container spacing={3}>
          {data.map((m, i) => {
            const applyLink = extractApplyLink(m.text)
            const applyHref = applyLink || `mailto:?subject=Application&body=${encodeURIComponent(m.text || '')}`
            const skills = m.skills ? m.skills.split(',').map(s => s.trim()).filter(Boolean) : []
            
            return (
              <Grid key={i} item xs={12} sm={6} md={4}>
                <JobMessageCard
                  company={m.company || m.group || 'Group'}
                  title={m.job_type ? `${m.job_type.replace('_', ' ')} Job` : 'Job Post'}
                  jobType={m.job_type}
                  date={m.date}
                  location={m.location || ''}
                  skills={skills}
                  description={m.text}
                  applyLink={applyHref}
                  applyText="Apply Now"
                />
              </Grid>
            )
          })}
        </Grid>
      </Grid>
    </Grid>
  )
}


