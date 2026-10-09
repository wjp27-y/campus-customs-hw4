import { useEffect, useRef, useState, type MouseEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { formatPrice, shortDescription } from "../api";
import { CARD_POINTS, usePoints } from "../fun/points";
import type { Product } from "../types";

// The fields a card needs. Catalogue products (Products page) and chat agent matches both have them,
// so the same card, with the same click-through to the product page, is used for both.
export type CardProduct = Pick<Product, "product_id" | "name" | "price" | "description" | "image_url" | "in_stock">;

const POP_MS = 380; // length of the pop-out animation before opening the product page

export default function ProductCard({ product }: { product: CardProduct }) {
  const { award } = usePoints();
  const navigate = useNavigate();
  const [popping, setPopping] = useState(false);
  const timer = useRef<number | undefined>(undefined);
  const to = `/products/${product.product_id}`;

  useEffect(() => () => clearTimeout(timer.current), []);

  // Clicking a card earns points and pops it out, then opens the product page.
  // Ctrl/Cmd/Shift-clicks still earn points but are left to the browser (open in a new tab, etc.).
  function handleClick(e: MouseEvent) {
    award(CARD_POINTS, `Checked out ${product.name}`);
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    if (popping) return;
    setPopping(true);
    timer.current = window.setTimeout(() => navigate(to), POP_MS);
  }

  return (
    <Link to={to} className={`card${popping ? " popping" : ""}`} onClick={handleClick}>
      <div className="card-img">
        <img src={product.image_url} alt={product.name} loading="lazy" />
      </div>
      <div className="card-body">
        <p className="card-name">{product.name}</p>
        <span className="card-price">{formatPrice(product.price)}</span>
        <p className="card-desc">{shortDescription(product.description)}</p>
        {!product.in_stock && <span className="badge badge-bad">Sold out</span>}
      </div>
    </Link>
  );
}
