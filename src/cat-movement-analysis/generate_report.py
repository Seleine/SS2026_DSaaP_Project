import base64
import os
from pathlib import Path
import webbrowser


def _embed_png(path: str) -> str:
    """Return an <img> tag with the PNG embedded as base64."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    filename = Path(path).name
    return (
        f"<figure>"
        f'<img src="data:image/png;base64,{data}" alt="{filename}">'
        f"<figcaption>{filename}</figcaption>"
        f"</figure>"
    )


def _embed_html(path: str) -> str:
    """Return an <iframe> with the HTML file's content inlined via srcdoc."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Escape quotes so the srcdoc attribute stays valid
    escaped = content.replace("&", "&amp;").replace('"', "&quot;")
    filename = Path(path).name
    return (
        f"<figure>"
        f'<iframe srcdoc="{escaped}" '
        f'title="{filename}" '
        f'style="width:100%; height:520px; border:none; border-radius:6px;">'
        f"</iframe>"
        f"<figcaption>{filename}</figcaption>"
        f"</figure>"
    )


def _render_section(section: dict, base_dir: str) -> str:
    """Recursively render one section (heading + content + subsections)."""
    level = max(1, min(section.get("level", 2), 6))
    title = section.get("title", "")
    content_files = section.get("content", [])
    subsections = section.get("subsections", [])
    text = section.get("text", "")

    html_parts = [f"<h{level}>{title}</h{level}>"]

    if text:
        html_parts.append(f"<p>{text}</p>")

    for filepath in content_files:
        full_path = os.path.join(base_dir, filepath)
        if not os.path.exists(full_path):
            html_parts.append(
                f'<p class="missing">File not found: <code>{filepath}</code></p>'
            )
            continue

        ext = Path(filepath).suffix.lower()
        if ext == ".png":
            html_parts.append(_embed_png(full_path))
        elif ext == ".html":
            html_parts.append(_embed_html(full_path))
        else:
            html_parts.append(
                f'<p class="missing">Unsupported file type: <code>{filepath}</code></p>'
            )

    for sub in subsections:
        html_parts.append(_render_section(sub, base_dir))

    return "\n".join(html_parts)


def generate_report(
    structure: list[dict],
    output_path: str = "report.html",
    base_dir: str = ".",
    report_title: str = "Report",
) -> str:
    """
    Generate a self-contained HTML report.

    Parameters
    ----------
    structure   : list of section dicts (see module docstring).
    output_path : where to write the finished HTML file.
    base_dir    : root directory used to resolve relative file paths.
    report_title: text shown in the browser tab and the top <h1>.

    Returns
    -------
    The absolute path to the generated file.
    """
    body_parts = []
    for section in structure:
        body_parts.append(_render_section(section, base_dir))

    body_html = "\n".join(body_parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{report_title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f6fa;
      color: #1a1a2e;
      padding: 2rem 1rem;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
    }}

    h1 {{ font-size: 2rem;   margin: 2rem 0 1rem;   border-bottom: 3px solid #4f6ef7; padding-bottom: .4rem; }}
    h2 {{ font-size: 1.5rem; margin: 1.8rem 0 .8rem; border-bottom: 2px solid #dde1f0; padding-bottom: .3rem; }}
    h3 {{ font-size: 1.15rem; margin: 1.4rem 0 .6rem; color: #4f6ef7; }}
    h4, h5, h6 {{ font-size: 1rem; margin: 1rem 0 .5rem; }}

    figure {{
      background: #ffffff;
      border: 1px solid #dde1f0;
      border-radius: 8px;
      padding: 1rem;
      margin: 1rem 0;
      box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }}

    figure img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
      border-radius: 4px;
    }}

    figcaption {{
      text-align: center;
      margin-top: .5rem;
      font-size: .8rem;
      color: #6b7280;
      font-family: monospace;
    }}

    p.missing {{
      background: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 6px;
      padding: .6rem 1rem;
      margin: .5rem 0;
      font-size: .9rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{report_title}</h1>
    {body_html}
  </div>
</body>
</html>"""

    if not os.path.exists("./report"):
        os.mkdir("./report")

    out = Path("./report/report.html")
    out.write_text(html, encoding="utf-8")
    webbrowser.open(f"file://{out.resolve()}")
    return str(out.resolve())
