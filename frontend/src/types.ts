export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  in_stock: boolean;
}

export interface SizeStock {
  size: string;
  quantity: number;
  in_stock: boolean;
}

export interface ProductDetail extends Product {
  sizes: SizeStock[];
}

// Mirrors backend/models.py ProductCard: one structured product match returned by the chat agent.
export interface ProductCard {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  price: number;
  image_url: string;
  colors: string[];
  in_stock: boolean;
  sizes_in_stock: string[];
}

// The "Products similar" bubble under a chat reply (mirrors backend/models.py SimilarProducts).
export interface SimilarProducts {
  title: string;
  products: ProductCard[];
}

export interface ChatReply {
  reply: string;
  products: ProductCard[];
  results_title: string | null;
  similar: SimilarProducts | null;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: ProductCard[];
  similar?: SimilarProducts | null;
}

export interface User {
  id: number;
  name: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
}
