"""F002 Skill 晋升审计器：只读检查项目试点到全局晋升的证据链。"""

# 人类可读 CLI 文本保留中文；该例外不影响被检查项目文件。
# ruff: noqa: RUF001, RUF002, T201

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path
from typing import Any


CONFIG_PATTERN = re.compile(r"```project-supervision\s*\n(.*?)\n```", re.DOTALL)


class PromotionAuditError(ValueError):
    """表示 Skill 晋升登记或项目配置不满足审查条件。"""


def parse_args() -> argparse.Namespace:
    """解析显式项目根；工具不安装、不复制和不修改任何 Skill。"""
    parser = argparse.ArgumentParser(description="F002 Skill 晋升只读审计器")
    parser.add_argument("--project-root", type=Path, required=True, help="包含根级 AGENTS.md 的项目根")
    parser.add_argument("--check", action="store_true", help="执行只读审计")
    return parser.parse_args()


def load_project_config(project_root: Path) -> dict[str, object]:
    """读取根级 project-supervision 配置。"""
    text = (project_root / "AGENTS.md").read_text(encoding="utf-8")
    match = CONFIG_PATTERN.search(text)
    if match is None:
        raise PromotionAuditError("根级 AGENTS.md 缺少 project-supervision 配置块")
    try:
        return tomllib.loads(match.group(1))
    except tomllib.TOMLDecodeError as exc:
        raise PromotionAuditError(f"project-supervision 配置无法解析：{exc}") from exc


def resolve_inside(root: Path, value: object, field_name: str) -> Path:
    """解析配置相对路径且禁止越界。"""
    if not isinstance(value, str) or not value.strip():
        raise PromotionAuditError(f"配置字段 {field_name} 缺失")
    relative = Path(value)
    if relative.is_absolute():
        raise PromotionAuditError(f"配置字段 {field_name} 必须为相对路径")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PromotionAuditError(f"配置字段 {field_name} 越出项目根") from exc
    return resolved


def load_json_file(path: Path) -> dict[str, Any]:
    """读取 JSON 兼容 YAML 登记。"""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionAuditError(f"无法读取 Skill 晋升登记：{exc}") from exc
    if not isinstance(value, dict):
        raise PromotionAuditError("Skill 晋升登记根节点必须是对象")
    return value


def resolve_reference(project_root: Path, value: object, field: str) -> tuple[Path | None, str | None]:
    """将证据引用定位为项目根以内的文件或目录，允许 Markdown 锚点。"""
    if not isinstance(value, str) or not value.strip():
        return None, f"{field} 缺失"
    path_text = value.split("#", 1)[0]
    path = Path(path_text)
    if path.is_absolute():
        return None, f"{field} 不得使用绝对路径"
    resolved = (project_root / path).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError:
        return None, f"{field} 越出项目根"
    if not resolved.exists():
        return None, f"{field} 不存在：{path_text}"
    return resolved, None


def sha256_tree(path: Path) -> str:
    """计算 Skill 文件树的稳定哈希，忽略目录元数据。"""
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if not item.is_file() or "__pycache__" in item.parts:
            continue
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest().upper()


def validate_project_skill(skill_path: Path, expected_name: str) -> list[str]:
    """验证项目 Skill 入口、名称和文档模板约定。"""
    errors: list[str] = []
    skill_file = skill_path / "SKILL.md"
    if not skill_file.is_file():
        return [f"项目 Skill 缺少 SKILL.md：{skill_path}"]
    content = skill_file.read_text(encoding="utf-8")
    if f"name: {expected_name}" not in content:
        errors.append(f"项目 Skill 名称与登记不一致：{expected_name}")
    if "## 文档输出" in content:
        assets = skill_path / "assets"
        if not assets.is_dir() or not any(assets.iterdir()):
            errors.append(f"文档型项目 Skill 缺少中文模板：{skill_path}")
        if "assets/" not in content:
            errors.append(f"文档型项目 Skill 未声明模板路径：{skill_path}")
    return errors


def run(project_root: Path) -> int:
    """审计所有待晋升或已晋升条目，绝不执行全局安装。"""
    try:
        config = load_project_config(project_root)
        registry_path = resolve_inside(project_root, config.get("skill_promotion_registry"), "skill_promotion_registry")
        registry = load_json_file(registry_path)
        required = registry.get("required_evidence")
        promotions = registry.get("promotions")
        if not isinstance(required, list) or not isinstance(promotions, list):
            raise PromotionAuditError("required_evidence 和 promotions 必须是数组")
        errors: list[str] = []
        for index, item in enumerate(promotions):
            if not isinstance(item, dict):
                errors.append(f"promotions[{index}] 必须是对象")
                continue
            missing = [str(field) for field in required if not item.get(field)]
            if missing:
                errors.append(f"promotions[{index}] 缺少证据：{', '.join(missing)}")
                continue
            skill_name = str(item.get("skill_name", ""))
            skill_path, path_error = resolve_reference(project_root, item.get("project_skill"), "project_skill")
            if path_error:
                errors.append(f"promotions[{index}] {path_error}")
                continue
            errors.extend(f"promotions[{index}] {message}" for message in validate_project_skill(skill_path, skill_name))
            expected_hash = str(item.get("package_sha256", "")).upper()
            if expected_hash and sha256_tree(skill_path) != expected_hash:
                errors.append(f"promotions[{index}] 项目 Skill 哈希不匹配")
            for field in required:
                _, reference_error = resolve_reference(project_root, item.get(field), str(field))
                if reference_error:
                    errors.append(f"promotions[{index}] {reference_error}")
        if not promotions:
            print("INFO: 当前没有待晋升 Skill；保持项目级试点，不执行全局安装。")
    except (PromotionAuditError, OSError) as exc:
        errors = [str(exc)]
    for message in errors:
        print(f"ERROR: {message}")
    print(f"F002 Skill 晋升审计完成：ERROR={len(errors)}，全局安装=未执行")
    return 1 if errors else 0


def main() -> int:
    """解析参数并运行审计。"""
    args = parse_args()
    root = args.project_root.resolve()
    if not root.is_dir():
        print(f"ERROR: 项目根不存在：{root}")
        return 2
    return run(root)


if __name__ == "__main__":
    raise SystemExit(main())
