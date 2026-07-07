import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import { useTheme } from "../context/ThemeContext";

function NotFound() {
  const navigate = useNavigate();
  const { darkMode, setDarkMode } = useTheme();
  const isLoggedIn = !!localStorage.getItem("token");

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-slate-950 text-white" : "bg-gray-100 text-black"
      }`}
    >
      <Header darkMode={darkMode} setDarkMode={setDarkMode} isLoggedIn={isLoggedIn} />

      <div className="flex flex-col items-center justify-center h-[80vh] text-center px-6">
        <h1 className="text-6xl font-bold">404</h1>
        <p className="mt-4 text-xl text-slate-400">
          This page doesn&apos;t exist.
        </p>

        <button
          onClick={() => navigate("/")}
          className="mt-8 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl font-semibold"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default NotFound;
