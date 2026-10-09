"""Tools the Campus Customs agent can call.

Every tool is read-only and uses parameterized SQL, so the model can look things up but can never change
the database. Product facts in the agent's replies (names, prices, colors, stock) must come from here.
"""

import json
import re
import sqlite3
from collections import Counter

from pydantic_ai import ModelRetry, RunContext

from models import (
    AgentDeps,
    CustomerProfile,
    PageContext,
    PageInfo,
    ProductCard,
    ProductDescription,
    ProductMatch,
    ProductPrice,
    ProductRef,
    ProductStock,
    ShopperContext,
    SimilarProducts,
    SimilarSearch,
    SizeStock,
)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# Words shoppers use for sizes -> inventory.size values.
SIZE_ALIASES = {
    "xs": "XS", "extra small": "XS", "x-small": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x-large": "XL",
    "xxl": "XXL", "2xl": "XXL", "xx-large": "XXL", "double xl": "XXL", "extra extra large": "XXL",
}

# catalogue.garment_type is free text, so group it the same way the Products page does.
# Order matters: "crew-neck t-shirt" must land in t-shirts, "full-zip hooded sweatshirt" in hoodies.
CATEGORIES: list[tuple[str, re.Pattern[str]]] = [
    ("hoodies", re.compile(r"hood", re.I)),
    ("quarter-zips", re.compile(r"quarter-zip", re.I)),
    ("t-shirts", re.compile(r"t-shirt", re.I)),
    ("jackets & fleece", re.compile(r"jacket", re.I)),
    ("long sleeve", re.compile(r"long-sleeve", re.I)),
    ("crewnecks & sweatshirts", re.compile(r"crew|sweatshirt|mockneck", re.I)),
]

STOP_WORDS = {"a", "an", "the", "and", "or", "for", "with", "in", "of", "do", "you", "have", "any", "some", "me", "show", "i", "want", "looking"}


def category_of(garment_type: str) -> str:
    return next((name for name, pattern in CATEGORIES if pattern.search(garment_type)), "other")


def _stock_by_product(conn: sqlite3.Connection) -> dict[str, list[str]]:
    sizes: dict[str, list[str]] = {}
    for row in conn.execute("SELECT product_id, size FROM inventory WHERE quantity > 0"):
        sizes.setdefault(row["product_id"], []).append(row["size"])
    for size_list in sizes.values():
        size_list.sort(key=_size_key)
    return sizes


def _score(row: sqlite3.Row, terms: list[str]) -> int:
    """Simple relevance: name matches count most, then tags/colors/type, then description."""
    name = row["name"].lower()
    tags = " ".join(json.loads(row["search_tags"])).lower()
    colors = " ".join(json.loads(row["colors"])).lower()
    garment = row["garment_type"].lower()
    desc = row["description"].lower()
    score = 0
    for term in terms:
        stem = term.rstrip("s") if len(term) > 3 else term  # "hoodies" -> "hoodie"
        if stem in name:
            score += 5
        if stem in tags or stem in colors or stem in garment:
            score += 3
        if stem in desc:
            score += 1
    return score


# ---------------------------------------------------------------- tools

def find_products(
    conn: sqlite3.Connection,
    query: str = "",
    category: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    limit: int = 8,
    exclude: set[str] | None = None,
) -> list[ProductMatch]:
    """The catalogue search behind search_products (also used for the 'Products similar' bubble)."""
    limit = max(1, min(limit, 20))
    terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t not in STOP_WORDS]
    rows = conn.execute("SELECT * FROM catalogue").fetchall()
    stock = _stock_by_product(conn)

    results: list[tuple[int, ProductMatch]] = []
    for row in rows:
        if exclude and row["product_id"] in exclude:
            continue
        if category and category_of(row["garment_type"]) != category.lower().strip():
            continue
        colors = json.loads(row["colors"])
        if color and not any(color.lower() in c.lower() for c in colors):
            continue
        if max_price is not None and row["price"] > max_price:
            continue
        in_stock = bool(stock.get(row["product_id"]))
        if in_stock_only and not in_stock:
            continue
        score = _score(row, terms) if terms else 1
        if terms and score == 0:
            continue
        results.append(
            (
                score,
                ProductMatch(
                    product_id=row["product_id"],
                    name=row["name"],
                    garment_type=row["garment_type"],
                    price=row["price"],
                    colors=colors,
                    in_stock=in_stock,
                ),
            )
        )

    results.sort(key=lambda r: (-r[0], r[1].name))
    return [match for _, match in results[:limit]]


