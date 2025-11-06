import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import BestJobs from './pages/BestJobs'
import Messages from './pages/Messages'
import FresherAnalysis from './pages/FresherAnalysis'
import Groups from './pages/Groups'
import ByDate from './pages/ByDate'
import GroupDetails from './pages/GroupDetails'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/best-jobs" element={<BestJobs />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/fresher-analysis" element={<FresherAnalysis />} />
        <Route path="/groups" element={<Groups />} />
        <Route path="/groups/:name" element={<GroupDetails />} />
        <Route path="/by-date" element={<ByDate />} />
      </Routes>
    </Layout>
  )
}


