"""F001 的最小回归测试。"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ENGINEERING_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ENGINEERING_ROOT.parents[1]
MODULE_PATH = ENGINEERING_ROOT / "scripts" / "f001_governance_validate.py"


def load_module() -> object:
    """从工程脚本目录加载待测模块。"""
    specification = importlib.util.spec_from_file_location("f001_governance_validate", MODULE_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("无法加载 F001")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class GovernanceValidationTests(unittest.TestCase):
    """验证当前模板的治理资产能通过只读校验。"""

    def test_current_template_passes(self) -> None:
        """当前模板配置、功能登记和已登记治理脚本保持一致。"""
        module = load_module()
        self.assertEqual(module.run(PROJECT_ROOT), 0)


if __name__ == "__main__":
    unittest.main()
