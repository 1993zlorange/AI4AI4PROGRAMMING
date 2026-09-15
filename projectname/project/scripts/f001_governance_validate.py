"""F001 项目治理校验器：只读检查功能登记、归属、命名和文档模板链路。"""

# 人类可读 CLI 文本保留中文；该例外不影响被检查项目文件。
# ruff: noqa: RUF001, RUF002, T201

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


CONFIG_PATTERN = re.compile(r"```project-supervision\s*\n(.*?)\n```", re.DOTALL)
DATE_DOCUMENT_PATTERN = re.compile(r"^\d{8}-.+-.+\.[A-Za-z0-9]+$")
FIXED_DOCUMENT_NAMES = {
    "AGENTS.md",
    "README.md",
    "PROGRAMMING_STANDARDS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "package.json",
    "SKILL.md",
    "openai.yaml",
    ".gitignore",
    ".editorconfig",
    ".env.example",
}
IGNORED_PARTS = {".git", ".venv", "node_modules", "__pycache__", "output"}


class GovernanceValidationError(ValueError):
    """表示项目治理配置或登记无法安全读取。"""


def parse_args() -> argparse.Namespace:
    """解析显式项目根；工具只读，保留 --check 作为统一入口。"""
    parser = argparse.ArgumentParser(description="F001 项目治理只读校验器")
    parser.add_argument("--project-root", type=Path, required=True, help="包含根级 AGENTS.md 的项目根")
    parser.add_argument("--check", action="store_true", help="执行只读检查")
    return parser.parse_args()


def load_project_config(project_root: Path) -> dict[str, object]:
    """从根级 AGENTS 读取 project-supervision TOML 配置。"""
    agents_path = project_root / "AGENTS.md"
    text = agents_path.read_text(encoding="utf-8")
    match = CONFIG_PATTERN.search(text)
    if match is None:
        raise GovernanceValidationError("根级 AGENTS.md 缺少 project-supervision 配置块")
    try:
        value = tomllib.loads(match.group(1))
    except tomllib.TOMLDecodeError as exc:
        raise GovernanceValidationError(f"project-supervision 配置无法解析：{exc}") from exc
    return value


def resolve_inside(root: Path, value: object, field_name: str) -> Path:
    """将配置相对路径解析并限制在项目根内。"""
    if not isinstance(value, str) or not value.strip():
        raise GovernanceValidationError(f"配置字段 {field_name} 缺失")
    candidate = Path(value)
    if candidate.is_absolute():
        raise GovernanceValidationError(f"配置字段 {field_name} 必须使用相对路径")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise GovernanceValidationError(f"配置字段 {field_name} 越出项目根") from exc
    return resolved


def load_json_file(path: Path, label: str) -> dict[str, Any]:
    """读取 JSON 兼容 YAML，避免引入 YAML 运行时依赖。"""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceValidationError(f"无法读取 {label}：{exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceValidationError(f"{label} 根节点必须是对象")
    return value


def is_within(root: Path, candidate: Path) -> bool:
    """返回候选路径是否位于根目录以内。"""
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def relative_paths(value: object, label: str, engineering_root: Path) -> tuple[list[Path], list[str]]:
    """验证工程相对路径列表并返回解析路径。"""
    if not isinstance(value, list) or not value:
        return [], [f"{label} 必须是非空路径数组"]
    paths: list[Path] = []
    errors: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label} 包含无效路径")
            continue
        path = Path(item)
        if path.is_absolute() or not is_within(engineering_root, engineering_root / path):
            errors.append(f"{label} 越出工程根：{item}")
            continue
        paths.append((engineering_root / path).resolve())
    return paths, errors


