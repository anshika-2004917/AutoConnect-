
import { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Loader from "./components/Loader";
import ProtectedRoute from "./components/ProtectedRoute";
import AIChat from "./components/AIChat";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import RouteDetail from "./pages/RouteDetail";
import StudentDashboard from "./pages/StudentDashboard";
import DriverDashboard from "./pages/DriverDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Profile from "./pages/Profile";
import "./App.css";

// Scroll to Available Routes section
function ScrollToRoutes() {
  const location = useLocation();

  useEffect(() => {
    if (
      location.pathname === "/" &&
      location.hash === "#available-routes"
    ) {
      setTimeout(() => {
        document.getElementById("available-routes")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 400);
    }
  }, [location]);

  return null;
}

function App() {
  const { loading } = useAuth();

  if (loading) return <Loader />;

  return (
    <div className="app">
      <Navbar />
      <ScrollToRoutes />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/route/:routeId" element={<RouteDetail />} />

          <Route path="/student" element={<ProtectedRoute role="student"><StudentDashboard /></ProtectedRoute>} />
          <Route path="/driver" element={<ProtectedRoute role="driver"><DriverDashboard /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute role="admin"><AdminDashboard /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />
      <AIChat />
    </div>
  );
}

export default App;
