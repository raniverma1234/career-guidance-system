// One question with its answer choices shown as buttons
export default function QuestionCard({ number, question, value, onChange }) {
  return (
    <div className={value ? "question answered" : "question"}>
      <div className="question-text">
        <span className="question-number">{number}</span>
        <span>{question.text}</span>
      </div>
      {question.hint && <div className="question-hint">{question.hint}</div>}
      <div className="choices">
        {question.options.map((opt) => (
          <button
            type="button"
            key={opt.value}
            className={value === opt.value ? "choice selected" : "choice"}
            onClick={() => onChange(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
