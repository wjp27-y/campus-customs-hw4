"""Structured types for the Campus Customs chat agent.

- ChatRequest / ChatHistoryMessage: what the website sends to POST /api/chat
- AgentReply / SimilarSearch: the structured output the PydanticAI agent must return
- FactCheck: the structured output of the fact-checker agent (agent.fact_checker)
- ProductCard / SimilarProducts / ChatResponse: what the API sends back to the chat widget
- ProductMatch / ProductDescription / ProductPrice / ProductStock / SizeStock: what the tools return to the agent
- AgentDeps: dependencies injected into every tool call
"""

import re
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_CHARS = 1000
MAX_HISTORY_MESSAGES = 20
MAX_PRODUCT_CARDS = 8
MAX_REPLY_SENTENCES = 7  # Problem 12: a reply is one paragraph of at most 7 sentences

SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=\S)")
LIST_MARKER = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def cap_reply(text: str) -> str:
    """Join the reply into one paragraph and keep its first MAX_REPLY_SENTENCES sentences."""
    lines = [LIST_MARKER.sub("", line).strip() for line in text.splitlines()]
    paragraph = " ".join(line if line[-1] in ".!?:" else line + "." for line in lines if line)
    return " ".join(SENTENCE_END.split(paragraph)[:MAX_REPLY_SENTENCES])


# ---------------------------------------------------------------- website -> API

class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class PageContext(BaseModel):
    """What the shopper is looking at when they send a message (sent by the website with every chat message).

    Untrusted input: the server keeps only product IDs that exist in the catalogue and looks up their names itself.
    """

    path: str = Field(default="/", max_length=200, description="Current page URL path, e.g. /products/basic-hoodie-big-yale")
    viewing_product_id: str | None = Field(default=None, max_length=100, description="Product open on a product page")
    shown_product_ids: list[str] = Field(
        default_factory=list, max_length=MAX_PRODUCT_CARDS, description="Chat result cards currently on the page"
    )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    page_context: PageContext = Field(default_factory=PageContext)
    # No client-sent history: logged-in shoppers' history comes from chat_messages; guests' isn't remembered.


# ---------------------------------------------------------------- agent output

class SimilarSearch(BaseModel):
    """The agent's suggestion for the 'Products similar' bubble. Only search terms: products come from the database."""

    label: str = Field(max_length=60, description="Bubble text, e.g. 'Navy t-shirts'")
    query: str = Field(default="", max_length=100, description="Keywords, e.g. 'bulldog'. Can be empty")
    category: str | None = Field(default=None, description="Same categories as search_products, e.g. 't-shirts'")
    color: str | None = Field(default=None, max_length=30, description="Color filter, e.g. 'navy'")


class AgentReply(BaseModel):
    """The agent's final answer for one chat turn."""

    reply: str = Field(
        description="The message shown to the shopper: one plain-text paragraph of at most 7 sentences, no lists."
    )
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=MAX_PRODUCT_CARDS,
        description=(
            "The structured product matches: product_id values (exactly as returned by the tools) for every product "
            "the shopper asked for or that you are recommending, most relevant first. The website shows these as "
            "product cards on the page. Leave empty if the message isn't about specific products."
        ),
    )
    results_title: str | None = Field(
        default=None,
        description=(
            "Short heading for the product cards shown on the page, e.g. 'Navy hoodies' or 'Berkeley College gear'. "
            "Required when product_ids is not empty; null otherwise."
        ),
    )
    similar_search: SimilarSearch | None = Field(
        default=None,
        description=(
            "A related search for the 'Products similar' bubble under the cards, e.g. navy t-shirts after navy "
            "hoodies. Set it when product_ids is not empty; null otherwise. The server runs the search itself."
        ),
    )

    @field_validator("reply")
    @classmethod
    def one_short_paragraph(cls, value: str) -> str:
        return cap_reply(value)


