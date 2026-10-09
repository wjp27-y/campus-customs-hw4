import { createContext, useContext, useState, type ReactNode } from "react";
import type { ProductCard } from "./types";

// The latest product matches from the chat agent. ChatWidget sets them; the Products page renders them.
export interface ChatResults {
  title: string;
  products: ProductCard[];
  updatedAt: number; // changes on every new result set, so the page can re-highlight it
}

interface ChatResultsState {
  results: ChatResults | null;
  showResults: (title: string, products: ProductCard[]) => void;
  clearResults: () => void;
}

const ChatResultsContext = createContext<ChatResultsState | null>(null);

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(null);
  const value: ChatResultsState = {
    results,
    showResults: (title, products) => setResults({ title, products, updatedAt: Date.now() }),
    clearResults: () => setResults(null),
  };
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>;
}

export function useChatResults(): ChatResultsState {
  const ctx = useContext(ChatResultsContext);
  if (!ctx) throw new Error("useChatResults must be used inside <ChatResultsProvider>");
  return ctx;
}
