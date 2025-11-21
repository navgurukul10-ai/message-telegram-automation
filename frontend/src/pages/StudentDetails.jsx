import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Grid, Typography, Card, CardContent, Box, Button, Chip, Divider,
  Paper, Table, TableBody, TableCell, TableContainer, TableRow,
  CircularProgress, Alert, IconButton, Tooltip
} from '@mui/material'
import { api } from '../api/client'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SchoolIcon from '@mui/icons-material/School'
import EmailIcon from '@mui/icons-material/Email'
import PhoneIcon from '@mui/icons-material/Phone'
import LocationOnIcon from '@mui/icons-material/LocationOn'
import WorkIcon from '@mui/icons-material/Work'
import CodeIcon from '@mui/icons-material/Code'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import LaunchIcon from '@mui/icons-material/Launch'

export default function StudentDetails() {
  const { studentId } = useParams()
  const navigate = useNavigate()
  const [student, setStudent] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [analyzing, setAnalyzing] = React.useState(false)

  React.useEffect(() => {
    loadStudent()
  }, [studentId])

  const loadStudent = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.get(`/students/${studentId}`)
      setStudent(response)
    } catch (err) {
      setError('Failed to load student details')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeResume = async () => {
    if (!student) return
    
    try {
      setAnalyzing(true)
      const response = await api.post(`/students/${studentId}/analyze`, {})
      
      if (response.status === 'success') {
        // Reload student data to get updated analysis
        await loadStudent()
      } else {
        setError(response.error || 'Analysis failed')
      }
    } catch (err) {
      setError('Analysis failed: ' + (err.response?.data?.error || err.message))
    } finally {
      setAnalyzing(false)
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

  const renderField = (label, value, icon = null, isUrl = false) => {
    if (!value || value === '-' || (Array.isArray(value) && value.length === 0)) {
      return null
    }
    
    return (
      <TableRow>
        <TableCell sx={{ fontWeight: 600, width: '30%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {icon}
            {label}
          </Box>
        </TableCell>
        <TableCell>
          {isUrl && (value.startsWith('http://') || value.startsWith('https://')) ? (
            <Button
              variant="text"
              size="small"
              startIcon={<LaunchIcon />}
              href={value}
              target="_blank"
              rel="noopener noreferrer"
              sx={{ textTransform: 'none', justifyContent: 'flex-start' }}
            >
              {value}
            </Button>
          ) : Array.isArray(value) ? (
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {value.map((item, idx) => (
                <Chip key={idx} label={item} size="small" variant="outlined" />
              ))}
            </Box>
          ) : typeof value === 'object' && value !== null ? (
            <pre style={{ margin: 0, fontSize: '0.875rem' }}>
              {JSON.stringify(value, null, 2)}
            </pre>
          ) : (
            <Typography variant="body2">{String(value)}</Typography>
          )}
        </TableCell>
      </TableRow>
    )
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error && !student) {
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
          <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/students')} sx={{ mt: 2 }}>
            Back to Students
          </Button>
        </Grid>
      </Grid>
    )
  }

  if (!student) {
    return (
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Alert severity="warning">Student not found</Alert>
          <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/students')} sx={{ mt: 2 }}>
            Back to Students
          </Button>
        </Grid>
      </Grid>
    )
  }

  const additionalInfo = student.additional_info_parsed || {}

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => navigate('/students')} color="primary">
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h4" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
              <SchoolIcon /> Student Details
            </Typography>
          </Box>
          {student.resume_url && (
            <Button
              variant="contained"
              startIcon={<AutoAwesomeIcon />}
              onClick={handleAnalyzeResume}
              disabled={analyzing}
            >
              {analyzing ? 'Analyzing...' : 'Analyze Resume'}
            </Button>
          )}
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Basic Information
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Student ID', student.student_id)}
                      {renderField('Name', student.name, <SchoolIcon fontSize="small" />)}
                      {renderField('Email', student.email, <EmailIcon fontSize="small" />)}
                      {renderField('Phone', student.phone, <PhoneIcon fontSize="small" />)}
                      {renderField('Campus', student.campus_name, <LocationOnIcon fontSize="small" />)}
                      {renderField('Status', student.status, <WorkIcon fontSize="small" />)}
                      {renderField('Category', student.category)}
                      {renderField('Data Source', student.data_source)}
                    </TableBody>
                  </Table>
                </TableContainer>
                {student.status && (
                  <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={student.status}
                      color={getStatusColor(student.status)}
                      size="small"
                    />
                    {student.category && (
                      <Chip
                        label={student.category}
                        color={getCategoryColor(student.category)}
                        size="small"
                      />
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Skills & Experience */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Skills & Experience
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Skills', student.skills, <CodeIcon fontSize="small" />)}
                      {renderField('Experience Level', student.experience_level)}
                      {renderField('Years of Experience', student.years_of_experience)}
                      {renderField('Languages', student.languages)}
                      {renderField('Technical Skills', additionalInfo.technical_skills)}
                      {renderField('Non-Technical Skills', additionalInfo.non_technical_skills)}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Education & Certifications */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Education & Certifications
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Education', student.education)}
                      {renderField('Certifications', student.certifications)}
                      {renderField('Educational Qualification', additionalInfo.educational_qualification)}
                      {renderField('Institute Name', additionalInfo.institute_name)}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Projects & Career */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Projects & Career
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Projects', student.projects)}
                      {renderField('Career Goal', additionalInfo.career_goal)}
                      {renderField('Looking For', additionalInfo.looking_for)}
                      {renderField('Preferred Mode', additionalInfo.preferred_mode)}
                      {renderField('Tech Interests', additionalInfo.tech_interests)}
                      {renderField('Non-Tech Interests', additionalInfo.non_tech_interests)}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Links & Resources */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Links & Resources
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Resume URL', student.resume_url, null, true)}
                      {renderField('Portfolio URL', student.portfolio_url || additionalInfo.portfolio_url, null, true)}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {student.resume_url && (
                    <Button
                      variant="outlined"
                      startIcon={<LaunchIcon />}
                      href={student.resume_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Resume
                    </Button>
                  )}
                  {(student.portfolio_url || additionalInfo.portfolio_url) && (
                    <Button
                      variant="outlined"
                      startIcon={<LaunchIcon />}
                      href={student.portfolio_url || additionalInfo.portfolio_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Portfolio
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* AI Analysis Results */}
          {(student.category || student.category_reasoning || student.category_confidence) && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AutoAwesomeIcon /> AI Analysis Results
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        {renderField('Category', student.category)}
                        {renderField('Confidence', student.category_confidence ? `${(student.category_confidence * 100).toFixed(1)}%` : null)}
                        {renderField('Reasoning', student.category_reasoning)}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Additional Information (Raw) */}
          {Object.keys(additionalInfo).length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Additional Information from Sheet
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        {Object.entries(additionalInfo).map(([key, value]) => {
                          // Skip if already displayed above
                          const displayedKeys = [
                            'technical_skills', 'non_technical_skills', 'tech_interests',
                            'non_tech_interests', 'preferred_mode', 'looking_for',
                            'career_goal', 'educational_qualification', 'institute_name', 'portfolio_url'
                          ]
                          if (displayedKeys.includes(key)) return null
                          
                          return renderField(
                            key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                            value
                          )
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Timestamps */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Metadata
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      {renderField('Created At', student.created_at)}
                      {renderField('Last Updated', student.last_updated)}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  )
}