def search_products(
    ctx: RunContext[AgentDeps],
    query: str = "",
    category: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    limit: int = 8,
) -> list[ProductMatch]:
    """Search the Campus Customs catalogue.

    Args:
        query: Free-text keywords, e.g. "berkeley college", "baseball", "vintage bulldog", "gift for dad".
        category: Optional category filter. One of: hoodies, quarter-zips, t-shirts, jackets & fleece,
            long sleeve, crewnecks & sweatshirts.
        color: Optional color filter, e.g. "navy", "gray", "white".
        max_price: Optional maximum price in US dollars.
        in_stock_only: If true, only return products with at least one size in stock.
        limit: Maximum number of results (1-20).
    """
    with ctx.deps.get_db() as conn:
        return find_products(conn, query, category, color, max_price, in_stock_only, limit)


def _catalogue_row(ctx: RunContext[AgentDeps], product_id: str, columns: str) -> sqlite3.Row:
    """Primary-key lookup of just the needed catalogue columns; asks the model to retry on an unknown ID."""
    with ctx.deps.get_db() as conn:
        row = conn.execute(f"SELECT {columns} FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    if row is None:
        raise ModelRetry(f"No product with product_id {product_id!r}. Use search_products to find the right ID.")
    return row


def _size_key(size: str) -> int:
    return SIZE_ORDER.index(size) if size in SIZE_ORDER else len(SIZE_ORDER)


def get_product_description(ctx: RunContext[AgentDeps], product_id: str) -> ProductDescription:
    """Get what a product looks like: its description, garment type, and colors.

    Use for questions like "what does it look like?", "what color is it?", "is it a pullover or a zip?".

    Args:
        product_id: The product_id exactly as returned by search_products.
    """
    row = _catalogue_row(ctx, product_id, "product_id, name, garment_type, description, colors")
    return ProductDescription(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
    )


def get_product_price(ctx: RunContext[AgentDeps], product_id: str) -> ProductPrice:
    """Get a product's current price in US dollars.

    Use for questions like "how much is it?" or when comparing prices.

    Args:
        product_id: The product_id exactly as returned by search_products.
    """
    row = _catalogue_row(ctx, product_id, "product_id, name, price")
    return ProductPrice(product_id=row["product_id"], name=row["name"], price=row["price"])


def get_stock(ctx: RunContext[AgentDeps], product_id: str, size: str | None = None) -> ProductStock:
    """Get how many units of a product are in stock, for every size or one size.

    Use for questions like "is it in stock?", "how many mediums do you have?", "what sizes are available?".

    Args:
        product_id: The product_id exactly as returned by search_products.
        size: Optional size to check: XS, S, M, L, XL, or XXL (words like "medium" also work).
            Leave empty to get every size.
    """
    wanted = None
    if size:
        wanted = SIZE_ALIASES.get(size.strip().lower(), size.strip().upper())
        if wanted not in SIZE_ORDER:
            raise ModelRetry(f"Unknown size {size!r}. Use one of: {', '.join(SIZE_ORDER)}, or leave size empty.")

    row = _catalogue_row(ctx, product_id, "product_id, name")
    with ctx.deps.get_db() as conn:
        if wanted:
            inv = conn.execute(
                "SELECT size, quantity FROM inventory WHERE product_id = ? AND size = ?", (product_id, wanted)
            ).fetchall()
        else:
            inv = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()

    sizes = sorted(
        (SizeStock(size=r["size"], quantity=r["quantity"], in_stock=r["quantity"] > 0) for r in inv),
        key=lambda s: _size_key(s.size),
    )
    if wanted and not sizes:  # catalogue has the product but no row for that size: treat as none in stock
        sizes = [SizeStock(size=wanted, quantity=0, in_stock=False)]
    total = sum(s.quantity for s in sizes)
    return ProductStock(product_id=row["product_id"], name=row["name"], sizes=sizes, total_quantity=total, in_stock=total > 0)


def list_categories(ctx: RunContext[AgentDeps]) -> list[dict]:
    """List the product categories with how many products each has and their price range.

    Use this for broad questions like "what do you sell?" or "what's your cheapest item?".
    """
    with ctx.deps.get_db() as conn:
        rows = conn.execute("SELECT garment_type, price FROM catalogue").fetchall()
    summary: dict[str, dict] = {}
    for row in rows:
        cat = summary.setdefault(category_of(row["garment_type"]), {"count": 0, "min_price": None, "max_price": None})
        cat["count"] += 1
        cat["min_price"] = row["price"] if cat["min_price"] is None else min(cat["min_price"], row["price"])
        cat["max_price"] = row["price"] if cat["max_price"] is None else max(cat["max_price"], row["price"])
    return [{"category": name, **info} for name, info in summary.items()]


def get_shopper_context(ctx: RunContext[AgentDeps]) -> ShopperContext:
    """Who you're talking to and what they're looking at on the website.

    Call this when the shopper refers to a product without naming it ("how much is this?", "do you have it in
    medium?", "tell me about that one", "the second one") or when you want to greet them. Returns:
    the customer's first/last name and member-since date (logged-in shoppers only), the product page they have
    open, the chat result cards currently on their page, and the product discussed most recently.
    """
    return ctx.deps.shopper or ShopperContext(
        logged_in=False,
        customer=None,
        page=PageInfo(path="/", page_type="other", viewing_product=None, products_on_page=[], last_discussed_product=None),
    )


AGENT_TOOLS = [
    search_products,
    get_product_description,
    get_product_price,
    get_stock,
    list_categories,
    get_shopper_context,
]


# ---------------------------------------------------------------- helpers for the API (not agent tools)

def load_product_cards(conn: sqlite3.Connection, product_ids: list[str]) -> list[ProductCard]:
    """Turn the agent's product_ids into cards using real database values. Unknown IDs are dropped."""
    stock = _stock_by_product(conn)
    cards: list[ProductCard] = []
    seen: set[str] = set()
    for pid in product_ids:
        if pid in seen:
            continue
        seen.add(pid)
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (pid,)).fetchone()
        if row is None:
            continue
        sizes = stock.get(pid, [])
        cards.append(
            ProductCard(
                product_id=pid,
                name=row["name"],
                garment_type=row["garment_type"],
                description=row["description"],
                price=row["price"],
                image_url=f"/images/{row['image_file_path']}",
                colors=json.loads(row["colors"]),
                in_stock=bool(sizes),
                sizes_in_stock=sizes,
            )
        )
    return cards


