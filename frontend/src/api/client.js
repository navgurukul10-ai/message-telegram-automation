const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function http(path, options = {}) {
  const url = `${API_BASE}${path}`
  
  // Prepare headers
  const headers = { ...options.headers }
  
  // Stringify body if it's an object and not FormData or Blob
  let body = options.body
  const isFormData = body instanceof FormData
  const isBlob = body instanceof Blob
  
  // Only add Content-Type for JSON if body is provided and not FormData/Blob
  // For FormData, browser will set Content-Type with boundary automatically
  if (body && !isFormData && !isBlob) {
    if (typeof body === 'object') {
      body = JSON.stringify(body)
      if (!headers['Content-Type'] && !headers['content-type']) {
        headers['Content-Type'] = 'application/json'
      }
    }
  }
  
  // Remove Content-Type header for FormData - browser will set it with boundary
  if (isFormData && headers['Content-Type']) {
    delete headers['Content-Type']
  }
  
  const res = await fetch(url, { 
    ...options,
    headers,
    body
  })
  
  if (!res.ok) {
    let errorData
    try {
      errorData = await res.json()
    } catch {
      const text = await res.text().catch(() => '')
      const error = new Error(`Request failed ${res.status}: ${text}`)
      error.response = { data: { error: text }, status: res.status }
      throw error
    }
    const error = new Error(errorData.error || 'Request failed')
    error.response = { data: errorData, status: res.status }
    throw error
  }
  
  // Handle blob responses (for file downloads)
  if (options.responseType === 'blob') {
    return res.blob()
  }
  
  return res.json()
}

export const api = {
  // Generic HTTP methods
  get: (path, options = {}) => http(path, { ...options, method: 'GET' }),
  post: (path, data, options = {}) => http(path, { ...options, method: 'POST', body: data }),
  put: (path, data, options = {}) => http(path, { ...options, method: 'PUT', body: data }),
  delete: (path, options = {}) => http(path, { ...options, method: 'DELETE' }),
  
  // Specific API methods (for backward compatibility)
  getStats: () => http('/stats'),
  getDailyStats: () => http('/daily_stats'),
  getGroupsByDate: () => http('/groups_by_date'),
  getGroupDetails: (groupName) => http(`/group_details/${encodeURIComponent(groupName)}`),
  getBestJobs: (location, skills) => {
    const params = new URLSearchParams()
    if (location) params.append('location', location)
    if (skills) params.append('skills', skills)
    const queryString = params.toString() ? `?${params.toString()}` : ''
    return http(`/best_jobs${queryString}`)
  },
  getMessages: (type, location, skills) => {
    const params = new URLSearchParams()
    if (location) params.append('location', location)
    if (skills) params.append('skills', skills)
    const queryString = params.toString() ? `?${params.toString()}` : ''
    return http(`/messages/${encodeURIComponent(type)}${queryString}`)
  },
  getAvailableDates: () => http('/available_dates'),
  getMessagesByDate: (date, type, location, skills) => {
    const params = new URLSearchParams()
    if (location) params.append('location', location)
    if (skills) params.append('skills', skills)
    const queryString = params.toString() ? `?${params.toString()}` : ''
    return http(`/messages_by_date/${encodeURIComponent(date)}/${encodeURIComponent(type)}${queryString}`)
  },
  getSkills: () => http('/skills'),
  getFresherAnalysis: () => http('/fresher_analysis'),
  getMessagesByLocation: (locationFilter) => http(`/messages_by_location/${encodeURIComponent(locationFilter)}`),
}


