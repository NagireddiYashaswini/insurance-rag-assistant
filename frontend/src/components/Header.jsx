import { FaMoon, FaSun } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

function Header({ darkMode, setDarkMode, isLoggedIn }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("selected_pdf");
    navigate("/login");
  };

  return (
    <div
      className={`w-full px-8 py-4 flex justify-between items-center border-b ${
        darkMode
          ? "bg-slate-900 border-slate-800 text-white"
          : "bg-white border-gray-300 text-black"
      }`}
    >
      {/* LEFT */}
      <div
        className="flex items-center gap-3 cursor-pointer"
        onClick={() => navigate("/")}
      >
        <div className="text-3xl">🛡️</div>
        <h1 className="text-2xl font-bold">Insurance AI</h1>
      </div>

      {/* RIGHT */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setDarkMode(!darkMode)}
          aria-label="Toggle dark mode"
          title="Toggle dark mode"
          className={`p-3 rounded-lg ${
            darkMode
              ? "bg-slate-800 hover:bg-slate-700"
              : "bg-gray-200 hover:bg-gray-300"
          }`}
        >
          {darkMode ? <FaSun /> : <FaMoon />}
        </button>

        {!isLoggedIn ? (
          <>
            <button
              onClick={() => navigate("/login")}
              className="bg-blue-600 hover:bg-blue-700 px-5 py-2 rounded-lg text-white"
            >
              Login
            </button>

            <button
              onClick={() => navigate("/signup")}
              className="bg-green-600 hover:bg-green-700 px-5 py-2 rounded-lg text-white"
            >
              Signup
            </button>
          </>
        ) : (
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 px-5 py-2 rounded-lg text-white"
          >
            Logout
          </button>
        )}
      </div>
    </div>
  );
}

export default Header;