def validate_features(project_root: Path, config: dict[str, object]) -> tuple[list[str], Path]:
    """验证功能三元组、路径存在性和功能文件登记。"""
    engineering_root = resolve_inside(project_root, config.get("engineering_root"), "engineering_root")
    registry_path = resolve_inside(project_root, config.get("feature_registry"), "feature_registry")
    registry = load_json_file(registry_path, "功能登记")
    required = registry.get("required_fields")
    features = registry.get("features")
    if not isinstance(required, list) or not isinstance(features, list):
        return ["功能登记必须包含 required_fields 数组和 features 数组"], engineering_root
    id_pattern = re.compile(str(registry.get("feature_id_pattern", r"F\d{3}")))
    code_pattern = re.compile(str(registry.get("feature_code_pattern", r"[A-Z][A-Z0-9_]+")))
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    registered_files: set[Path] = set()
    errors: list[str] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            errors.append(f"features[{index}] 必须是对象")
            continue
        missing = [field for field in required if not feature.get(field)]
        if missing:
            errors.append(f"features[{index}] 缺少字段：{', '.join(str(item) for item in missing)}")
        feature_id = str(feature.get("feature_id", ""))
        feature_code = str(feature.get("feature_code", ""))
        if not id_pattern.fullmatch(feature_id):
            errors.append(f"features[{index}] feature_id 格式错误：{feature_id}")
        if not code_pattern.fullmatch(feature_code):
            errors.append(f"features[{index}] feature_code 格式错误：{feature_code}")
        if feature_id in seen_ids:
            errors.append(f"重复 feature_id：{feature_id}")
        if feature_code in seen_codes:
            errors.append(f"重复 feature_code：{feature_code}")
        seen_ids.add(feature_id)
        seen_codes.add(feature_code)
        implementation_paths, path_errors = relative_paths(
            feature.get("implementation_paths"), f"features[{index}].implementation_paths", engineering_root
        )
        test_paths, test_errors = relative_paths(
            feature.get("test_paths"), f"features[{index}].test_paths", engineering_root
        )
        errors.extend(path_errors + test_errors)
        for path in implementation_paths + test_paths:
            if not path.exists():
                errors.append(f"features[{index}] 登记路径不存在：{path.relative_to(engineering_root).as_posix()}")
            registered_files.add(path)
    extensions = {str(value) for value in registry.get("functional_extensions", [])}
    for root_name in ("apps", "packages", "scripts", "database"):
        source_root = engineering_root / root_name
        if not source_root.exists():
            continue
        for path in source_root.rglob("*"):
            if not path.is_file() or path.suffix not in extensions or any(part in IGNORED_PARTS for part in path.parts):
                continue
            if path.resolve() not in registered_files:
                errors.append(f"功能性文件未登记功能三元组：{path.relative_to(engineering_root).as_posix()}")
    return errors, engineering_root


def validate_layout(project_root: Path, config: dict[str, object], engineering_root: Path) -> list[str]:
    """检查工程顶层目录允许列表和必要治理资产。"""
    errors: list[str] = []
    registry_path = resolve_inside(project_root, config.get("feature_registry"), "feature_registry")
    registry = load_json_file(registry_path, "功能登记")
    allowed = registry.get("allowed_engineering_top_level")
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        return ["功能登记缺少 allowed_engineering_top_level 字符串数组"]
    allowed_names = set(allowed)
    for child in engineering_root.iterdir():
        if child.is_dir() and child.name not in allowed_names and not child.name.startswith("."):
            errors.append(f"未登记工程顶层目录：{child.name}")
    for field_name in (
        "project_management_root",
        "scripts_root",
        "release_root",
        "skill_promotion_registry",
    ):
        path = resolve_inside(project_root, config.get(field_name), field_name)
        if not path.exists():
            errors.append(f"配置目标不存在：{field_name} -> {path.relative_to(project_root).as_posix()}")
    return errors


def validate_documents(project_root: Path, config: dict[str, object]) -> list[str]:
    """检查项目级文档命名和文档型 Skill 的模板链路。"""
    errors: list[str] = []
    management_root = resolve_inside(project_root, config.get("project_management_root"), "project_management_root")
    templates_root = resolve_inside(management_root, config.get("templates_dir"), "templates_dir")
    skills_root = resolve_inside(project_root, config.get("project_skills_root"), "project_skills_root")
    if not templates_root.exists():
        errors.append("项目管理模板目录不存在")
    if skills_root.exists():
        for skill_file in skills_root.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            if "## 文档输出" not in content:
                continue
            assets = skill_file.parent / "assets"
            if not assets.is_dir() or not any(assets.iterdir()):
                errors.append(f"文档型项目 Skill 缺少 assets 模板：{skill_file.relative_to(project_root).as_posix()}")
            if "assets/" not in content:
                errors.append(f"文档型项目 Skill 未引用模板路径：{skill_file.relative_to(project_root).as_posix()}")
    for path in management_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".html"}:
            continue
        if path.name in FIXED_DOCUMENT_NAMES or path.parent == templates_root:
            continue
        if not DATE_DOCUMENT_PATTERN.fullmatch(path.name):
            errors.append(f"项目管理文档未采用日期化命名：{path.relative_to(project_root).as_posix()}")
    return errors


def run(project_root: Path) -> int:
    """执行只读治理检查并返回稳定退出码。"""
    try:
        config = load_project_config(project_root)
        feature_errors, engineering_root = validate_features(project_root, config)
        errors = feature_errors + validate_layout(project_root, config, engineering_root) + validate_documents(project_root, config)
    except (GovernanceValidationError, OSError) as exc:
        errors = [str(exc)]
    for message in errors:
        print(f"ERROR: {message}")
    print(f"F001 治理校验完成：ERROR={len(errors)}")
    return 1 if errors else 0


def main() -> int:
    """解析参数并执行检查。"""
    args = parse_args()
    root = args.project_root.resolve()
    if not root.is_dir():
        print(f"ERROR: 项目根不存在：{root}")
        return 2
    return run(root)


if __name__ == "__main__":
    raise SystemExit(main())
