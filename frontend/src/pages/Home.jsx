import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import FeatureCard from "../components/FeatureCard";
import { useTheme } from "../context/ThemeContext";

function Home() {
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

      {/* HERO SECTION */}
      <div className="flex flex-col items-center justify-center text-center px-6 py-24">
        <h1 className="text-6xl font-bold leading-tight">
          AI-Powered Insurance Assistant
        </h1>

        <p className="mt-6 text-xl text-slate-400 max-w-3xl">
          Upload insurance policies, ask questions, and get instant
          AI-powered answers using RAG technology.
        </p>

        <button
          onClick={() => navigate(isLoggedIn ? "/dashboard" : "/login")}
          className="mt-10 bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-xl text-xl"
        >
          Get Started
        </button>
      </div>

      {/* FEATURES */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-12 pb-20">
        <FeatureCard
          darkMode={darkMode}
          title="Smart Insurance AI"
          description="Get accurate answers from your insurance documents."
        />

        <FeatureCard
          darkMode={darkMode}
          title="Upload PDFs"
          description="Upload and process insurance policies instantly."
        />

        <FeatureCard
          darkMode={darkMode}
          title="RAG Technology"
          description="Advanced retrieval augmented generation system."
        />
      </div>
    </div>
  );
}

export default Home;
