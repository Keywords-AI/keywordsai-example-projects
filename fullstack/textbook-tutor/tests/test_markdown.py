"""Markdown rendering (`frontend/js/markdown.js`), exercised through Node.

Solve-mode answers lean on tables, italics, blockquotes and rules constantly,
and all four used to render as raw source in the chat. These run the real module
rather than a Python re-implementation, so they can't drift from it.
"""
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

JS_DIR = Path(__file__).resolve().parent.parent / "frontend" / "js"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")


def render(md: str) -> str:
    """Run mdToHtml on a string via node, with a KaTeX stub for the math path."""
    script = textwrap.dedent(f"""
        globalThis.katex = {{ renderToString: (t) => '<span class="katex">' + t + '</span>' }};
        const {{ mdToHtml }} = await import({json.dumps(str(JS_DIR / 'markdown.js'))});
        process.stdout.write(mdToHtml({json.dumps(md)}));
    """)
    out = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=60,
    )
    assert out.returncode == 0, out.stderr
    return out.stdout


# --- tables ---

def test_table_renders_as_a_table():
    html = render("| Part | Answer |\n|------|--------|\n| (a) | ATP |\n| (b) | Thylakoid |")
    assert "<table>" in html and "<th>Part</th>" in html
    assert "<td>ATP</td>" in html and "<td>Thylakoid</td>" in html
    assert "|" not in html, "raw pipes leaked into the output"


def test_table_is_wrapped_so_it_can_scroll():
    # A wide table must not stretch the thread layout.
    assert 'class="tablewrap"' in render("| a | b |\n|---|---|\n| 1 | 2 |")


def test_ragged_row_does_not_lose_columns():
    html = render("| a | b |\n|---|---|\n| 1 |")
    assert html.count("<td>") == 2


def test_pipes_without_a_rule_row_are_not_a_table():
    assert "<table>" not in render("this | that | other")


def test_inline_formatting_works_inside_cells():
    html = render("| x | y |\n|---|---|\n| **bold** | `code` |")
    assert "<strong>bold</strong>" in html and "<code>code</code>" in html


# --- italics vs bold ---

def test_italics_render():
    assert "<em>Teaching point:</em>" in render("*Teaching point:* something")


def test_bold_is_not_eaten_by_the_italic_pass():
    html = render("**ATP and NADPH** are produced")
    assert "<strong>ATP and NADPH</strong>" in html
    assert "<em>" not in html


def test_bold_and_italic_together():
    html = render("**bold** then *ital*")
    assert "<strong>bold</strong>" in html and "<em>ital</em>" in html


# --- blockquotes and rules ---

def test_blockquote_renders():
    html = render('> "water is split in a step called photolysis"')
    assert "<blockquote>" in html and "photolysis" in html


def test_consecutive_quote_lines_are_one_blockquote():
    html = render("> line one\n> line two")
    assert html.count("<blockquote>") == 1
    assert html.count("<p>") == 2


def test_horizontal_rule():
    assert "<hr>" in render("above\n\n---\n\nbelow")


def test_list_dash_is_not_mistaken_for_a_rule():
    html = render("- a bullet\n- another")
    assert "<hr>" not in html and html.count("<li>") == 2


# --- regressions on what already worked ---

def test_headings_lists_and_citations_still_work():
    html = render("## Heading\n\n- one\n- two\n\nSee [Campbell, p. 1].")
    assert "<h3>Heading</h3>" in html
    assert html.count("<li>") == 2
    assert 'class="cite"' in html


def test_html_in_source_is_escaped():
    assert "<script>" not in render("<script>alert(1)</script>")


def test_math_is_typeset_not_escaped():
    assert 'class="katex"' in render("The equation $E=mc^2$ holds.")