class FactCheck(BaseModel):
    """The fact-checker agent's verdict on one reply."""

    accurate: bool = Field(description="True if every price and stock claim in the reply matches the database facts")
    problems: list[str] = Field(default_factory=list, description="Each wrong or unsupported claim, e.g. 'Says $45; price is $68'")
    corrected_reply: str | None = Field(
        default=None, description="The reply rewritten with only the wrong claims fixed. Null when accurate"
    )


# ---------------------------------------------------------------- API -> website

class ProductCard(BaseModel):
    """One structured product match, rendered as a product card in the chat and on the page.

    Built from the database (never from model text). Has the same fields the website's Problem 3 ProductCard
    component needs (product_id, name, price, description, image_url, in_stock), so cards look and click the same.
    """

    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    image_url: str
    colors: list[str]
    in_stock: bool
    sizes_in_stock: list[str]


class SimilarProducts(BaseModel):
    """The 'Products similar' bubble: a heading plus product cards, ready to show when the shopper clicks it."""

    title: str
    products: list[ProductCard]


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    results_title: str | None = None  # heading for the page's "From your chat" results
    similar: SimilarProducts | None = None  # the "Products similar" bubble (Problem 9)


# ---------------------------------------------------------------- tool results

class ProductMatch(BaseModel):
    product_id: str
    name: str
    garment_type: str
    price: float
    colors: list[str]
    in_stock: bool


# The three lookup results below use catalogue column names as field names, so each tool is a single
# primary-key lookup whose row maps straight onto the model (see output/harness.md, Problem 6).

class ProductDescription(BaseModel):
    """get_product_description result. Fields = catalogue columns."""

    product_id: str = Field(description="catalogue.product_id")
    name: str = Field(description="catalogue.name")
    garment_type: str = Field(description="catalogue.garment_type")
    description: str = Field(description="catalogue.description: what the item looks like")
    colors: list[str] = Field(description="catalogue.colors (parsed from JSON)")


class ProductPrice(BaseModel):
    """get_product_price result. Fields = catalogue columns."""

    product_id: str = Field(description="catalogue.product_id")
    name: str = Field(description="catalogue.name")
    price: float = Field(description="catalogue.price in US dollars")


class SizeStock(BaseModel):
    size: str = Field(description="inventory.size")
    quantity: int = Field(description="inventory.quantity: units on hand")
    in_stock: bool = Field(description="quantity > 0")


class ProductStock(BaseModel):
    """get_stock result: catalogue identity fields plus inventory rows for the product."""

    product_id: str = Field(description="catalogue.product_id")
    name: str = Field(description="catalogue.name")
    sizes: list[SizeStock] = Field(description="One entry per size (or just the requested size), XS to XXL")
    total_quantity: int = Field(description="Sum of quantity across the sizes listed")
    in_stock: bool = Field(description="True if any listed size has quantity > 0")


# ---------------------------------------------------------------- dependencies

@dataclass
class AgentDeps:
    get_db: Callable[[], AbstractContextManager[Connection]]
    shopper: "ShopperContext | None" = None  # who the agent is talking to + what's on their page


# ---------------------------------------------------------------- customer memory + page context

class ProductRef(BaseModel):
    product_id: str
    name: str


class CustomerProfile(BaseModel):
    """The only customer fields the agent sees. Never email, password hash, or user id."""

    first_name: str | None = Field(description="users.first_name, for greeting by name")
    last_name: str | None = Field(description="users.last_name")
    member_since: str = Field(description="Date from users.created_at, e.g. 2026-09-19")
    saved_messages: int = Field(description="How many earlier chat messages are saved for this customer")


class PageInfo(BaseModel):
    path: str = Field(description="Current page path")
    page_type: str = Field(description="home, products, product, about, login, register, or other")
    viewing_product: ProductRef | None = Field(description="The product page the shopper has open, if any")
    products_on_page: list[ProductRef] = Field(description="Chat result cards currently shown on the page")
    last_discussed_product: ProductRef | None = Field(
        description="First product in the agent's most recent saved reply (logged-in shoppers only)"
    )


class ShopperContext(BaseModel):
    """get_shopper_context result: who the shopper is and what they're looking at."""

    logged_in: bool
    customer: CustomerProfile | None = Field(description="None for guests")
    page: PageInfo
