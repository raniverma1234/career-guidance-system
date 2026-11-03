// A list of horizontal bars, used for skill levels and interest percentages
export default function Bars({ items, max = 100, suffix = "" }) {
  return (
    <div className="bars">
      {items.map((item) => (
        <div className="bar-row" key={item.label}>
          <div className="bar-label">{item.label}</div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${Math.min(100, (item.value / max) * 100)}%` }} />
          </div>
          <div className="bar-value">
            {item.value}
            {suffix}
          </div>
        </div>
      ))}
    </div>
  );
}
