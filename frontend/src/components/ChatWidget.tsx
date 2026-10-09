import { Fragment, useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { clearChatHistory, formatPrice, getChatHistory, sendChat } from "../api";
import { useAuth } from "../auth";
import { useChatResults } from "../chatResults";
import Bulldog, { MOOD_CAPTION, useBulldogMood } from "../fun/Bulldog";
import { CARD_POINTS, usePoints } from "../fun/points";
import type { ChatMessage, ProductCard, SimilarProducts } from "../types";

const GREETING: ChatMessage = {
  role: "assistant",
  content: "Hi! I'm Handsome Dan, the Campus Customs assistant. Ask me about our Yale apparel, sizes, or prices.",
};
// What Handsome Dan says over his hello animation, by mood.
const INTRO_WOOF = {
  happy: "Woof! Let's find your gear!",
  sad: "*whimper* …ask me something?",
  stressed: "Arf?! Please say something!",
};
const MAX_MESSAGE = 1000; // matches backend MAX_MESSAGE_CHARS
const CARDS_IN_CHAT = 3; // the rest are shown on the page

// Render **bold** from the agent's light markdown; everything else stays plain text (no HTML injection).
function RichText({ text }: { text: string }) {
  return (
    <>
      {text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
        part.startsWith("**") && part.endsWith("**") ? (
          <strong key={i}>{part.slice(2, -2)}</strong>
        ) : (
          <Fragment key={i}>{part}</Fragment>
        ),
      )}
    </>
  );
}

function ChatProductCard({ product }: { product: ProductCard }) {
  const { award } = usePoints();
  return (
    <Link
      to={`/products/${product.product_id}`}
      className="chat-card"
      onClick={() => award(CARD_POINTS, `Checked out ${product.name}`)}
    >
      <img src={product.image_url} alt={product.name} />
      <div>
        <strong>{product.name}</strong>
        <span className="chat-card-price">{formatPrice(product.price)}</span>
        <small className={product.in_stock ? "ok" : "bad"}>
          {product.in_stock ? `In stock: ${product.sizes_in_stock.join(", ")}` : "Sold out"}
        </small>
      </div>
    </Link>
  );
}

export default function ChatWidget() {
  const { user } = useAuth();
  const { results, showResults, clearResults } = useChatResults();
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const { markActive } = usePoints();
  const mood = useBulldogMood();
  const freshChat = messages.length === 1; // only the greeting: Handsome Dan's hello animation plays

  // New conversation whenever the shopper logs in or out; logged-in shoppers get their saved chat back.
  useEffect(() => {
    setMessages([GREETING]);
    if (!user) return;
    getChatHistory()
      .then((saved) => saved.length && setMessages([GREETING, ...saved]))
      .catch(() => {});
  }, [user?.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open, sending]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    // Page context goes with every message. Conversation memory is server-side, and only for logged-in shoppers.
    const viewing = location.pathname.match(/^\/products\/([^/]+)$/);
    const pageContext = {
      path: location.pathname,
      viewing_product_id: viewing ? decodeURIComponent(viewing[1]) : null,
      shown_product_ids: location.pathname === "/products" && results ? results.products.map((p) => p.product_id) : [],
    };
    setInput("");
    markActive(); // chatting cheers Handsome Dan up
    setMessages((m) => [...m, { role: "user", content: text }]);
    setSending(true);
    try {
      const { reply, products, results_title, similar } = await sendChat(text, pageContext);
      setMessages((m) => [...m, { role: "assistant", content: reply, products, similar }]);
      // Update the website in real time: show the agent's product matches as cards on the Products page,
      // unless they're all already on screen ("how much is the second one?", "how much is this?" on a product
      // page). Then the page stays put, so "the third one" still refers to the same cards.
      const onScreen = new Set([...pageContext.shown_product_ids, pageContext.viewing_product_id]);
      if (products.length > 0 && !products.every((p) => onScreen.has(p.product_id))) {
        showResults(results_title ?? "Products from your chat", products);
        if (location.pathname !== "/products") navigate("/products");
      }
    } catch (err) {
      const detail = (err as Error).message;
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: detail.includes("Failed to fetch") ? "Sorry, I couldn't reach the server. Is the backend running?" : detail,
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  // "Products similar" bubble: show the related products on the page (no extra chat call; they're already loaded).
  function openSimilar(similar: SimilarProducts) {
    const n = similar.products.length;
    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        content: `Here ${n === 1 ? "is 1 similar product" : `are ${n} similar products`}: **${similar.title}**. They're on the page now.`,
        products: similar.products,
      },
    ]);
    showResults(similar.title, similar.products);
    if (location.pathname !== "/products") navigate("/products");
  }

  // "Start over": wipe the conversation (and, for logged-in shoppers, their saved history) so the agent starts fresh.
  async function startOver() {
    if (user && !window.confirm("Start over? This deletes your saved chat history.")) return;
    try {
      if (user) await clearChatHistory();
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Sorry, I couldn't clear your chat. Please try again." }]);
      return;
    }
    setMessages([GREETING]);
    setInput("");
    clearResults();
  }

  return (
    <>
      {open && (
        <section className="chat-panel" aria-label="Campus Customs chat">
          <header className="chat-header">
            <div className="chat-title">
              <Bulldog mood={mood} size={42} />
              <div>
                <strong>Campus Customs Assistant</strong>
                <small>{MOOD_CAPTION[mood]}</small>
              </div>
            </div>
            <div className="chat-header-actions">
              <button className="chat-start-over" onClick={startOver} disabled={sending} title="Clear the chat and start fresh">
                Start over
              </button>
              <button onClick={() => setOpen(false)} aria-label="Close chat">
                ✕
              </button>
            </div>
          </header>
          <div className="chat-messages">
            {freshChat && (
              <div className="bulldog-intro">
                <div className="bulldog-intro-dog">
                  <Bulldog mood={mood} size={110} />
                </div>
                <span className="bulldog-intro-woof">{INTRO_WOOF[mood]}</span>
              </div>
            )}
            {messages.map((m, i) => (
              <Fragment key={i}>
                <div className={`msg ${m.role}`}>
                  <RichText text={m.content} />
                </div>
                {m.products && m.products.length > 0 && (
                  <div className="chat-cards">
                    {m.products.slice(0, CARDS_IN_CHAT).map((p) => (
                      <ChatProductCard key={p.product_id} product={p} />
                    ))}
                    {m.products.length > CARDS_IN_CHAT && (
                      <small className="chat-more">+{m.products.length - CARDS_IN_CHAT} more on the page</small>
                    )}
                  </div>
                )}
                {m.similar && (
                  <button className="similar-bubble" onClick={() => openSimilar(m.similar!)}>
                    <span className="similar-bubble-label">Products similar</span>
                    {m.similar.title} ({m.similar.products.length}) →
                  </button>
                )}
              </Fragment>
            ))}
            {sending && <div className="msg assistant typing">Typing…</div>}
            <div ref={bottomRef} />
          </div>
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about a product…"
              aria-label="Chat message"
              maxLength={MAX_MESSAGE}
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      {!open && mood !== "happy" && (
        <button className={`chat-nudge ${mood}`} onClick={() => setOpen(true)}>
          {mood === "sad" ? "Handsome Dan misses you…" : "Handsome Dan is stressed! Chat with him?"}
        </button>
      )}
      <button className={`chat-toggle mood-${mood}`} onClick={() => setOpen((o) => !o)} aria-label="Toggle chat">
        {open ? "✕" : <Bulldog mood={mood} size={50} />}
      </button>
    </>
  );
}
