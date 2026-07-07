import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../components/Header";
import ChatMessage from "../components/ChatMessage";
import api from "../services/api";
import { useTheme } from "../context/ThemeContext";
import { useToast } from "../context/ToastContext";

// How many prior turns to send back to the backend as conversational
// memory, so follow-up questions like "what is its lock-in period?"
// can be resolved without the user repeating context.
const HISTORY_TURNS_SENT = 4;

function Dashboard() {
  const navigate = useNavigate();
  const { darkMode, setDarkMode } = useTheme();
  const { showToast } = useToast();

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [selectedPDF, setSelectedPDF] = useState("");
  const [documents, setDocuments] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);

  // ----------------------------
  // Load documents + selected PDF + chat history
  // (auth itself is enforced by ProtectedRoute in App.jsx)
  // ----------------------------
  useEffect(() => {
    const pdf = localStorage.getItem("selected_pdf");

    if (pdf) {
      setSelectedPDF(pdf);
    }

    const fetchHistory = async () => {
      try {
        const response = await api.get("/history");
        setChatHistory(response.data.history.reverse());
      } catch (error) {
        console.error(error);
      }
    };

    fetchHistory();
    refreshDocuments(pdf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ----------------------------
  // Document list (multi-PDF management)
  // ----------------------------
  const refreshDocuments = async (preferPdf) => {
    setDocsLoading(true);

    try {
      const response = await api.get("/documents");

      if (response.data.error) {
        console.error(response.data.error);
        setDocsLoading(false);
        return;
      }

      const docs = response.data.documents || [];
      setDocuments(docs);

      const preferred = preferPdf ?? selectedPDF;
      const stillExists = docs.some((d) => d.filename === preferred);

      if (!stillExists && docs.length > 0) {
        selectDocument(docs[0].filename);
      } else if (docs.length === 0) {
        setSelectedPDF("");
        localStorage.removeItem("selected_pdf");
      }
    } catch (error) {
      console.error(error);
    }

    setDocsLoading(false);
  };

  const selectDocument = (filename) => {
    setSelectedPDF(filename);
    localStorage.setItem("selected_pdf", filename);
  };

  const handleDeleteDocument = async (filename) => {
    try {
      await api.delete(`/documents/${encodeURIComponent(filename)}`);
      showToast(`Deleted ${filename}`, "success");

      const remaining = documents.filter((d) => d.filename !== filename);
      setDocuments(remaining);

      if (selectedPDF === filename) {
        if (remaining.length > 0) {
          selectDocument(remaining[0].filename);
        } else {
          setSelectedPDF("");
          localStorage.removeItem("selected_pdf");
        }
      }
    } catch (error) {
      console.error(error);
      showToast("Failed to delete document", "error");
    }
  };

  // ----------------------------
  // Logout
  // ----------------------------
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("selected_pdf");
    navigate("/login");
  };

  // ----------------------------
  // New Chat
  // ----------------------------
  const handleNewChat = () => {
    setChatHistory([]);
    setQuestion("");
  };

  // ----------------------------
  // Ask Question
  // ----------------------------
  const askQuestion = async () => {
    if (!question.trim()) return;

    if (!selectedPDF) {
      showToast("Please upload a PDF first", "error");
      return;
    }

    setLoading(true);

    const userQuestion = question;
    setQuestion("");

    // Only include turns for the same document, so switching documents
    // doesn't leak unrelated context into the conversational memory.
    const recentTurns = chatHistory
      .filter((chat) => chat.filename === selectedPDF)
      .slice(0, HISTORY_TURNS_SENT)
      .reverse()
      .map((chat) => ({ question: chat.question, answer: chat.answer }));

    try {
      const response = await api.post("/ask", {
        query: userQuestion,
        filename: selectedPDF,
        history: recentTurns,
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const newChat = {
        question: userQuestion,
        answer: response.data.answer,
        filename: selectedPDF,
        sources: response.data.sources || [],
      };

      setChatHistory((prev) => [newChat, ...prev]);
    } catch (error) {
      console.error(error);

      const errorChat = {
        question: userQuestion,
        answer: "Failed to get response from server.",
        filename: selectedPDF,
        sources: [],
      };

      setChatHistory((prev) => [errorChat, ...prev]);
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
      <Header darkMode={darkMode} setDarkMode={setDarkMode} isLoggedIn={true} />

      <div className="flex">
        {/* Sidebar */}
        <div
          className={`w-[320px] min-h-screen border-r p-5 ${
            darkMode ? "bg-slate-900 border-slate-800" : "bg-white border-gray-300"
          }`}
        >
          <button
            onClick={handleNewChat}
            className="w-full bg-blue-600 hover:bg-blue-700 transition p-3 rounded-xl font-semibold"
          >
            + New Chat
          </button>

          <button
            onClick={() => navigate("/upload")}
            className="w-full mt-4 bg-green-600 hover:bg-green-700 transition p-3 rounded-xl font-semibold"
          >
            Upload PDF
          </button>

          <button
            onClick={handleLogout}
            className="w-full mt-4 bg-red-600 hover:bg-red-700 transition p-3 rounded-xl font-semibold"
          >
            Logout
          </button>

          {/* Document switcher (multi-PDF management) */}
          <div
            className={`mt-8 p-4 rounded-xl ${
              darkMode ? "bg-slate-800" : "bg-gray-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <h3 className="font-bold">Your Documents</h3>
              {docsLoading && (
                <span className="text-xs text-slate-400">Loading...</span>
              )}
            </div>

            {documents.length === 0 ? (
              <p className="mt-2 text-sm text-slate-400">
                No PDFs uploaded yet
              </p>
            ) : (
              <div className="mt-3 space-y-2 max-h-[220px] overflow-y-auto">
                {documents.map((doc) => (
                  <div
                    key={doc.filename}
                    onClick={() => selectDocument(doc.filename)}
                    className={`p-2 rounded-lg cursor-pointer flex items-center justify-between gap-2 ${
                      doc.filename === selectedPDF
                        ? "bg-blue-600 text-white"
                        : darkMode
                        ? "bg-slate-900 hover:bg-slate-700"
                        : "bg-white hover:bg-gray-100"
                    }`}
                  >
                    <span className="truncate text-sm" title={doc.filename}>
                      {doc.filename}
                    </span>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteDocument(doc.filename);
                      }}
                      title="Delete document"
                      className="text-xs px-2 py-1 rounded bg-red-500/80 hover:bg-red-600 text-white shrink-0"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Chat History */}
          <h2 className="mt-10 text-xl font-bold">Chat History</h2>

          <div className="mt-5 space-y-3 max-h-[500px] overflow-y-auto">
            {chatHistory.length === 0 ? (
              <p className="text-slate-400">No chats yet</p>
            ) : (
              chatHistory.map((chat, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg transition ${
                    darkMode
                      ? "bg-slate-800 hover:bg-slate-700"
                      : "bg-gray-200 hover:bg-gray-300"
                  }`}
                >
                  <div>
                    <p className="truncate font-medium">{chat.question}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {chat.filename}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-10">
          <h1 className="text-4xl font-bold">Insurance AI Assistant</h1>

          <p className="mt-3 text-slate-400">
            Ask questions from your uploaded insurance documents using
            AI-powered Retrieval-Augmented Generation.
          </p>

          {/* Current PDF */}
          <div
            className={`mt-6 inline-block px-4 py-2 rounded-xl text-sm ${
              darkMode ? "bg-slate-800" : "bg-gray-200"
            }`}
          >
            Active document:{" "}
            <span className="font-semibold">
              {selectedPDF || "No PDF Selected"}
            </span>
          </div>

          {/* Input */}
          <div className="mt-6 flex gap-4">
            <input
              type="text"
              placeholder="Ask your insurance question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  askQuestion();
                }
              }}
              className={`flex-1 p-4 rounded-xl outline-none ${
                darkMode ? "bg-slate-800 text-white" : "bg-white text-black border"
              }`}
            />

            <button
              onClick={askQuestion}
              disabled={loading}
              className={`px-8 rounded-xl font-semibold ${
                loading ? "bg-gray-500 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {/* Chat Area */}
          <div className="mt-10 space-y-6">
            {chatHistory.map((chat, index) => (
              <ChatMessage key={index} chat={chat} darkMode={darkMode} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
