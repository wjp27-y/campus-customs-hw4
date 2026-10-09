import { useEffect, useMemo, useRef, useState } from "react";
import { getProducts } from "../api";
import { useChatResults } from "../chatResults";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

// catalogue.garment_type is free text ("pullover hoodie", "short-sleeve T-shirt", ...), so group it into
// a few shopper-friendly categories. Order matters: "crew-neck t-shirt" must match T-shirts first.
const CATEGORY_RULES: [string, RegExp][] = [
  ["Hoodies", /hood/i],
  ["Quarter-zips", /quarter-zip/i],
  ["T-shirts", /t-shirt/i],
  ["Jackets & fleece", /jacket/i],
  ["Long sleeve", /long-sleeve/i],
  ["Crewnecks & sweatshirts", /crew|sweatshirt|mockneck/i],
];

const categoryOf = (garmentType: string) =>
  CATEGORY_RULES.find(([, re]) => re.test(garmentType))?.[0] ?? "Other";

type Sort = "name" | "price-asc" | "price-desc";

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [sort, setSort] = useState<Sort>("name");
  const { results, clearResults } = useChatResults();
  const resultsRef = useRef<HTMLElement>(null);

  // New matches from the chat agent: bring them into view.
  useEffect(() => {
    if (results) resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [results?.updatedAt, loading]);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(
    () => ["All", ...CATEGORY_RULES.map(([c]) => c).filter((c) => products.some((p) => categoryOf(p.garment_type) === c))],
    [products],
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = products.filter(
      (p) =>
        (category === "All" || categoryOf(p.garment_type) === category) &&
        (!q || [p.name, p.description, ...p.search_tags, ...p.colors].some((s) => s.toLowerCase().includes(q))),
    );
    return filtered.sort((a, b) =>
      sort === "price-asc" ? a.price - b.price : sort === "price-desc" ? b.price - a.price : a.name.localeCompare(b.name),
    );
  }, [products, query, category, sort]);

  if (loading) return <p className="status">Loading products…</p>;
  if (error) return <p className="status error">Couldn't load products ({error}). Is the backend running?</p>;

  return (
    <>
      <h1 className="section-title">Products</h1>

      {results && (
        // key re-mounts the section on every new result set, replaying the highlight animation
        <section className="chat-results" ref={resultsRef} key={results.updatedAt} aria-live="polite">
          <div className="chat-results-header">
            <div>
              <span className="chat-results-eyebrow">From your chat</span>
              <h2>{results.title}</h2>
              <span className="status">
                {results.products.length} item{results.products.length === 1 ? "" : "s"}. Click a card for photos,
                sizes, and stock
              </span>
            </div>
            <button type="button" className="btn btn-light" onClick={clearResults}>
              Clear
            </button>
          </div>
          <div className="grid">
            {results.products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}

      <h2 className="section-title all-products-title">{results ? "All products" : ""}</h2>
      <div className="toolbar">
        <input
          type="search"
          placeholder="Search by name, college, sport, color…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Category">
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value as Sort)} aria-label="Sort">
          <option value="name">Name A–Z</option>
          <option value="price-asc">Price: low to high</option>
          <option value="price-desc">Price: high to low</option>
        </select>
        <span className="status">{visible.length} items</span>
      </div>
      <div className="grid">
        {visible.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </>
  );
}
