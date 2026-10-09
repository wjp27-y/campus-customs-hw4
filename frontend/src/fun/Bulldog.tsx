import { useEffect, useState } from "react";
import { usePoints } from "./points";

// Handsome Dan, the chat assistant's bulldog avatar. He's happy while the shopper chats or clicks product cards,
// and gets sad, then stressed, the longer they go without doing either.
export type Mood = "happy" | "sad" | "stressed";
const SAD_AFTER_MS = 30_000;
const STRESSED_AFTER_MS = 60_000;

export const MOOD_CAPTION: Record<Mood, string> = {
  happy: "Handsome Dan · happy to help!",
  sad: "Handsome Dan · getting lonely…",
  stressed: "Handsome Dan · so stressed! Say something!",
};

export function useBulldogMood(): Mood {
  const { lastActive } = usePoints();
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    setNow(Date.now());
    const id = setInterval(() => setNow(Date.now()), 2000);
    return () => clearInterval(id);
  }, [lastActive]);
  const idle = now - lastActive;
  return idle >= STRESSED_AFTER_MS ? "stressed" : idle >= SAD_AFTER_MS ? "sad" : "happy";
}

const NAVY = "#00356b";

export default function Bulldog({ mood, size = 48 }: { mood: Mood; size?: number }) {
  return (
    <svg
      className={`bulldog bulldog-${mood}`}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role="img"
      aria-label={`Bulldog looking ${mood}`}
    >
      {/* ears: perked when happy, drooping otherwise */}
      <g className="bulldog-ears" fill="#8a5a3c" stroke={NAVY} strokeWidth="2">
        <path d={mood === "happy" ? "M18 34 Q10 14 30 20 Z" : "M20 36 Q4 34 10 52 Z"} />
        <path d={mood === "happy" ? "M82 34 Q90 14 70 20 Z" : "M80 36 Q96 34 90 52 Z"} />
      </g>
      {/* head and tan eye patch */}
      <ellipse cx="50" cy="54" rx="36" ry="32" fill="#fffaf2" stroke={NAVY} strokeWidth="2.5" />
      <ellipse cx="36" cy="44" rx="12" ry="10" fill="#e6c49a" />
      {/* brows */}
      {mood === "sad" && (
        <g stroke={NAVY} strokeWidth="2.5" strokeLinecap="round">
          <path d="M28 36 L40 32" />
          <path d="M72 36 L60 32" />
        </g>
      )}
      {mood === "stressed" && (
        <g stroke={NAVY} strokeWidth="3" strokeLinecap="round">
          <path d="M27 31 L41 37" />
          <path d="M73 31 L59 37" />
        </g>
      )}
      {/* eyes */}
      {mood === "happy" && (
        <g stroke={NAVY} strokeWidth="3" strokeLinecap="round" fill="none">
          <path d="M30 45 Q36 38 42 45" />
          <path d="M58 45 Q64 38 70 45" />
        </g>
      )}
      {mood === "sad" && (
        <g>
          <ellipse cx="36" cy="45" rx="5" ry="4" fill={NAVY} />
          <ellipse cx="64" cy="45" rx="5" ry="4" fill={NAVY} />
          <path className="bulldog-tear" d="M33 51 Q31 57 33 59 Q35 57 33 51 Z" fill="#6fb3ff" />
        </g>
      )}
      {mood === "stressed" && (
        <g>
          <circle cx="36" cy="45" r="6.5" fill="white" stroke={NAVY} strokeWidth="2" />
          <circle cx="64" cy="45" r="6.5" fill="white" stroke={NAVY} strokeWidth="2" />
          <circle cx="36" cy="45" r="2" fill={NAVY} />
          <circle cx="64" cy="45" r="2" fill={NAVY} />
          <path className="bulldog-sweat" d="M83 28 Q79 36 83 39 Q87 36 83 28 Z" fill="#6fb3ff" />
          <path className="bulldog-sweat bulldog-sweat-2" d="M16 30 Q13 36 16 38 Q19 36 16 30 Z" fill="#6fb3ff" />
        </g>
      )}
      {/* jowls, nose */}
      <ellipse cx="40" cy="66" rx="13" ry="10" fill="#fffaf2" stroke={NAVY} strokeWidth="2" />
      <ellipse cx="60" cy="66" rx="13" ry="10" fill="#fffaf2" stroke={NAVY} strokeWidth="2" />
      <ellipse cx="50" cy="57" rx="8" ry="5.5" fill="#2b2b2b" />
      {/* mouth */}
      {mood === "happy" && (
        <>
          <path d="M40 72 Q50 82 60 72" stroke={NAVY} strokeWidth="2.5" fill="none" strokeLinecap="round" />
          <path className="bulldog-tongue" d="M46 76 Q50 86 54 76 Z" fill="#ff7a8a" />
        </>
      )}
      {mood === "sad" && <path d="M41 79 Q50 71 59 79" stroke={NAVY} strokeWidth="2.5" fill="none" strokeLinecap="round" />}
      {mood === "stressed" && (
        <path d="M38 76 L43 73 L47 77 L51 73 L55 77 L59 73 L62 76" stroke={NAVY} strokeWidth="2.5" fill="none" strokeLinejoin="round" />
      )}
      {/* Yale blue collar with a white Y tag */}
      <path d="M22 82 Q50 96 78 82" stroke={NAVY} strokeWidth="6" fill="none" strokeLinecap="round" />
      <circle cx="50" cy="91" r="6" fill="white" stroke={NAVY} strokeWidth="2" />
      <text x="50" y="94.5" textAnchor="middle" fontSize="9" fontWeight="800" fill={NAVY}>
        Y
      </text>
    </svg>
  );
}
