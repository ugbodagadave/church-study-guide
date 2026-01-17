import pytest
import os
from unittest.mock import patch, MagicMock
from src.design.pdf_designer import PDFDesigner

class TestPDFDesigner:
    
    def test_init(self):
        designer = PDFDesigner()
        assert designer.primary_color == (0, 0, 0)
        
    def test_extract_colors_no_logo(self):
        designer = PDFDesigner()
        designer.extract_colors_from_logo(None)
        # Should remain default
        assert designer.primary_color == (0, 0, 0)
        
    @patch('src.design.pdf_designer.Image')
    def test_extract_colors_success(self, mock_image, tmp_path):
        # Create a dummy logo file
        logo_path = tmp_path / "logo.png"
        logo_path.write_text("fake image data")
        
        # Mock Image.open and processing chain
        mock_img_instance = MagicMock()
        mock_image.open.return_value = mock_img_instance
        
        # Mock conversion result
        mock_converted = MagicMock()
        mock_img_instance.resize.return_value.convert.return_value.convert.return_value = mock_converted
        
        # Mock getcolors return: (count, (R,G,B))
        # Return a bright red
        mock_converted.getcolors.return_value = [(100, (255, 0, 0)), (50, (0, 255, 0))]
        
        designer = PDFDesigner()
        designer.extract_colors_from_logo(str(logo_path))
        
        assert designer.primary_color == (255, 0, 0)
        assert designer.accent_color == (0, 255, 0)

    def test_create_pdf_structure(self, tmp_path):
        """
        Tests the PDF generation logic without verifying visual output.
        We check if the file is created.
        """
        designer = PDFDesigner()
        
        content = {
            "series_title": "Test Series",
            "memory_verse": "Test Verse",
            "key_quotes": ["Quote 1", "Quote 2"],
            "days": [
                {
                    "day": 1,
                    "title": "Day 1 Title",
                    "scripture": "Gen 1:1",
                    "reflection": "Reflection text.",
                    "questions": ["Q1", "Q2"],
                    "prayer": "Amen."
                }
            ]
        }
        
        output_file = tmp_path / "test_guide.pdf"
        
        # We need to ensure FPDF doesn't fail on font loading or other env issues
        # Standard Helvetica is built-in, so it should be fine.
        
        path = designer.create_pdf(content, str(output_file))
        
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
