import React from 'react'
import { Grid, Typography, Tabs, Tab } from '@mui/material'
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

export default function BestJobs() {
  const [tab, setTab] = React.useState(0)
  const tabs = ['Best Jobs', 'Tech Jobs', 'Non-Tech Jobs', 'Freelance Jobs', 'Fresher Jobs']
  const [data, setData] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    let mounted = true
    setLoading(true)
    const typeMap = {
      0: null,
      1: 'tech',
      2: 'non_tech',
      3: 'freelance',
      4: 'fresher'
    }
    const t = typeMap[tab]
    // Strategy: if 'Best Jobs', use best_jobs endpoint. Else fetch messages by type and apply a light quality filter.
    const fetcher = t ? api.getMessages(t).then(list => list.filter(m => {
      const text = (m.text || '').toLowerCase()
      const hasContact = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|\+?\d{10,13}/.test(text)
      const hasApplyWord = text.includes('apply') || text.includes('send resume') || text.includes('email')
      return (hasContact || hasApplyWord) && (text.split(/\s+/).length > 12)
    }).map(m => ({
      message: m.text,
      company: m.company || 'Company Not Specified',
      skills: m.skills,
      salary: '',
      work_mode: '',
      location: '',
      score: 60, // treated as qualifying
      date: m.date,
      group: m.group,
      apply_link: null,
      job_type: t
    }))) : api.getBestJobs()

    fetcher
      .then(res => { if (mounted) setData(res) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [tab])

  if (loading) return <>
    <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
      {tabs.map((t, i) => <Tab key={i} label={t} />)}
    </Tabs>
    <Typography>Loading...</Typography>
  </>
  if (error) return <Typography color="error">{error}</Typography>

  return (
    <>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        {tabs.map((t, i) => <Tab key={i} label={t} />)}
      </Tabs>
      <Grid container spacing={3}>
        {data.map((job, i) => {
          const skills = (job.skills || '').split(',').map(s => s.trim()).filter(Boolean)
          const applyLink = job.apply_link || (job.message ? extractApplyLink(job.message) : null)
          const applyHref = applyLink || (job.company ? `mailto:?subject=Application - ${encodeURIComponent(job.company)}&body=${encodeURIComponent(job.message || '')}` : null)
          
          return (
            <Grid key={i} item xs={12} sm={6} md={4}>
              <JobMessageCard
                company={job.company || job.group || 'Company Not Specified'}
                title={job.job_type ? `${job.job_type.replace('_', ' ')} Job` : 'Job Position'}
                jobType={job.job_type}
                score={job.score}
                salary={job.salary}
                experience={job.experience_required || job.experience}
                location={job.location || job.work_mode || job.group}
                date={job.date}
                skills={skills}
                description={job.message || job.message_text}
                applyLink={applyHref}
                applyText="View Details"
              />
            </Grid>
          )
        })}
        {data.length === 0 ? (
          <Grid item xs={12}>
            <Typography>No high-quality jobs found.</Typography>
          </Grid>
        ) : null}
      </Grid>
    </>
  )
}


