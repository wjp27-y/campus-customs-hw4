import { useEffect, useState } from "react";
import { REWARD_LABEL, previousGoal, usePoints } from "./points";

// Points pill in the nav bar: score, progress to the current goal, a floating "+10" on every gain,
// and a dropdown listing the rewards earned so far.
export default function PointsTracker() {
  const { points, goal, rewards, lastGain } = usePoints();
  const [open, setOpen] = useState(false);
  const [floating, setFloating] = useState<typeof lastGain>(null);

  useEffect(() => {
    if (!lastGain) return;
    setFloating(lastGain);
    const id = setTimeout(() => setFloating(null), 1200);
    return () => clearTimeout(id);
  }, [lastGain?.id]);

  const from = previousGoal(goal);
  const pct = Math.min(100, Math.round(((points - from) / (goal - from)) * 100));

  return (
    <div className="points">
      <button
        type="button"
        className="points-pill"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        title={`+10 for product cards, +50 for buying. Next reward at ${goal} points`}
      >
        <span className="points-score">★ {points} pts</span>
        <span className="points-bar" aria-hidden="true">
          <span style={{ width: `${pct}%` }} />
        </span>
        <span className="points-goal">Goal {goal}</span>
      </button>
      {floating && (
        <span className="points-float" key={floating.id}>
          +{floating.amount}
        </span>
      )}
      {open && (
        <div className="points-menu">
          <strong>Merch points</strong>
          <p>
            +10 for checking out a product card, +50 for buying. Reach <b>{goal}</b> to earn {REWARD_LABEL}. Each
            time you hit a goal, the next one moves up by 100.
          </p>
          {rewards.length === 0 ? (
            <p className="status">No rewards yet: {goal - points} points to go!</p>
          ) : (
            <ul>
              {rewards.map((r) => (
                <li key={r.code}>
                  <span>{r.goal} pts</span> <code>{r.code}</code>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// "Goal reached" toast with the reward code. Dismissed by the shopper, or on its own after a while.
export function RewardToast() {
  const { newReward, goal, dismissReward } = usePoints();
  useEffect(() => {
    if (!newReward) return;
    const id = setTimeout(dismissReward, 10_000);
    return () => clearTimeout(id);
  }, [newReward?.code]);

  if (!newReward) return null;
  return (
    <div className="reward-toast" role="status">
      <div className="reward-burst" aria-hidden="true">🎉</div>
      <div>
        <strong>Goal reached: {newReward.goal} points!</strong>
        <p>
          You earned <b>{REWARD_LABEL}</b>. Code: <code>{newReward.code}</code>
        </p>
        <small>Next goal: {goal} points</small>
      </div>
      <button type="button" onClick={dismissReward} aria-label="Dismiss">
        ✕
      </button>
    </div>
  );
}
