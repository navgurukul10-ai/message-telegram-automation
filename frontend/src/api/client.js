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
  getBestJobs: (location) => {
    const url = location ? `/best_jobs?location=${encodeURIComponent(location)}` : '/best_jobs'
    return http(url)
  },
  getMessages: (type, location) => {
    const url = location ? `/messages/${encodeURIComponent(type)}?location=${encodeURIComponent(location)}` : `/messages/${encodeURIComponent(type)}`
    return http(url)
  },
  getAvailableDates: () => http('/available_dates'),
  getMessagesByDate: (date, type, location) => {
    const url = location ? `/messages_by_date/${encodeURIComponent(date)}/${encodeURIComponent(type)}?location=${encodeURIComponent(location)}` : `/messages_by_date/${encodeURIComponent(date)}/${encodeURIComponent(type)}`
    return http(url)
  },
  getFresherAnalysis: () => http('/fresher_analysis'),
  getMessagesByLocation: (locationFilter) => http(`/messages_by_location/${encodeURIComponent(locationFilter)}`),
}


