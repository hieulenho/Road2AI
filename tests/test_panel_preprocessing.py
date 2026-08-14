from __future__ import annotations

import unittest

from road2ai_vifinqa.build_panel import (
    _classify,
    _find_code,
    _is_current_period_source,
    _numeric_values,
)
from road2ai_vifinqa.table_semantics import TableAnalyzer


class PanelPreprocessingTest(unittest.TestCase):
    def test_finds_consistent_code_column_after_ordinal(self) -> None:
        rows = [
            ["STT", "Mã", "Chỉ tiêu", "2024", "2023"],
            ["1", "01", "Doanh thu bán hàng", "1.000", "900"],
            ["2", "11", "Giá vốn hàng bán", "700", "600"],
            ["3", "20", "Lợi nhuận gộp", "300", "300"],
            ["4", "25", "Chi phí bán hàng", "50", "40"],
            ["5", "26", "Chi phí quản lý", "30", "20"],
        ]
        result = _classify(rows, "BÁO CÁO KẾT QUẢ HOẠT ĐỘNG KINH DOANH")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.kind, "kqkd")
        self.assertEqual(result.code_col, 1)
        self.assertEqual(_find_code(rows[1], code_col=result.code_col), (1, "01"))

    def test_numeric_values_skip_codes_years_and_small_ordinals(self) -> None:
        row = ["1", "01", "Doanh thu", "2024", "1.234.567"]
        self.assertEqual(_numeric_values(row, 1), [(4, 1234567.0, "1.234.567")])

    def test_rejects_prior_year_cell_when_current_value_is_blank(self) -> None:
        rows = [
            ["Chỉ tiêu", "2024", "2023"],
            ["Doanh thu", "", "1.000"],
        ]
        semantics = TableAnalyzer(rows, report_year=2024).cell(1, 2)
        self.assertFalse(_is_current_period_source(semantics, 2024))


if __name__ == "__main__":
    unittest.main()