# "Products similar" bubble (Problem 9): by default, the same color in a neighbouring category,
# e.g. navy hoodies -> navy t-shirts.
RELATED_CATEGORIES = {
    "hoodies": "t-shirts",
    "t-shirts": "crewnecks & sweatshirts",
    "long sleeve": "t-shirts",
    "crewnecks & sweatshirts": "hoodies",
    "quarter-zips": "jackets & fleece",
    "jackets & fleece": "quarter-zips",
}
SIMILAR_LIMIT = 8


def _main_color(cards: list[ProductCard]) -> str | None:
    """The main color most of the cards share. Each product's first color is its garment color (the rest are
    print/accent colors), and "navy blue" and "navy" both count as navy."""
    counts = Counter("navy" if "navy" in c.colors[0].lower() else c.colors[0].lower() for c in cards if c.colors)
    return counts.most_common(1)[0][0] if counts else None


def similar_products(
    conn: sqlite3.Connection, cards: list[ProductCard], hint: SimilarSearch | None
) -> SimilarProducts | None:
    """In-stock products related to the shopper's results, excluding the ones already shown.

    Tries the agent's suggestion first, then the same color in a related category, then more of the same
    category in that color. Returns None if nothing turns up (no bubble).
    """
    if not cards:
        return None
    searches: list[tuple[str, str, str | None, str | None]] = []
    if hint and (hint.query.strip() or hint.category or hint.color):
        searches.append((hint.label, hint.query, hint.category, hint.color))
    category = Counter(category_of(c.garment_type) for c in cards).most_common(1)[0][0]
    color = _main_color(cards)
    if color and category in RELATED_CATEGORIES:
        related = RELATED_CATEGORIES[category]
        searches.append((f"{color.capitalize()} {related}", "", related, color))
        searches.append((f"More {color} {category}", "", category, color))

    shown = {c.product_id for c in cards}
    for label, query, cat, col in searches:
        matches = find_products(conn, query, cat, col, in_stock_only=True, limit=20, exclude=shown)
        if col:  # "navy t-shirts" means navy shirts, not gray shirts with a navy print
            matches = [m for m in matches if m.colors and col.lower() in m.colors[0].lower()]
        matches = matches[:SIMILAR_LIMIT]
        if matches:
            return SimilarProducts(title=label, products=load_product_cards(conn, [m.product_id for m in matches]))
    return None


