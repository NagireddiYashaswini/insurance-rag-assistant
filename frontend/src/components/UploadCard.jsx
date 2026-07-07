function UploadCard({ file, darkMode }) {
  const sizeMB = (file.size / (1024 * 1024)).toFixed(2);

  return (
    <div
      className={`w-[500px] p-6 rounded-2xl shadow-lg transition hover:scale-105 ${
        darkMode ? "bg-slate-900" : "bg-white"
      }`}
    >
      <h3 className="text-xl font-bold truncate">{file.name}</h3>
      <p className="mt-3 text-slate-400">PDF Document</p>
      <p className="mt-2">Size: {sizeMB} MB</p>
    </div>
  );
}

export default UploadCard;
