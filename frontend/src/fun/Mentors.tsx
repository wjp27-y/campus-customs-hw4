import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { BUY_POINTS, CARD_POINTS, usePoints } from "./points";

// Gon and Naruto greet shoppers in the bottom-left corner: starting college is like the start of a shonen arc.
// They take turns giving encouraging lines that change with the page the shopper is on.
type Speaker = "gon" | "naruto";
type Line = [Speaker, string];
const CYCLE_MS = 7000;

const LINES: Record<string, Line[]> = {
  home: [
    ["gon", "Hi, I'm Gon! Starting at Yale is the first episode of a huge adventure, and every adventurer needs gear!"],
    ["naruto", "And I'm Naruto! Your Yale story starts right here, believe it!"],
    ["gon", "Every arc starts with a first step. Yours can be a cozy Yale hoodie!"],
    ["naruto", "Every hero has a signature outfit. Let's go find yours!"],
  ],
  products: [
    ["naruto", `Whoa, look at all this gear! Click a card to check it out. That's +${CARD_POINTS} points!`],
    ["gon", "Use the search bar to track down exactly what you want, like a real Hunter!"],
    ["naruto", "Rep your residential college. That's your squad for the next four years!"],
    ["gon", "Not sure where to start? Ask Handsome Dan in the chat. He's a very good boy!"],
  ],
  product: [
    ["gon", `Pick your size and grab it! Buying is worth +${BUY_POINTS} points!`],
    ["naruto", "This would look awesome at The Game. Just saying!"],
    ["gon", "Training arc: first year. Uniform: this. Perfect!"],
    ["naruto", "Check the sizes. Some are going fast, so don't hesitate!"],
  ],
  about: [
    ["naruto", "Campus Customs is like the gear shop in your home village. Visit 57 Broadway!"],
    ["gon", "Every corner of Yale has its own gear. Find your people!"],
  ],
  account: [
    ["gon", "Make an account so Handsome Dan remembers your chats!"],
    ["naruto", "Your points are saved to you. Never give up on that next reward!"],
  ],
};

function section(path: string) {
  if (path === "/") return "home";
  if (path === "/products") return "products";
  if (path.startsWith("/products/")) return "product";
  if (path === "/about") return "about";
  return "account";
}

function Gon() {
  return (
    <svg viewBox="0 0 80 110" width="64" height="88" aria-hidden="true">
      {/* spiky black hair with green tips */}
      <path d="M14 46 L8 18 L22 32 L24 4 L34 26 L40 0 L46 26 L56 4 L58 32 L72 18 L66 46 Z" fill="#141414" />
      <path d="M24 4 L27 12 L21 10 Z M40 0 L43 9 L37 9 Z M56 4 L59 10 L53 12 Z" fill="#2f7d32" />
      <ellipse cx="40" cy="52" rx="22" ry="21" fill="#f8d5b5" />
      <ellipse cx="32" cy="50" rx="4" ry="5.5" fill="#3b2a1a" />
      <ellipse cx="48" cy="50" rx="4" ry="5.5" fill="#3b2a1a" />
      <circle cx="33.5" cy="48" r="1.4" fill="white" />
      <circle cx="49.5" cy="48" r="1.4" fill="white" />
      <path d="M32 61 Q40 68 48 61" stroke="#7a3b2a" strokeWidth="2.5" fill="none" strokeLinecap="round" />
      {/* green jacket and shorts */}
      <path d="M18 76 Q40 68 62 76 L64 98 L16 98 Z" fill="#2e8b3e" />
      <path d="M36 74 L40 84 L44 74" fill="#f2f2f2" />
      <rect x="20" y="98" width="17" height="10" rx="3" fill="#2e8b3e" />
      <rect x="43" y="98" width="17" height="10" rx="3" fill="#2e8b3e" />
    </svg>
  );
}

