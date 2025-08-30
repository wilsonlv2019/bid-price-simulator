import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import Home from '@/pages/Home';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import SimpleDashboard from '@/pages/SimpleDashboard';
import Projects from '@/pages/Projects';
import NewProject from '@/pages/NewProject';
import ProjectDetail from '@/pages/ProjectDetail';
import EditProject from '@/pages/EditProject';
import Simulation from '@/pages/Simulation';
import TestPage from '@/pages/TestPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<SimpleDashboard />} />
        <Route path="/dashboard-full" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/new" element={<NewProject />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/projects/:id/edit" element={<EditProject />} />
        <Route path="/projects/:id/simulation" element={<Simulation />} />
        <Route path="/test" element={<TestPage />} />
      </Routes>
      <Toaster position="top-right" richColors />
    </Router>
  );
}

export default App;
