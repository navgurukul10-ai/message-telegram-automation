import React from 'react'
import { Grid, Typography, TextField, MenuItem, FormControl, Select, InputLabel } from '@mui/material'
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

export default function Messages() {
  const [groupsByDate, setGroupsByDate] = React.useState([])
  const [groupNames, setGroupNames] = React.useState([])
  const [selected, setSelected] = React.useState('')
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
    api.getGroupsByDate()
      .then(res => {
        if (!mounted) return
        setGroupsByDate(res)
        const names = Array.from(new Set(
          res.flatMap(r => (r.groups || '').split(', ').filter(Boolean))
        ))
        setGroupNames(names)
        if (names[0]) setSelected(names[0])
      })
      .catch(e => setError(e.message))
    return () => { mounted = false }
  }, [])

  React.useEffect(() => {
    if (!selected) return
    let mounted = true
    setLoading(true)
    api.getGroupDetails(selected)
      .then(res => { if (mounted) setData(res.messages || []) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [selected])

  // Filter messages by location and skills
  const filteredData = React.useMemo(() => {
    let filtered = data
    
    // Apply location filter
    if (locationFilter) {
      filtered = filtered.filter(m => {
        const text = (m.text || '').toLowerCase()
        const location = (m.location || '').toLowerCase()
        
        if (locationFilter === 'pan_india') {
        return text.includes('india') || text.includes('indian') || 
               text.includes('bangalore') || text.includes('mumbai') || 
               text.includes('delhi') || text.includes('pune') || 
               text.includes('hyderabad') || text.includes('chennai') ||
               location.includes('india') || location.includes('indian') ||
               location.includes('bangalore') || location.includes('mumbai') ||
               location.includes('delhi') || location.includes('pune')
      } else if (locationFilter === 'remote') {
        return text.includes('remote') || text.includes('wfh') || 
               text.includes('work from home') || 
               location.includes('remote') || location.includes('wfh')
      } else if (locationFilter === 'international') {
        return text.includes('usa') || text.includes('uk') || 
               text.includes('singapore') || text.includes('dubai') ||
               text.includes('canada') || text.includes('australia') ||
               location.includes('usa') || location.includes('uk') ||
               location.includes('singapore') || location.includes('dubai')
      }
        return true
      })
    }
    
    // Apply skills filter
    if (skillsFilter) {
      filtered = filtered.filter(m => {
        const text = (m.text || '').toLowerCase()
        const keywords = (m.keywords || '').toLowerCase()
        return text.includes(skillsFilter.toLowerCase()) || keywords.includes(skillsFilter.toLowerCase())
      })
    }
    
    return filtered
  }, [data, locationFilter, skillsFilter])

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6} lg={4}>
        <TextField select fullWidth label="Group" value={selected} onChange={e => setSelected(e.target.value)}>
          {groupNames.map(name => <MenuItem key={name} value={name}>{name}</MenuItem>)}
        </TextField>
      </Grid>
      <Grid item xs={12} md={6} lg={4}>
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
      <Grid item xs={12} md={6} lg={4}>
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
          {filteredData.map((m, i) => {
            const applyLink = extractApplyLink(m.text)
            const applyHref = applyLink || `mailto:?subject=Application&body=${encodeURIComponent(m.text || '')}`
            const skills = m.keywords ? m.keywords.split(',').map(s => s.trim()).filter(Boolean) : []
            
            return (
              <Grid key={i} item xs={12} sm={6} md={4}>
                <JobMessageCard
                  company={m.group_name || 'Group'}
                  title={m.job_type ? `${m.job_type.replace('_', ' ')} Message` : 'Message'}
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
        {(!loading && filteredData.length === 0) ? <Typography>No messages found{locationFilter ? ` for selected location filter` : ''}.</Typography> : null}
      </Grid>
    </Grid>
  )
}


