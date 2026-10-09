import { useEffect, useRef } from "react";

// A few spiders wandering around the screen. Purely decorative: they ignore the mouse (pointer-events: none),
// sit under the chat, and are skipped for visitors who ask their OS for reduced motion.
const COUNT = 5;
const SIZE = 30;

interface Crawler {
  x: number;
  y: number;
  angle: number; // radians, direction of travel
  speed: number; // px per frame
  pause: number; // frames left to sit still
}

function SpiderSvg() {
  return (
    <svg width={SIZE} height={SIZE} viewBox="0 0 40 40" aria-hidden="true">
      <g stroke="#1b1b2f" strokeWidth="2" strokeLinecap="round" fill="none">
        <g className="spider-legs-a">
          <path d="M16 16 L6 8 L2 12" />
          <path d="M24 20 L36 18 L39 23" />
          <path d="M16 24 L5 28 L3 35" />
          <path d="M24 28 L33 36 L37 34" />
        </g>
        <g className="spider-legs-b">
          <path d="M24 16 L34 8 L38 12" />
          <path d="M16 20 L4 18 L1 23" />
          <path d="M24 24 L35 28 L37 35" />
          <path d="M16 28 L7 36 L3 34" />
        </g>
      </g>
      <ellipse cx="20" cy="27" rx="7" ry="9" fill="#1b1b2f" />
      <circle cx="20" cy="15" r="5" fill="#1b1b2f" />
      <circle cx="18" cy="13" r="1.2" fill="white" />
      <circle cx="22" cy="13" r="1.2" fill="white" />
    </svg>
  );
}

export default function Spiders() {
  const refs = useRef<(HTMLDivElement | null)[]>([]);
  const reduceMotion = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (reduceMotion) return;
    const crawlers: Crawler[] = Array.from({ length: COUNT }, () => ({
      x: Math.random() * (window.innerWidth - SIZE),
      y: Math.random() * (window.innerHeight - SIZE),
      angle: Math.random() * Math.PI * 2,
      speed: 0.6 + Math.random() * 0.9,
      pause: 0,
    }));
    let frame = 0;
    const step = () => {
      const w = window.innerWidth - SIZE;
      const h = window.innerHeight - SIZE;
      crawlers.forEach((c, i) => {
        const el = refs.current[i];
        if (!el) return;
        if (c.pause > 0) {
          c.pause--;
          el.classList.add("resting");
        } else {
          el.classList.remove("resting");
          c.angle += (Math.random() - 0.5) * 0.25;
          c.x += Math.cos(c.angle) * c.speed;
          c.y += Math.sin(c.angle) * c.speed;
          // turn back toward the middle at the edges
          if (c.x < 0 || c.x > w || c.y < 0 || c.y > h) {
            c.x = Math.min(Math.max(c.x, 0), w);
            c.y = Math.min(Math.max(c.y, 0), h);
            c.angle = Math.atan2(h / 2 - c.y, w / 2 - c.x) + (Math.random() - 0.5);
          }
          if (Math.random() < 0.004) c.pause = 60 + Math.floor(Math.random() * 120);
        }
        // the SVG faces up, so add 90° to face the direction of travel
        el.style.transform = `translate(${c.x}px, ${c.y}px) rotate(${c.angle + Math.PI / 2}rad)`;
      });
      frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [reduceMotion]);

  if (reduceMotion) return null;
  return (
    <div className="spiders" aria-hidden="true">
      {Array.from({ length: COUNT }, (_, i) => (
        <div
          key={i}
          className="spider"
          ref={(el) => {
            refs.current[i] = el;
          }}
        >
          <SpiderSvg />
        </div>
      ))}
    </div>
  );
}
