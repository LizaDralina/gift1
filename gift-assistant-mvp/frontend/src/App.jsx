import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import RecipientForm from "./pages/RecipientForm";
import Recommendations from "./pages/Recommendations";
import { getToken } from "./api/client";
import VkCallback from "./pages/VkCallback";

function ProtectedRoute() {
  return getToken() ? <Outlet /> : <Navigate to="/login" replace />;
}

function HomeRedirect() {
  return getToken() ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<HomeRedirect />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/recipients/new" element={<RecipientForm />} />
            <Route path="/recipients/:id/edit" element={<RecipientForm />} />
            <Route path="/recommendations/:recipientId" element={<Recommendations />} />
            <Route path="/vk/callback" element={<VkCallback />} />
          </Route>
        </Routes>
      </div>
    </>
  );
}