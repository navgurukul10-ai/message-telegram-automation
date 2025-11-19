const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function http(path, options = {}) {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Request failed ${res.status}: ${text}`)
  }
  return res.json()
}

export const api = {
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


