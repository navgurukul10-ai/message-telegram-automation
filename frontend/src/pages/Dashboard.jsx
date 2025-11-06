import React from 'react'
import { Grid, Card, CardContent, Typography, Table, TableHead, TableRow, TableCell, TableBody, TableContainer, Pagination, Stack } from '@mui/material'
import { api } from '../api/client'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const [stats, setStats] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [daily, setDaily] = React.useState([])
  const [page, setPage] = React.useState(1)
  const rowsPerPage = 10

  React.useEffect(() => {
    let mounted = true
    async function load() {
      try {
        const [s, d] = await Promise.all([api.getStats(), api.getDailyStats()])
        if (!mounted) return
        setStats(s)
        setDaily(d)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  if (loading) return <Typography>Loading...</Typography>
  if (error) return <Typography color="error">{error}</Typography>
  if (!stats) return null

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={3}><StatCard title="Tech Jobs" value={stats.tech_jobs} color="primary" /></Grid>
      <Grid item xs={12} md={3}><StatCard title="Non-Tech Jobs" value={stats.non_tech_jobs} color="secondary" /></Grid>
      <Grid item xs={12} md={3}><StatCard title="Freelance Jobs" value={stats.freelance_jobs} color="primary" /></Grid>
      <Grid item xs={12} md={3}><StatCard title="Fresher Jobs" value={stats.fresher_jobs} color="secondary" /></Grid>

      <Grid item xs={12} md={3}><StatCard title="Groups Joined" value={stats.total_groups} /></Grid>
      
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>Welcome</Typography>
            <Typography variant="body2" color="text.secondary">
              Use the sidebar to view Best Jobs, Messages by Group, Fresher Jobs Analysis, and Groups by Date.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>Jobs Collected (Date-wise)</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>📅 Date</TableCell>
                    <TableCell>🔧 Tech</TableCell>
                    <TableCell>💼 Non-Tech</TableCell>
                    <TableCell>🏖️ Freelance</TableCell>
                    <TableCell>🎓 Fresher</TableCell>
                    <TableCell>📊 Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {daily.slice((page-1)*rowsPerPage, page*rowsPerPage).map((r, i) => (
                    <TableRow key={i}>
                      <TableCell>{r.date}</TableCell>
                      <TableCell>{r.tech}</TableCell>
                      <TableCell>{r.non_tech}</TableCell>
                      <TableCell>{r.freelance}</TableCell>
                      <TableCell>{r.fresher}</TableCell>
                      <TableCell>{r.total}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Stack direction="row" justifyContent="flex-end" sx={{ mt: 2 }}>
              <Pagination count={Math.max(1, Math.ceil(daily.length / rowsPerPage))} page={page} onChange={(_, p) => setPage(p)} />
            </Stack>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )
}


