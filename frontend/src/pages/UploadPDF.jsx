import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import UploadCard from "../components/UploadCard";
import api from "../services/api";
import { useTheme } from "../context/ThemeContext";
import { useToast } from "../context/ToastContext";

function UploadPDF() {
  const navigate = useNavigate();
  const { darkMode, setDarkMode } = useTheme();
  const { showToast } = useToast();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      showToast("Please select a PDF", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const response = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      console.log(response.data);
      localStorage.setItem("selected_pdf", response.data.filename);

      showToast("PDF uploaded successfully", "success");
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      showToast("PDF upload failed", "error");
    }

    setLoading(false);
  };

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-slate-950 text-white" : "bg-gray-100 text-black"
      }`}
    >
      <Header darkMode={darkMode} setDarkMode={setDarkMode} isLoggedIn={true} />

      <div className="flex flex-col justify-center items-center h-[85vh] gap-6">
        <div
          className={`w-[500px] p-10 rounded-2xl shadow-2xl ${
            darkMode ? "bg-slate-900" : "bg-white"
          }`}
        >
          <h1 className="text-4xl font-bold text-center">
            Upload Insurance PDF
          </h1>

          <p className="text-center text-slate-400 mt-3">
            Upload policy documents for AI analysis
          </p>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full mt-10"
          />

          <button
            onClick={handleUpload}
            disabled={loading}
            className={`w-full mt-8 p-4 rounded-xl font-semibold ${
              loading ? "bg-gray-500 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {loading ? "Uploading..." : "Upload PDF"}
          </button>
        </div>

        {/* Preview of the selected file before upload */}
        {file && <UploadCard file={file} darkMode={darkMode} />}
      </div>
    </div>
  );
}

export default UploadPDF;