def _page_type(path: str) -> str:
    if path == "/":
        return "home"
    if path == "/products":
        return "products"
    if path.startswith("/products/"):
        return "product"
    return {"/about": "about", "/login": "login", "/register": "register"}.get(path, "other")


def _product_refs(conn: sqlite3.Connection, product_ids: list[str]) -> list[ProductRef]:
    """Look up names for product IDs; IDs that aren't in the catalogue are dropped (page context is untrusted)."""
    refs: list[ProductRef] = []
    for pid in dict.fromkeys(product_ids):
        row = conn.execute("SELECT product_id, name FROM catalogue WHERE product_id = ?", (pid,)).fetchone()
        if row:
            refs.append(ProductRef(product_id=row["product_id"], name=row["name"]))
    return refs


def build_shopper_context(conn: sqlite3.Connection, user: sqlite3.Row | None, page: PageContext) -> ShopperContext:
    """Assemble the customer profile (logged-in only) and the validated page context for one chat turn."""
    customer, last_discussed = None, None
    if user is not None:
        saved = conn.execute("SELECT COUNT(*) FROM chat_messages WHERE user_id = ?", (user["id"],)).fetchone()[0]
        customer = CustomerProfile(
            first_name=user["first_name"],
            last_name=user["last_name"],
            member_since=str(user["created_at"])[:10],
            saved_messages=saved,
        )
        last = conn.execute(
            "SELECT products_json FROM chat_messages WHERE user_id = ? AND role = 'assistant' "
            "AND products_json IS NOT NULL ORDER BY id DESC LIMIT 1",
            (user["id"],),
        ).fetchone()
        if last:
            try:
                ids = [p["product_id"] for p in json.loads(last["products_json"]) if isinstance(p, dict)]
            except (ValueError, TypeError, KeyError):
                ids = []
            refs = _product_refs(conn, ids[:1])
            last_discussed = refs[0] if refs else None

    viewing = _product_refs(conn, [page.viewing_product_id]) if page.viewing_product_id else []
    return ShopperContext(
        logged_in=user is not None,
        customer=customer,
        page=PageInfo(
            path=page.path,
            page_type=_page_type(page.path),
            viewing_product=viewing[0] if viewing else None,
            products_on_page=_product_refs(conn, page.shown_product_ids),
            last_discussed_product=last_discussed,
        ),
    )


# Fact-checker (agent.check_reply): the database facts a reply is checked against.
MAX_FACT_PRODUCTS = 15


def build_facts(conn: sqlite3.Connection, product_ids: list[str]) -> list[dict]:
    """Name, price, and units in stock per size, straight from the database. Unknown IDs are skipped."""
    facts = []
    for pid in list(dict.fromkeys(product_ids))[:MAX_FACT_PRODUCTS]:
        row = conn.execute("SELECT product_id, name, price FROM catalogue WHERE product_id = ?", (pid,)).fetchone()
        if row is None:
            continue
        inv = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (pid,)).fetchall()
        stock = {r["size"]: r["quantity"] for r in sorted(inv, key=lambda r: _size_key(r["size"]))}
        facts.append({"product_id": row["product_id"], "name": row["name"], "price": row["price"], "stock": stock})
    return facts
