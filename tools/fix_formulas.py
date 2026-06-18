#!/usr/bin/env python3
"""
Markdown 公式预处理器：将围栏代码块公式转为 LaTeX $$ display math。
行内 Unicode 数学符号保持不变（现代 Word 字体可正常渲染）。

用法：
  python fix_formulas.py -i input.md -o output.md
  然后：pandoc output.md -o output.docx --from markdown+tex_math_dollars
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── Unicode → LaTeX 映射 ─────────────────────────────────────────────

UNICODE_TO_LATEX: list[tuple[str, str]] = [
    ("ν̇", r"\dot{\nu}"), ("ν̈", r"\ddot{\nu}"),
    ("x̂", r"\hat{x}"), ("X̂", r"\hat{X}"), ("x̄", r"\bar{x}"),
    ("α", r"\alpha "), ("β", r"\beta "), ("γ", r"\gamma "), ("δ", r"\delta "),
    ("ε", r"\epsilon "), ("ζ", r"\zeta "), ("η", r"\eta "), ("θ", r"\theta "),
    ("ι", r"\iota "), ("κ", r"\kappa "), ("λ", r"\lambda "), ("μ", r"\mu "),
    ("ν", r"\nu "), ("ξ", r"\xi "), ("π", r"\pi "), ("ρ", r"\rho "),
    ("σ", r"\sigma "), ("τ", r"\tau "), ("υ", r"\upsilon "), ("φ", r"\phi "),
    ("χ", r"\chi "), ("ψ", r"\psi "), ("ω", r"\omega "),
    ("Γ", r"\Gamma "), ("Δ", r"\Delta "), ("Θ", r"\Theta "), ("Λ", r"\Lambda "),
    ("Σ", r"\Sigma "), ("Φ", r"\Phi "), ("Ψ", r"\Psi "), ("Ω", r"\Omega "),
    ("∆", r"\Delta "),  # U+2206 INCREMENT (常被用作 Delta 的数学变体)
    ("⁻¹", r"^{-1}"), ("⁻²", r"^{-2}"), ("⁻³", r"^{-3}"), ("⁻ᵀ", r"^{-T}"),
    ("⁰", "^{0}"), ("¹", "^{1}"), ("²", "^{2}"), ("³", "^{3}"),
    ("⁴", "^{4}"), ("⁵", "^{5}"), ("⁶", "^{6}"), ("⁷", "^{7}"),
    ("⁸", "^{8}"), ("⁹", "^{9}"),
    ("⁺", "^{+}"), ("⁻", "^{-}"), ("ᵀ", "^{T}"),
    ("₀", "_{0}"), ("₁", "_{1}"), ("₂", "_{2}"), ("₃", "_{3}"),
    ("₄", "_{4}"), ("₅", "_{5}"), ("₆", "_{6}"), ("₇", "_{7}"),
    ("₈", "_{8}"), ("₉", "_{9}"),
    ("ₓ", "_{x}"), ("ₚ", "_{P}"), ("ₑ", "_{E}"), ("ₖ", "_{k}"),
    ("ₙ", "_{n}"), ("ₐ", "_{a}"), ("ₒ", "_{o}"),
    ("ₘₐₓ", r"_{\text{max}}"), ("ₘᵢₙ", r"_{\text{min}}"),
    ("·", r"\cdot "), ("×", r"\times "), ("±", r"\pm "),
    ("∂", r"\partial "), ("∫", r"\int "), ("∑", r"\sum "), ("∞", r"\infty "),
    ("≠", r"\neq "), ("≤", r"\leq "), ("≥", r"\geq "),
    ("≈", r"\approx "), ("≡", r"\equiv "),
    ("→", r"\rightarrow "), ("←", r"\leftarrow "), ("⇒", r"\Rightarrow "),
    ("⟨", r"\langle "), ("⟩", r"\rangle "),
    ("∈", r"\in "), ("∀", r"\forall "), ("∃", r"\exists "),
    ("ℝ", r"\mathbb{R}"),
    ("…", r"\dots "), ("⋯", r"\cdots "),
    ("°", r"^{\circ}"),
]


def _unicode_to_latex(text: str) -> str:
    result = text
    for uni, latex in UNICODE_TO_LATEX:
        result = result.replace(uni, latex)
    return result


def _has_math_content(text: str) -> bool:
    """检测文本是否包含足够的数学内容。"""
    math_chars = sum(1 for uni, _ in UNICODE_TO_LATEX if uni in text)
    if math_chars >= 1:
        return True
    math_patterns = len(re.findall(
        r'[_^][a-zA-Z0-9]|\\[a-zA-Z]+|[=+\-*/]|\b[a-zA-Z]_[a-zA-Z]',
        text
    ))
    return math_patterns >= 3


def process_markdown(text: str) -> str:
    """将围栏代码块公式转为 $$ display math。"""
    lines = text.splitlines()
    result_lines: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            start = i
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith("```"):
                    code_lines = lines[start + 1 : i]
                    code_content = "\n".join(code_lines)

                    if _has_math_content(code_content) or lang in ("math", "equation"):
                        latex_content = _unicode_to_latex(code_content)
                        result_lines.append("$$")
                        result_lines.append(latex_content)
                        result_lines.append("$$")
                    else:
                        result_lines.append("```")
                        result_lines.extend(code_lines)
                        result_lines.append("```")
                    i += 1
                    break
                i += 1
        else:
            result_lines.append(lines[i])
            i += 1

    return "\n".join(result_lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Markdown 围栏代码块公式 → LaTeX $$ display math"
    )
    p.add_argument("-i", "--input", required=True, help="输入 .md 路径")
    p.add_argument("-o", "--output", required=True, help="输出 .md 路径")
    args = p.parse_args(argv)

    in_path = Path(args.input).resolve()
    if not in_path.is_file():
        print(f"错误：找不到 {in_path}", file=sys.stderr)
        return 1

    text = in_path.read_text(encoding="utf-8")
    result = process_markdown(text)

    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")
    print(f"已写入: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
