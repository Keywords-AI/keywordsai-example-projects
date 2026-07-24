"""Central configuration. Everything tunable lives here or in the environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

# --- paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# Load every .env from the project directory upward, nearest first. load_dotenv
# never overrides an already-set var, so the closest file wins while a shared key
# kept one level up still resolves. A bare load_dotenv() stops at the FIRST file
# it finds: the moment this project grew its own .env, that shadowed the parent
# holding RESPAN_API_KEY and the gateway silently switched off.
for _dir in (BASE_DIR, *BASE_DIR.parents):
    _env_file = _dir / ".env"
    if _env_file.is_file():
        load_dotenv(_env_file)
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
CHROMA_DIR = STORAGE_DIR / "chroma"
SUBJECTS_FILE = STORAGE_DIR / "subjects.json"   # subjects + their books
CHATS_FILE = STORAGE_DIR / "chats.json"         # chat index (sidebar)
MESSAGES_DIR = STORAGE_DIR / "messages"         # messages/{chat_id}.json

# Pre-Subject layout, read only by scripts/migrate_to_subjects.py.
LEGACY_TUTORS_FILE = STORAGE_DIR / "tutors.json"
LEGACY_CHATS_DIR = STORAGE_DIR / "chats"

for _d in (STORAGE_DIR, UPLOADS_DIR, CHROMA_DIR, MESSAGES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- keys ---
# Generation can go one of two ways:
#   1. Respan Gateway (set RESPAN_API_KEY) — routes to Claude AND logs every call
#      in Respan. No ANTHROPIC_API_KEY needed; the gateway handles provider auth.
#   2. Anthropic directly (set ANTHROPIC_API_KEY).
# If RESPAN_API_KEY is present it wins.
RESPAN_API_KEY = os.environ.get("RESPAN_API_KEY")
RESPAN_GATEWAY_URL = os.environ.get(
    "RESPAN_GATEWAY_URL", "https://api.respan.ai/api/anthropic/"
)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")       # used only if no RESPAN_API_KEY
USE_GATEWAY = bool(RESPAN_API_KEY)

LLAMA_CLOUD_API_KEY = os.environ.get("LLAMA_CLOUD_API_KEY")   # optional (better PDF parsing)

# --- models ---
# Claude Opus 4.8 is the default. Switch to a cheaper tier for a snappier/cheaper
# tutor by setting GENERATION_MODEL=claude-haiku-4-5 (or claude-sonnet-5) in .env.
GENERATION_MODEL = os.environ.get("GENERATION_MODEL", "claude-opus-4-8")
# Adaptive thinking is on by default. Set THINKING=off for a snappier/cheaper tutor.
THINKING = os.environ.get("THINKING", "adaptive")
THINKING_ON = THINKING.lower() not in ("off", "none", "disabled", "")

# Adaptive thinking only exists on Claude 4.6+. Older models (Haiku 4.5,
# Sonnet 4.5) reject {"type": "adaptive"} with a 400, so we check the model
# rather than trusting GENERATION_MODEL and THINKING to be kept in sync — a
# lone GENERATION_MODEL=claude-haiku-4-5 used to break every request.
_ADAPTIVE_THINKING_MODELS = {
    "claude-fable-5", "claude-mythos-5",
    "claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6",
    "claude-sonnet-5", "claude-sonnet-4-6",
}


def thinking_config(model: str) -> dict | None:
    """The `thinking` kwarg for this model, or None to omit it entirely."""
    if THINKING_ON and model in _ADAPTIVE_THINKING_MODELS:
        return {"type": "adaptive"}
    return None


# Models a tutor may be switched to from the UI. An allowlist rather than free
# text: the value reaches the API directly, and a typo would 404 every question.
# `thinking` is derived per model above, so picking a pre-4.6 model here just
# runs without it instead of erroring.
AVAILABLE_MODELS = [
    {"id": "claude-opus-4-8", "label": "Opus 4.8", "note": "most capable"},
    {"id": "claude-opus-4-7", "label": "Opus 4.7", "note": "previous Opus"},
    {"id": "claude-sonnet-5", "label": "Sonnet 5", "note": "faster, cheaper"},
    {"id": "claude-sonnet-4-6", "label": "Sonnet 4.6", "note": "previous Sonnet"},
    {"id": "claude-haiku-4-5", "label": "Haiku 4.5", "note": "fastest, no thinking"},
]
_ALLOWED_MODEL_IDS = {m["id"] for m in AVAILABLE_MODELS}


# Teaching styles offered when starting a chat. Lives here rather than in the
# markup so a subject's default and a chat's own style pick from one list.
TEACHING_STYLES = [
    {"label": "Default", "value": ""},
    {"label": "Socratic", "value": "Socratic — guide the student with questions rather than giving the answer outright."},
    {"label": "Concise", "value": "Concise — keep explanations short and to the point."},
    {"label": "Step by step", "value": "Step by step — break every explanation into clear, numbered steps."},
    {"label": "Worked examples", "value": "Worked examples — teach by walking through concrete examples in detail."},
    {"label": "Exam prep", "value": "Exam prep — emphasize what is most likely to be tested and common pitfalls."},
    {"label": "Plain language", "value": "Plain language — explain in the simplest terms, with minimal jargon."},
]

# Short label for a stored style string, for the sidebar chip.
_STYLE_LABELS = {s["value"]: s["label"] for s in TEACHING_STYLES if s["value"]}


def style_label(instructions: str | None) -> str:
    """"Socratic" for a known style, a trimmed prefix for a custom one."""
    text = (instructions or "").strip()
    if not text:
        return "Default"
    if text in _STYLE_LABELS:
        return _STYLE_LABELS[text]
    return (text.split("—")[0].split(".")[0].strip() or "Custom")[:24]


def resolve_model(requested: str | None) -> str:
    """A tutor's model if it's one we allow, else the configured default."""
    if requested and requested in _ALLOWED_MODEL_IDS:
        return requested
    return GENERATION_MODEL


# Local embedding model — no API key, runs on your machine. First run downloads it.
EMBED_MODEL = os.environ.get("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Vision model: transcribing an uploaded exercise, and (v2) captioning figures
# at ingest. This is OCR-shaped work, not reasoning, so it defaults to the
# cheapest vision-capable tier rather than inheriting GENERATION_MODEL — running
# it on Opus cost ~5x for no measurable gain in transcription quality.
CAPTION_IMAGES = os.environ.get("CAPTION_IMAGES", "true").lower() not in ("0", "false", "off", "no")
CAPTION_MODEL = os.environ.get("CAPTION_MODEL", "claude-haiku-4-5")

# --- Respan evaluation pipelines (workspace-specific) ---
# The five deployed graders live in YOUR Respan workspace, so their ids can't be
# baked into the repo — they'd point at someone else's org. `/setup-respan`
# provisions them and writes these values into .env.
#
# These are pipeline **family** ids (`workflow_id`), not grader ids and NOT the
# `id` that list_evaluation_pipelines returns — that one is the primary key of a
# single *version*, so pinning it silently freezes the grader at the version it
# had when you copied it. Committing a new version mints a new PK, deploys fine,
# and every run keeps scoring with the old logic.
#
# `experiments.pipeline_versions()` resolves these families to whatever version
# is current at run time.
EVAL_PIPELINE_IDS = {k: v for k, v in {
    "context_relevance": os.environ.get("EVAL_PIPELINE_CONTEXT_RELEVANCE", ""),
    "context_completeness": os.environ.get("EVAL_PIPELINE_CONTEXT_COMPLETENESS", ""),
    "groundedness": os.environ.get("EVAL_PIPELINE_GROUNDEDNESS", ""),
    "context_utilization": os.environ.get("EVAL_PIPELINE_CONTEXT_UTILIZATION", ""),
    "citation_validity": os.environ.get("EVAL_PIPELINE_CITATION_VALIDITY", ""),
}.items() if v}

# All five present AND a key to call them with.
EXPERIMENTS_CONFIGURED = bool(RESPAN_API_KEY) and len(EVAL_PIPELINE_IDS) == 5

# --- conversation memory ---
# How many prior chat turns to replay into the generation call (6 = the last
# three exchanges). 0 disables memory and restores single-turn behaviour.
HISTORY_TURNS = int(os.environ.get("HISTORY_TURNS", "6"))
# Retrieval is embedding-based, so a bare follow-up ("explain that more simply")
# would pull semantically random chunks. This cheap model rewrites follow-ups
# into standalone search queries first. Only runs when there IS history.
REWRITE_MODEL = os.environ.get("REWRITE_MODEL", "claude-haiku-4-5")

# --- retrieval / chunking ---
# Source-diverse retrieval: pull TOP_K_PER_BOOK from each of the tutor's books,
# merge, then keep the best MAX_CONTEXT_CHUNKS overall. Guarantees each relevant
# book can be cited so the tutor can actually synthesize across sources.
#
# 8/14, not the original 3/10: the top-k sweep (scripts/topk_experiment.py) showed
# recall on Axler climbing 0.78 -> 0.94 going 3 -> 8, with generation graders flat.
# MAX raised to 14 so multi-book subjects aren't trimmed back below the per-book
# budget.
TOP_K_PER_BOOK = int(os.environ.get("TOP_K_PER_BOOK", "8"))
MAX_CONTEXT_CHUNKS = int(os.environ.get("MAX_CONTEXT_CHUNKS", "14"))

# Hybrid retrieval (RAG roadmap step 2): fuse dense vector search with BM25
# keyword search, per book, by Reciprocal Rank Fusion. Vector search blurs exact
# notation ("(T - λI)", theorem numbers, "injective") that a math book turns on;
# BM25 nails literal terms but misses paraphrase. RRF adds 1/(RRF_K + rank) from
# each ranked list, so a chunk ranked high by EITHER method surfaces. Each method
# contributes HYBRID_CANDIDATES before fusion, which is then cut to TOP_K_PER_BOOK.
# Off by default: flip it on and re-run scripts/retrieval_benchmark to measure the
# recall delta before committing, the same loop every other knob here went through.
HYBRID_SEARCH = os.environ.get("HYBRID_SEARCH", "off").lower() in ("on", "true", "1", "yes")
RRF_K = int(os.environ.get("RRF_K", "60"))                          # rank-fusion damping (60 is standard)
HYBRID_CANDIDATES = int(os.environ.get("HYBRID_CANDIDATES", "20"))  # pool per method before fusion

# Reranking (RAG roadmap step 3): a cross-encoder reorders a larger candidate
# pool before the TOP_K_PER_BOOK cut. The bi-encoder embeddings score query and
# chunk separately (fast, but blurry on which of two close chunks truly answers
# the question); a cross-encoder reads query+chunk together and is far better at
# that final ordering. So retrieve RERANK_CANDIDATES cheaply, then let the
# cross-encoder pick the top_n. Targets recall@1 / MRR, the measured weak spot.
# Local model, no API key, downloads once. Off by default: flip on, re-run
# scripts/rerank_experiment to measure before committing.
RERANK = os.environ.get("RERANK", "off").lower() in ("on", "true", "1", "yes")
# bge-reranker-base understands this technical prose; the lighter, faster
# ms-marco-MiniLM-L-6-v2 measured clearly worse on it (see evals/rerank_*.json).
# Both experiments found reranking net-neutral-to-negative at the current k=8, so
# this only matters if RERANK is switched on for a small-k or big-pool config.
RERANK_MODEL = os.environ.get("RERANK_MODEL", "BAAI/bge-reranker-base")
RERANK_CANDIDATES = int(os.environ.get("RERANK_CANDIDATES", "20"))  # pool fetched, then reranked down

# Lecture mode wants a continuous run of the book, not the best-matching
# fragments, so it pulls the chunks either side of each hit in reading order and
# allows a bigger budget. A window of 1 roughly triples the context; 2 is worth
# trying on books with short chunks.
LECTURE_NEIGHBOUR_WINDOW = int(os.environ.get("LECTURE_NEIGHBOUR_WINDOW", "1"))
LECTURE_MAX_CHUNKS = int(os.environ.get("LECTURE_MAX_CHUNKS", "18"))

# The study modes a question can be asked in. `solve` isn't here: it is implied
# by attaching an image, not chosen.
MODES = [
    {"id": "qa", "label": "Ask", "note": "answer the question"},
    {"id": "lecture", "label": "Lecture", "note": "teach the concept behind it"},
]
_MODE_IDS = {m["id"] for m in MODES}


def resolve_mode(requested: str | None) -> str:
    """A known mode, else plain Q&A. The value reaches prompt selection."""
    return requested if requested in _MODE_IDS else "qa"
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "150"))
