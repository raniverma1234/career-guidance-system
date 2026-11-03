// A single progress bar with a small label on top
export default function ProgressBar({ value, max = 100, label }) {
  const percent = max ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div className="progress">
      <div className="progress-top">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}
