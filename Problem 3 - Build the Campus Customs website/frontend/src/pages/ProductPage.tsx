import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { formatPrice, getProduct } from "../api";
import { BUY_POINTS, usePoints } from "../fun/points";
import type { ProductDetail } from "../types";

const LOW_STOCK = 5;

export default function ProductPage() {
  const { productId = "" } = useParams();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [size, setSize] = useState<string | null>(null);
  const [bought, setBought] = useState<{ size: string; at: number } | null>(null);
  const { award } = usePoints();

  useEffect(() => {
    setProduct(null);
    setError(null);
    setSize(null);
    setBought(null);
    getProduct(productId)
      .then(setProduct)
      .catch((e: Error) => setError(e.message));
  }, [productId]);

  if (error) return <p className="status error">Couldn't load this product ({error}).</p>;
  if (!product) return <p className="status">Loading…</p>;

  return (
    <>
      <Link to="/products" className="back-link">
        ← Back to all products
      </Link>
      <div className="detail">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div>
          <p className="detail-type">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <div className="detail-price">{formatPrice(product.price)}</div>
          <span className={`badge ${product.in_stock ? "badge-ok" : "badge-bad"}`}>
            {product.in_stock ? "In stock" : "Sold out in all sizes"}
          </span>
          <p className="detail-desc">{product.description}</p>

          {product.colors.length > 0 && (
            <div className="colors">
              {product.colors.map((c) => (
                <span key={c} className="chip">
                  {c}
                </span>
              ))}
            </div>
          )}

          <strong>Sizes</strong>
          <div className="sizes">
            {product.sizes.map((s) => (
              <button
                key={s.size}
                type="button"
                className={`size${s.in_stock ? "" : " out"}${size === s.size ? " selected" : ""}`}
                disabled={!s.in_stock}
                onClick={() => setSize(s.size)}
              >
                <strong>{s.size}</strong>
                <small>
                  {!s.in_stock ? "Out of stock" : s.quantity <= LOW_STOCK ? `Only ${s.quantity} left` : "In stock"}
                </small>
              </button>
            ))}
          </div>

          {/* No checkout yet: "Buy" confirms on the page and earns the purchase points. */}
          <button
            className="btn"
            disabled={!size}
            onClick={() => {
              if (!size) return;
              award(BUY_POINTS, `Bought ${product.name} (${size})`);
              setBought({ size, at: Date.now() }); // new "at" replays the confirmation animation
            }}
          >
            {size ? `Buy size ${size} · +${BUY_POINTS} pts` : "Select a size"}
          </button>
          {bought && (
            <p className="buy-msg" key={bought.at}>
              Bought size {bought.size}! +{BUY_POINTS} merch points.
            </p>
          )}
        </div>
      </div>
    </>
  );
}
