import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import api from "../services/api";
import { useTheme } from "../context/ThemeContext";
import { useToast } from "../context/ToastContext";

function Login() {
  const navigate = useNavigate();
  const { darkMode, setDarkMode } = useTheme();
  const { showToast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      showToast("Please fill all fields", "error");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/login", null, {
        params: {
          email,
          password,
        },
      });

      // Save token
      localStorage.setItem("token", response.data.access_token);

      showToast("Login successful", "success");
      navigate("/dashboard");
    } catch (error) {
      console.error(error);

      if (error.response) {
        showToast(error.response.data.detail || "Invalid credentials", "error");
      } else {
        showToast("Server connection failed", "error");
      }
    }

    setLoading(false);
  };

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-slate-950 text-white" : "bg-gray-100 text-black"
      }`}
    >
      {/* Header */}
      <Header darkMode={darkMode} setDarkMode={setDarkMode} isLoggedIn={false} />

      {/* Login Box */}
      <div className="flex justify-center items-center h-[85vh]">
        <div
          className={`w-[420px] p-10 rounded-2xl shadow-2xl ${
            darkMode ? "bg-slate-900" : "bg-white"
          }`}
        >
          <h1 className="text-4xl font-bold text-center">Login</h1>

          <p className="text-center text-slate-400 mt-3">
            Welcome back to Insurance AI
          </p>

          {/* Email */}
          <input
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            className={`w-full mt-8 p-4 rounded-xl outline-none ${
              darkMode ? "bg-slate-800 text-white" : "bg-gray-100 text-black border"
            }`}
          />

          {/* Password */}
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
            className={`w-full mt-5 p-4 rounded-xl outline-none ${
              darkMode ? "bg-slate-800 text-white" : "bg-gray-100 text-black border"
            }`}
          />

          {/* Login Button */}
          <button
            onClick={handleLogin}
            disabled={loading}
            className={`w-full mt-8 p-4 rounded-xl font-semibold transition ${
              loading ? "bg-gray-500 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {loading ? "Logging in..." : "Login"}
          </button>

          {/* Signup Redirect */}
          <p className="text-center text-slate-400 mt-8">
            Don&apos;t have an account?
          </p>

          <button
            onClick={() => navigate("/signup")}
            className="w-full mt-4 bg-green-600 hover:bg-green-700 transition p-4 rounded-xl font-semibold"
          >
            Signup
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;
