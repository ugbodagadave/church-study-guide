import os
from src.design.pdf_designer import PDFDesigner


class TestPDFDesigner:
    def test_init_uses_static_palette(self):
        designer = PDFDesigner()
        assert designer.primary_color == (24, 37, 72)
        assert designer.accent_color == (211, 83, 121)

    def test_create_pdf_structure(self, tmp_path):
        designer = PDFDesigner()

        content = {
            "series_title": "Test Series",
            "preacher_name": "Test Preacher",
            "memory_verse": "Test Verse",
            "key_quotes": ["Quote 1", "Quote 2"],
            "days": [
                {
                    "day": 1,
                    "title": "Day 1 Title",
                    "scripture": "Gen 1:1",
                    "reflection": "Reflection text.",
                    "questions": ["Q1", "Q2"],
                    "prayer": "Amen.",
                }
            ],
        }

        output_file = tmp_path / "test_guide.pdf"

        path = designer.create_pdf(content, str(output_file))

        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
