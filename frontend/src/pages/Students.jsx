import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Grid, Typography, TextField, MenuItem, FormControl, Select, InputLabel,
  Button, Box, Card, CardContent, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Chip, IconButton, Tooltip, Alert, Snackbar
} from '@mui/material'
import { api } from '../api/client'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DownloadIcon from '@mui/icons-material/Download'
import RefreshIcon from '@mui/icons-material/Refresh'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import SchoolIcon from '@mui/icons-material/School'

export default function Students() {
  const navigate = useNavigate()
  const [students, setStudents] = React.useState([])
  const [filteredStudents, setFilteredStudents] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [snackbar, setSnackbar] = React.useState({ open: false, message: '', severity: 'success' })
  
  // Filters
  const [campusFilter, setCampusFilter] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('')
  const [categoryFilter, setCategoryFilter] = React.useState('')
  const [searchQuery, setSearchQuery] = React.useState('')
  
  // Campus list for filter
  const [campuses, setCampuses] = React.useState([])
  
  // File upload
  const [uploading, setUploading] = React.useState(false)
  const fileInputRef = React.useRef(null)

  React.useEffect(() => {
    loadStudents()
    loadCampuses()
  }, [])

  React.useEffect(() => {
    applyFilters()
  }, [students, campusFilter, statusFilter, categoryFilter, searchQuery])

  const loadStudents = async () => {
    try {
      setLoading(true)
      const response = await api.get('/students')
      // API client returns data directly, not wrapped in response.data
      setStudents(Array.isArray(response) ? response : [])
      setError('')
    } catch (err) {
      setError('Failed to load students')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadCampuses = async () => {
    try {
      const response = await api.get('/campuses')
      // API client returns data directly, not wrapped in response.data
      setCampuses(Array.isArray(response) ? response : [])
    } catch (err) {
      console.error('Failed to load campuses:', err)
    }
  }

  const applyFilters = () => {
    let filtered = [...students]

    if (campusFilter) {
      filtered = filtered.filter(s => s.campus_name === campusFilter)
    }

    if (statusFilter) {
      filtered = filtered.filter(s => s.status === statusFilter)
    }

    if (categoryFilter) {
      filtered = filtered.filter(s => s.category === categoryFilter)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(s =>
        s.name?.toLowerCase().includes(query) ||
        s.student_id?.toLowerCase().includes(query) ||
        s.email?.toLowerCase().includes(query) ||
        s.campus_name?.toLowerCase().includes(query)
      )
    }

    setFilteredStudents(filtered)
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const campusName = prompt('Enter campus name (optional):') || ''
    
    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)
    if (campusName) {
      formData.append('campus_name', campusName)
    }

    try {
      // For FormData, don't set Content-Type header - browser will set it with boundary
      const response = await api.post('/students/upload', formData)

      // API client returns data directly
      if (response.status === 'success') {
        setSnackbar({
          open: true,
          message: `Successfully processed ${response.records_added} new students and updated ${response.records_updated} existing students`,
          severity: 'success'
        })
        loadStudents()
        loadCampuses()
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Upload failed',
          severity: 'error'
        })
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Upload failed: ' + (err.response?.data?.error || err.message),
        severity: 'error'
      })
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleExport = async (format = 'csv') => {
    try {
      const params = new URLSearchParams()
      if (campusFilter) params.append('campus', campusFilter)
      if (statusFilter) params.append('status', statusFilter)
      if (categoryFilter) params.append('category', categoryFilter)
      params.append('format', format)

      const response = await api.get(`/students/export?${params.toString()}`, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `students_export_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : 'csv'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setSnackbar({
        open: true,
        message: `Exported ${filteredStudents.length} students to ${format.toUpperCase()}`,
        severity: 'success'
      })
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Export failed: ' + (err.response?.data?.error || err.message),
        severity: 'error'
      })
    }
  }

  const handleAnalyzeStudent = async (studentId) => {
    try {
      setSnackbar({ open: true, message: 'Analyzing resume...', severity: 'info' })
      
      const student = students.find(s => s.student_id === studentId)
      if (!student || !student.resume_text) {
        setSnackbar({
          open: true,
          message: 'Resume text not available for this student',
          severity: 'warning'
        })
        return
      }

      const response = await api.post(`/students/${studentId}/analyze`, {
        resume_text: student.resume_text
      })

      // API client returns data directly
      if (response.status === 'success') {
        setSnackbar({
          open: true,
          message: 'Student analyzed and categorized successfully!',
          severity: 'success'
        })
        loadStudents()
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Analysis failed',
          severity: 'error'
        })
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Analysis failed: ' + (err.response?.data?.error || err.message),
        severity: 'error'
      })
    }
  }

  const getCategoryColor = (category) => {
    const colors = {
      'job-ready': 'success',
      'needs-training': 'warning',
      'advanced': 'info',
      'beginner': 'default'
    }
    return colors[category] || 'default'
  }

  const getStatusColor = (status) => {
    const colors = {
      'active': 'success',
      'placed': 'info',
      'inactive': 'default'
    }
    return colors[status] || 'default'
  }

  const uniqueCampuses = [...new Set(students.map(s => s.campus_name).filter(Boolean))].sort()
  const uniqueCategories = [...new Set(students.map(s => s.category).filter(Boolean))].sort()

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            <SchoolIcon /> Student Management
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<UploadFileIcon />}
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Data'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleExport('csv')}
            >
              Export CSV
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => handleExport('excel')}
            >
              Export Excel
            </Button>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadStudents}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls,.json"
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Card>
          <CardContent>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Search"
                  variant="outlined"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by name, ID, email..."
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Campus</InputLabel>
                  <Select
                    value={campusFilter}
                    label="Campus"
                    onChange={(e) => setCampusFilter(e.target.value)}
                  >
                    <MenuItem value="">All Campuses</MenuItem>
                    {uniqueCampuses.map(campus => (
                      <MenuItem key={campus} value={campus}>{campus}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={statusFilter}
                    label="Status"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="placed">Placed</MenuItem>
                    <MenuItem value="inactive">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={categoryFilter}
                    label="Category"
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <MenuItem value="">All Categories</MenuItem>
                    {uniqueCategories.map(cat => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                Showing {filteredStudents.length} of {students.length} students
              </Typography>
            </Box>

            {loading ? (
              <Typography>Loading students...</Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Student ID</strong></TableCell>
                      <TableCell><strong>Name</strong></TableCell>
                      <TableCell><strong>Email</strong></TableCell>
                      <TableCell><strong>Campus</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                      <TableCell><strong>Category</strong></TableCell>
                      <TableCell><strong>Skills</strong></TableCell>
                      <TableCell><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredStudents.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          <Typography color="text.secondary" sx={{ py: 4 }}>
                            No students found
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredStudents.map((student) => (
                        <TableRow 
                          key={student.student_id} 
                          hover
                          onClick={() => navigate(`/students/${student.student_id}`)}
                          sx={{ cursor: 'pointer' }}
                        >
                          <TableCell>{student.student_id || '-'}</TableCell>
                          <TableCell>{student.name || '-'}</TableCell>
                          <TableCell>{student.email || '-'}</TableCell>
                          <TableCell>{student.campus_name || '-'}</TableCell>
                          <TableCell>
                            <Chip
                              label={student.status || 'active'}
                              color={getStatusColor(student.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {student.category ? (
                              <Chip
                                label={student.category}
                                color={getCategoryColor(student.category)}
                                size="small"
                              />
                            ) : (
                              <Typography variant="body2" color="text.secondary">-</Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            {student.skills && Array.isArray(student.skills) && student.skills.length > 0 ? (
                              <Tooltip title={student.skills.join(', ')}>
                                <Typography variant="body2">
                                  {student.skills.slice(0, 3).join(', ')}
                                  {student.skills.length > 3 && '...'}
                                </Typography>
                              </Tooltip>
                            ) : (
                              <Typography variant="body2" color="text.secondary">-</Typography>
                            )}
                          </TableCell>
                          <TableCell onClick={(e) => e.stopPropagation()}>
                            {student.resume_text && (
                              <Tooltip title="Analyze resume with AI">
                                <IconButton
                                  size="small"
                                  onClick={() => handleAnalyzeStudent(student.student_id)}
                                  color="primary"
                                >
                                  <AutoAwesomeIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
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
      </Grid>

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

