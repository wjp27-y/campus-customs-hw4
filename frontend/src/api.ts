import type { ChatMessage, ChatReply, Product, ProductDetail, User } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { credentials: "same-origin", ...init });
  if (!res.ok) {
    // FastAPI errors look like {"detail": "..."}; surface that message to the user.
    const body = await res.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : `${res.status} ${res.statusText}`);
  }
  return (res.status === 204 ? undefined : res.json()) as Promise<T>;
}

const postJson = <T>(path: string, data?: unknown) =>
  request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: data === undefined ? undefined : JSON.stringify(data),
  });

export interface RegisterInput {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirm_password: string;
}

export const register = (input: RegisterInput) => postJson<User>("/api/auth/register", input);
export const login = (email: string, password: string) => postJson<User>("/api/auth/login", { email, password });
export const logout = () => postJson<void>("/api/auth/logout");
export const getMe = () => request<User>("/api/auth/me");

export const getProducts = () => request<Product[]>("/api/products");

export const getProduct = (id: string) =>
  request<ProductDetail>(`/api/products/${encodeURIComponent(id)}`);

// What the shopper is looking at; lets the agent work out "this one" / "it" (mirrors backend PageContext).
export interface PageContext {
  path: string;
  viewing_product_id: string | null;
  shown_product_ids: string[];
}

export const sendChat = (message: string, page_context: PageContext) =>
  postJson<ChatReply>("/api/chat", { message, page_context });
export const getChatHistory = () => request<ChatMessage[]>("/api/chat/history");
// "Start over": deletes a logged-in shopper's saved chat (a no-op for guests).
export const clearChatHistory = () => request<void>("/api/chat/history", { method: "DELETE" });

export const formatPrice = (price: number) => `$${price.toFixed(2)}`;

// First sentence of the catalogue description, for product grid cards.
export const shortDescription = (description: string) => {
  const end = description.indexOf(". ");
  return end === -1 ? description : description.slice(0, end + 1);
};
