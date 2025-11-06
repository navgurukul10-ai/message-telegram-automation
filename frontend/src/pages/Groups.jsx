import React from 'react'
import { Card, CardContent, Typography, List, ListItemButton, ListItemText } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Groups() {
  const [data, setData] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const navigate = useNavigate()

  React.useEffect(() => {
    let mounted = true
    api.getGroupsByDate()
      .then(res => { if (mounted) setData(res) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [])

  if (loading) return <Typography>Loading...</Typography>
  if (error) return <Typography color="error">{error}</Typography>

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>Groups by Join Date</Typography>
        <List>
          {data.map((g, i) => (
            <div key={i}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mt: i ? 2 : 0, mb: 1 }}>
                {g.date} • {g.count} groups
              </Typography>
              {(g.groups || '').split(', ').filter(Boolean).map((name, idx) => (
                <ListItemButton key={`${i}-${idx}`} onClick={() => navigate(`/groups/${encodeURIComponent(name)}`)}>
                  <ListItemText primary={name} />
                </ListItemButton>
              ))}
            </div>
          ))}
        </List>
      </CardContent>
    </Card>
  )
}