function Naruto() {
  return (
    <svg viewBox="0 0 80 110" width="64" height="88" aria-hidden="true">
      {/* spiky yellow hair */}
      <path d="M12 48 L4 26 L18 30 L14 8 L30 22 L36 2 L44 20 L56 4 L56 24 L74 14 L66 34 L76 44 L66 48 Z" fill="#f7c600" />
      <ellipse cx="40" cy="54" rx="22" ry="20" fill="#f8d5b5" />
      {/* forehead protector */}
      <rect x="16" y="34" width="48" height="9" rx="2" fill="#24457a" />
      <rect x="31" y="35" width="18" height="7" rx="1.5" fill="#c9d3dd" />
      <path d="M36 38.5 Q40 36 44 38.5 Q40 41 36 38.5" stroke="#5a6672" strokeWidth="1" fill="none" />
      {/* blue eyes, whiskers, big grin */}
      <ellipse cx="32" cy="52" rx="3.8" ry="4.5" fill="#1e6fd9" />
      <ellipse cx="48" cy="52" rx="3.8" ry="4.5" fill="#1e6fd9" />
      <circle cx="33" cy="50.5" r="1.2" fill="white" />
      <circle cx="49" cy="50.5" r="1.2" fill="white" />
      <g stroke="#6b4a2f" strokeWidth="1.2" strokeLinecap="round">
        <path d="M20 56 L27 57 M20 60 L27 60 M21 64 L27 62" />
        <path d="M60 56 L53 57 M60 60 L53 60 M59 64 L53 62" />
      </g>
      <path d="M31 63 Q40 72 49 63 Z" fill="#7a2a2a" />
      {/* orange and black jacket */}
      <path d="M18 76 Q40 68 62 76 L64 98 L16 98 Z" fill="#f47b20" />
      <path d="M18 76 Q40 68 62 76 L60 82 Q40 75 20 82 Z" fill="#1c1c1c" />
      <rect x="20" y="98" width="17" height="10" rx="3" fill="#f47b20" />
      <rect x="43" y="98" width="17" height="10" rx="3" fill="#f47b20" />
    </svg>
  );
}

export default function Mentors() {
  const { pathname } = useLocation();
  const { user } = useAuth();
  const { points, goal } = usePoints();
  const [index, setIndex] = useState(0);
  const [hidden, setHidden] = useState(() => sessionStorage.getItem("cc-mentors-hidden") === "1");

  const where = section(pathname);
  const name = user?.first_name || user?.name;
  const lines: Line[] = [
    ...LINES[where],
    // a live points line, so the cheering keeps up with the shopper's score
    ["naruto", `${name ? `${name}, you're` : "You're"} ${goal - points} points from your next reward. You've got this!`],
  ];

  // New page: start that page's lines from the top, then keep cycling.
  useEffect(() => setIndex(0), [where]);
  useEffect(() => {
    const id = setInterval(() => setIndex((i) => i + 1), CYCLE_MS);
    return () => clearInterval(id);
  }, [where]);

  function toggle(hide: boolean) {
    setHidden(hide);
    sessionStorage.setItem("cc-mentors-hidden", hide ? "1" : "0");
  }

  if (hidden) {
    return (
      <button type="button" className="mentors-tab" onClick={() => toggle(false)}>
        Gon &amp; Naruto
      </button>
    );
  }

  const [speaker, text] = lines[index % lines.length];
  return (
    <aside className="mentors" aria-label="Gon and Naruto">
      <div className={`mentor-bubble from-${speaker}`} key={`${where}-${index}`} aria-live="polite">
        <button type="button" className="mentor-close" onClick={() => toggle(true)} aria-label="Hide Gon and Naruto">
          ✕
        </button>
        <strong>{speaker === "gon" ? "Gon" : "Naruto"}</strong>
        <p>{text}</p>
      </div>
      <div className="mentor-figures">
        <div className={`mentor${speaker === "gon" ? " talking" : ""}`}>
          <Gon />
        </div>
        <div className={`mentor${speaker === "naruto" ? " talking" : ""}`}>
          <Naruto />
        </div>
      </div>
    </aside>
  );
}
