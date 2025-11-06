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
  getBestJobs: () => http('/best_jobs'),
  getMessages: (type) => http(`/messages/${encodeURIComponent(type)}`),
  getAvailableDates: () => http('/available_dates'),
  getMessagesByDate: (date, type) => http(`/messages_by_date/${encodeURIComponent(date)}/${encodeURIComponent(type)}`),
  getFresherAnalysis: () => http('/fresher_analysis'),
}


