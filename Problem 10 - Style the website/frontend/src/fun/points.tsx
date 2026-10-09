import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { useAuth } from "../auth";

// Merch points (Problem 10): +10 for interacting with a product card, +50 for buying.
// The first goal is 300 points; each time it's met the shopper earns a reward and the goal moves up by 100.
export const CARD_POINTS = 10;
export const BUY_POINTS = 50;
const FIRST_GOAL = 300;
const GOAL_STEP = 100;
export const REWARD_LABEL = "10% off at Campus Customs vending machines";

export interface Reward {
  goal: number;
  code: string;
  earnedAt: string;
}

interface Saved {
  key: string; // localStorage key the state belongs to (one per shopper, plus "guest")
  points: number;
  goal: number;
  rewards: Reward[];
}

export interface PointsGain {
  id: number;
  amount: number;
  reason: string;
}

interface PointsState {
  points: number;
  goal: number;
  rewards: Reward[];
  lastGain: PointsGain | null; // drives the floating "+10" in the nav
  newReward: Reward | null; // drives the "goal reached" toast
  lastActive: number; // last chat message or product card click (the bulldog's mood depends on it)
  award: (amount: number, reason: string) => void;
  markActive: () => void;
  dismissReward: () => void;
}

const PointsContext = createContext<PointsState | null>(null);

function load(key: string): Saved {
  try {
    const saved = JSON.parse(localStorage.getItem(key) ?? "null");
    if (saved && typeof saved.points === "number") return { ...saved, key };
  } catch {
    // corrupt or blocked storage: start fresh
  }
  return { key, points: 0, goal: FIRST_GOAL, rewards: [] };
}

function rewardCode() {
  return `DAN10-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
}

export function PointsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const key = `cc-points-${user?.id ?? "guest"}`;
  const [saved, setSaved] = useState<Saved>(() => load(key));
  const [lastGain, setLastGain] = useState<PointsGain | null>(null);
  const [newReward, setNewReward] = useState<Reward | null>(null);
  const [lastActive, setLastActive] = useState(() => Date.now());

  useEffect(() => setSaved(load(key)), [key]);
  useEffect(() => localStorage.setItem(saved.key, JSON.stringify(saved)), [saved]);

  // Kept in a ref too, so award() can compute the next state (and spot a new reward) without a state updater.
  const savedRef = useRef(saved);
  savedRef.current = saved;
  useEffect(() => setNewReward(null), [key]);

  const markActive = useCallback(() => setLastActive(Date.now()), []);

  const award = useCallback((amount: number, reason: string) => {
    const s = savedRef.current;
    const points = s.points + amount;
    let goal = s.goal;
    const rewards = [...s.rewards];
    while (points >= goal) {
      rewards.push({ goal, code: rewardCode(), earnedAt: new Date().toISOString() });
      goal += GOAL_STEP;
    }
    const next = { ...s, points, goal, rewards };
    savedRef.current = next;
    setSaved(next);
    setLastActive(Date.now());
    setLastGain({ id: Date.now(), amount, reason });
    if (rewards.length > s.rewards.length) setNewReward(rewards[rewards.length - 1]);
  }, []);

  const dismissReward = useCallback(() => setNewReward(null), []);

  return (
    <PointsContext.Provider
      value={{ ...saved, lastGain, newReward, lastActive, award, markActive, dismissReward }}
    >
      {children}
    </PointsContext.Provider>
  );
}

export function usePoints() {
  const ctx = useContext(PointsContext);
  if (!ctx) throw new Error("usePoints must be used inside PointsProvider");
  return ctx;
}

// The previous goal (or 0), so the progress bar shows progress toward the current goal.
export function previousGoal(goal: number) {
  return goal === FIRST_GOAL ? 0 : goal - GOAL_STEP;
}
