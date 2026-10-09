import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

const FEATURES = [
  {
    title: "Officially licensed",
    text: "Every item we carry is approved Yale merchandise, so you know the logos, crests, and colors are the real thing.",
  },
  {
    title: "Something for every Eli",
    text: "Gear for the residential colleges, the varsity teams, and Yale's graduate and professional schools.",
  },
  {
    title: "Made for everyday wear",
    text: "Soft hoodies, crewnecks, and tees you'll want to wear to section, to the Game, and long after you graduate.",
  },
];

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([]);

  useEffect(() => {
    getProducts()
      .then((all) => setFeatured(all.filter((p) => p.in_stock).slice(0, 4)))
      .catch(() => setFeatured([]));
  }, []);

  return (
    <>
      <section className="hero">
        <h1>Wear your Bulldog spirit.</h1>
        <p>
          Campus Customs is New Haven's home for Yale apparel. Whether you're a first-year, a proud parent, or an
          alum heading back for reunion, find comfortable, officially licensed gear to show where your heart is.
        </p>
        <Link to="/products" className="btn">
          Shop all products
        </Link>
        <Link to="/about" className="btn ghost">
          Our story
        </Link>
      </section>

      <section className="features">
        {FEATURES.map((f) => (
          <div key={f.title} className="feature">
            <h3>{f.title}</h3>
            <p>{f.text}</p>
          </div>
        ))}
      </section>

      {featured.length > 0 && (
        <section>
          <h2 className="section-title">Fan favorites</h2>
          <div className="grid">
            {featured.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
