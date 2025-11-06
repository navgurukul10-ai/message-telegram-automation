import React from 'react'
import { Grid, Card, CardContent, Typography, Chip, Stack, Tabs, Tab } from '@mui/material'
import { api } from '../api/client'
import JobMessageCard from '../components/JobMessageCard'

// Extract apply link from job text
function extractApplyLink(text) {
  if (!text) return null
  const urlMatch = text.match(/(https?:\/\/\S+|www\.\S+)/i)
  if (urlMatch) {
    let link = urlMatch[1].trim().replace(/[)>.,;:]+$/, '')
    if (link.startsWith('http://') || link.startsWith('https://') || link.startsWith('www.')) {
      if (link.startsWith('www.')) {
        link = 'https://' + link
      }
      return link
    }
  }
  return null
}

const tabs = [
  { key: 'overview', label: '📊 Overview' },
  { key: '0-1', label: '0-1 Years' },
  { key: '0-3', label: '0-3 Years' },
  { key: 'trainee', label: 'Trainee/Intern' },
  { key: 'graduate', label: 'Graduate' },
  { key: 'all', label: 'All Fresher Jobs' }
]

export default function FresherAnalysis() {
  const [data, setData] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [tab, setTab] = React.useState(0)

  React.useEffect(() => {
    let mounted = true
    api.getFresherAnalysis()
      .then(res => { if (mounted) setData(res) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [])

  function matchesFilter(item) {
    if (!data) return false
    const lvl = (item.experience_level || '').toLowerCase()
    const t = tabs[tab].key
    if (t === 'overview') return true
    if (t === 'all') return true
    if (t === '0-1') return lvl.includes('0-1') || lvl.includes('0 to 1') || lvl.includes('general entry')
    if (t === '0-3') return lvl.includes('0-3') || lvl.includes('1-3') || lvl.includes('0 to 3')
    if (t === 'trainee') return lvl.includes('trainee') || lvl.includes('intern')
    if (t === 'graduate') return lvl.includes('graduate')
    return true
  }

  const shown = (data?.fresher_jobs || []).filter(matchesFilter).slice(0, 100)

  if (loading) return <Typography>Loading...</Typography>
  if (error) return <Typography color="error">{error}</Typography>
  if (!data) return null

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 800, mb: 1 }}>🎓 Fresher Jobs Analysis</Typography>
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {Object.entries(data.experience_breakdown || {}).map(([k, v]) => (
                <Chip key={k} label={`${k}: ${v}`} />
              ))}
            </Stack>
            <Typography variant="h4" sx={{ fontWeight: 900 }}>{data.total_fresher_jobs}</Typography>
            <Typography variant="body2" color="text.secondary">Total Fresher Jobs</Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          {tabs.map((t, i) => <Tab key={t.key} label={t.label} />)}
        </Tabs>
      </Grid>

      <Grid item xs={12}>
        <Grid container spacing={3}>
          {shown.map((j, i) => {
            const applyLink = extractApplyLink(j.text)
            const applyHref = applyLink || `mailto:?subject=Application&body=${encodeURIComponent(j.text || '')}`
            const skills = j.keywords_found ? j.keywords_found.split(',').map(s => s.trim()).filter(Boolean) : []
            
            return (
              <Grid key={i} item xs={12} sm={6} md={4}>
                <JobMessageCard
                  company={j.group || 'Company Not Specified'}
                  title="Fresher Job"
                  jobType="fresher"
                  experience={j.experience_level}
                  location={j.group}
                  date={j.date}
                  skills={skills}
                  description={j.text}
                  applyLink={applyHref}
                  applyText="View Details"
                />
              </Grid>
            )
          })}
        </Grid>
        {shown.length === 0 ? (
          <Card>
            <CardContent>
              <Typography sx={{ textAlign: 'center', py: 2 }}>No jobs for this filter.</Typography>
            </CardContent>
          </Card>
        ) : null}
      </Grid>
    </Grid>
  )
}


