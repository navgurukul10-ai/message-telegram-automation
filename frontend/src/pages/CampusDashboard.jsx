import React from 'react'
import {
  Grid, Typography, Card, CardContent, Box, Button, Chip, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Alert, Snackbar, IconButton, Tooltip
} from '@mui/material'
import { api } from '../api/client'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import WarningIcon from '@mui/icons-material/Warning'
import RefreshIcon from '@mui/icons-material/Refresh'
import AddIcon from '@mui/icons-material/Add'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'

export default function CampusDashboard() {
  const [campuses, setCampuses] = React.useState([])
  const [stats, setStats] = React.useState(null)
  const [followUps, setFollowUps] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [snackbar, setSnackbar] = React.useState({ open: false, message: '', severity: 'success' })
  
  // Dialog states
  const [registerDialogOpen, setRegisterDialogOpen] = React.useState(false)
  const [newCampus, setNewCampus] = React.useState({
    campus_code: '',
    campus_name: '',
    location: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    expected_submission_date: ''
  })

  React.useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      await Promise.all([
        loadCampuses(),
        loadStats(),
        loadFollowUps()
      ])
    } catch (err) {
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadCampuses = async () => {
    try {
      const response = await api.get('/campuses')
      // API client returns data directly
      setCampuses(Array.isArray(response) ? response : [])
    } catch (err) {
      console.error('Failed to load campuses:', err)
    }
  }

  const loadStats = async () => {
    try {
      const response = await api.get('/campuses/dashboard-stats')
      // API client returns data directly
      setStats(response)
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const loadFollowUps = async () => {
    try {
      const response = await api.get('/follow-ups')
      // API client returns data directly
      setFollowUps(Array.isArray(response) ? response : [])
    } catch (err) {
      console.error('Failed to load follow-ups:', err)
    }
  }

  const handleRegisterCampus = async () => {
    try {
      const response = await api.post('/campuses', newCampus)
      
      // API client returns data directly
      if (response.status === 'success') {
        setSnackbar({
          open: true,
          message: 'Campus registered successfully!',
          severity: 'success'
        })
        setRegisterDialogOpen(false)
        setNewCampus({
          campus_code: '',
          campus_name: '',
          location: '',
          contact_person: '',
          contact_email: '',
          contact_phone: '',
          expected_submission_date: ''
        })
        loadData()
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Registration failed',
          severity: 'error'
        })
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Registration failed: ' + (err.response?.data?.error || err.message),
        severity: 'error'
      })
    }
  }

  const handleAutoCreateFollowUps = async () => {
    try {
      const response = await api.post('/follow-ups/auto-create')
      
      // API client returns data directly
      if (response.status === 'success') {
        setSnackbar({
          open: true,
          message: `Created ${response.follow_ups_created} follow-ups for overdue campuses`,
          severity: 'success'
        })
        loadFollowUps()
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to create follow-ups',
        severity: 'error'
      })
    }
  }

  const handleCompleteFollowUp = async (followUpId) => {
    try {
      const response = await api.post(`/follow-ups/${followUpId}/complete`, {})
      
      // API client returns data directly
      if (response.status === 'success') {
        setSnackbar({
          open: true,
          message: 'Follow-up marked as completed',
          severity: 'success'
        })
        loadFollowUps()
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to complete follow-up',
        severity: 'error'
      })
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'submitted':
        return <CheckCircleIcon color="success" />
      case 'overdue':
        return <WarningIcon color="error" />
      case 'pending':
        return <CancelIcon color="warning" />
      default:
        return <CancelIcon color="disabled" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'submitted':
        return 'success'
      case 'overdue':
        return 'error'
      case 'pending':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'error'
      case 'high':
        return 'warning'
      case 'medium':
        return 'info'
      case 'low':
        return 'default'
      default:
        return 'default'
    }
  }

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            <LocationOnIcon /> Campus Dashboard
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setRegisterDialogOpen(true)}
            >
              Register Campus
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadData}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Statistics Cards */}
        {stats && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>Total Campuses</Typography>
                  <Typography variant="h4">{stats.total_campuses || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>Data Submitted</Typography>
                  <Typography variant="h4" color="success.main">
                    {stats.submitted_campuses || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>Pending</Typography>
                  <Typography variant="h4" color="warning.main">
                    {stats.pending_campuses || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>Total Students</Typography>
                  <Typography variant="h4">{stats.total_students || 0}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Campuses Table */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>Campus Status</Typography>
            {loading ? (
              <Typography>Loading campuses...</Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Campus Code</strong></TableCell>
                      <TableCell><strong>Campus Name</strong></TableCell>
                      <TableCell><strong>Location</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                      <TableCell><strong>Students</strong></TableCell>
                      <TableCell><strong>Completeness</strong></TableCell>
                      <TableCell><strong>Last Submission</strong></TableCell>
                      <TableCell><strong>Contact</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {campuses.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          <Typography color="text.secondary" sx={{ py: 4 }}>
                            No campuses registered
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      campuses.map((campus) => (
                        <TableRow key={campus.campus_code} hover>
                          <TableCell>{campus.campus_code}</TableCell>
                          <TableCell>{campus.campus_name}</TableCell>
                          <TableCell>{campus.location || 'N/A'}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getStatusIcon(campus.submission_status)}
                              <Chip
                                label={campus.submission_status || 'pending'}
                                color={getStatusColor(campus.submission_status)}
                                size="small"
                              />
                              {campus.is_overdue && (
                                <Chip
                                  label={`${campus.days_overdue} days overdue`}
                                  color="error"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>{campus.students_submitted || 0}</TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {campus.data_completeness?.toFixed(1) || 0}%
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {campus.last_submission_date || 'Never'}
                          </TableCell>
                          <TableCell>
                            <Box>
                              {campus.contact_email && (
                                <Tooltip title={campus.contact_email}>
                                  <IconButton size="small">
                                    <EmailIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              {campus.contact_phone && (
                                <Tooltip title={campus.contact_phone}>
                                  <IconButton size="small">
                                    <PhoneIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Follow-ups Section */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Follow-ups</Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={handleAutoCreateFollowUps}
              >
                Auto-create for Overdue
              </Button>
            </Box>
            {followUps.length === 0 ? (
              <Typography color="text.secondary" sx={{ py: 2 }}>
                No pending follow-ups
              </Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Campus</strong></TableCell>
                      <TableCell><strong>Type</strong></TableCell>
                      <TableCell><strong>Priority</strong></TableCell>
                      <TableCell><strong>Scheduled Date</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                      <TableCell><strong>Notes</strong></TableCell>
                      <TableCell><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {followUps.map((followUp) => (
                      <TableRow key={followUp.id} hover>
                        <TableCell>{followUp.campus_name}</TableCell>
                        <TableCell>{followUp.follow_up_type}</TableCell>
                        <TableCell>
                          <Chip
                            label={followUp.priority}
                            color={getPriorityColor(followUp.priority)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{followUp.scheduled_date}</TableCell>
                        <TableCell>
                          <Chip
                            label={followUp.status}
                            color={followUp.status === 'completed' ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                            {followUp.notes || '-'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {followUp.status === 'pending' && (
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleCompleteFollowUp(followUp.id)}
                            >
                              Complete
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Register Campus Dialog */}
      <Dialog open={registerDialogOpen} onClose={() => setRegisterDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Register New Campus</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Campus Code *"
                value={newCampus.campus_code}
                onChange={(e) => setNewCampus({ ...newCampus, campus_code: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Campus Name *"
                value={newCampus.campus_name}
                onChange={(e) => setNewCampus({ ...newCampus, campus_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Location"
                value={newCampus.location}
                onChange={(e) => setNewCampus({ ...newCampus, location: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Person"
                value={newCampus.contact_person}
                onChange={(e) => setNewCampus({ ...newCampus, contact_person: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Email"
                type="email"
                value={newCampus.contact_email}
                onChange={(e) => setNewCampus({ ...newCampus, contact_email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Phone"
                value={newCampus.contact_phone}
                onChange={(e) => setNewCampus({ ...newCampus, contact_phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Expected Submission Date"
                type="date"
                value={newCampus.expected_submission_date}
                onChange={(e) => setNewCampus({ ...newCampus, expected_submission_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRegisterDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleRegisterCampus}
            variant="contained"
            disabled={!newCampus.campus_code || !newCampus.campus_name}
          >
            Register
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Grid>
  )
}

