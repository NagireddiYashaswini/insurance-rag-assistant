function FeatureCard({ title, description, darkMode }) {
  return (
    <div
      className={`p-6 rounded-2xl shadow-lg hover:scale-105 transition-all duration-300 ${
        darkMode ? "bg-slate-800 text-white" : "bg-white text-black border"
      }`}
    >
      <h2 className="text-2xl font-bold mb-4">{title}</h2>
      <p className={darkMode ? "text-slate-300" : "text-slate-600"}>
        {description}
      </p>
    </div>
  );
}

export default FeatureCard;
