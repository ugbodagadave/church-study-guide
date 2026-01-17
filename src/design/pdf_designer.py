import os
from typing import Tuple, Dict, Any, List
from fpdf import FPDF
from PIL import Image
import math
from src.utils.logger import setup_logger

logger = setup_logger("pdf_designer")

class PDFDesigner(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.primary_color = (0, 0, 0) # Default Black
        self.secondary_color = (100, 100, 100) # Default Grey
        self.accent_color = (50, 50, 50) # Dark Grey
        self.set_auto_page_break(auto=True, margin=15)
        self.series_title = ""

    def extract_colors_from_logo(self, logo_path: str):
        """
        Extracts dominant colors from a logo file.
        Falls back to B&W if fails or path invalid.
        """
        if not logo_path or not os.path.exists(logo_path):
            logger.warning(f"Logo not found at {logo_path}. Using fallback colors.")
            return

        try:
            img = Image.open(logo_path)
            img = img.resize((150, 150))
            result = img.convert('P', palette=Image.ADAPTIVE, colors=3)
            result = result.convert('RGB')
            
            # Get most frequent colors
            colors = result.getcolors(150*150)
            colors.sort(key=lambda x: x[0], reverse=True)
            
            # Simple heuristic: Pick top non-white colors
            extracted = []
            for count, col in colors:
                # Skip near-whites and near-transparent
                if sum(col) > 700: # 255*3 = 765
                    continue
                extracted.append(col)
                if len(extracted) >= 2:
                    break
            
            if extracted:
                self.primary_color = extracted[0]
                if len(extracted) > 1:
                    self.accent_color = extracted[1]
                logger.info(f"Extracted colors: Primary={self.primary_color}, Accent={self.accent_color}")
            else:
                logger.warning("Could not extract suitable colors from logo. Using fallback.")

        except Exception as e:
            logger.error(f"Error extracting colors: {e}. Using fallback.")

    def header(self):
        # Header on all pages except cover (handled separately or logic here)
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(*self.secondary_color)
            self.cell(0, 10, f'{self.series_title} - Discipleship Guide', 0, 0, 'R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def create_pdf(self, content: Dict[str, Any], output_path: str, logo_path: str = None):
        """
        Generates the PDF based on content dictionary.
        """
        self.series_title = content.get("series_title", "Study Guide")
        self.extract_colors_from_logo(logo_path)
        
        # --- Cover Page ---
        self.add_page()
        self._create_cover_page(content, logo_path)
        
        # --- Daily Guides ---
        for day_data in content.get("days", []):
            self.add_page()
            self._create_day_page(day_data)
            
        # --- Save ---
        try:
            self.output(output_path)
            logger.info(f"PDF generated successfully at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save PDF: {e}")
            raise

    def _create_cover_page(self, content: Dict[str, Any], logo_path: str = None):
        # Logo
        if logo_path and os.path.exists(logo_path):
            try:
                # Center logo
                self.image(logo_path, x=75, y=30, w=60)
                self.ln(80)
            except Exception as e:
                logger.warning(f"Could not add logo image: {e}")
                self.ln(50)
        else:
            self.ln(50)

        # Title
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*self.primary_color)
        self.multi_cell(0, 10, content.get("series_title", "Sermon Series").upper(), align='C')
        self.ln(10)
        
        # Subtitle
        self.set_font('Helvetica', '', 14)
        self.set_text_color(*self.accent_color)
        self.cell(0, 10, "Discipleship & Study Guide", 0, 1, 'C')
        self.ln(20)
        
        # Memory Verse Box
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(*self.primary_color)
        self.rect(20, self.get_y(), 170, 40, 'DF')
        
        self.set_xy(25, self.get_y() + 5)
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, "MEMORY VERSE", 0, 1, 'L')
        
        self.set_x(25)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(160, 6, content.get("memory_verse", ""), align='L')
        
        # Key Quotes
        self.ln(30)
        if "key_quotes" in content:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(*self.primary_color)
            self.cell(0, 10, "KEY QUOTES", 0, 1, 'C')
            self.ln(5)
            
            self.set_font('Helvetica', '', 10)
            self.set_text_color(0, 0, 0)
            for quote in content["key_quotes"]:
                self.multi_cell(0, 6, f'"{quote}"', align='C')
                self.ln(4)

    def _create_day_page(self, day_data: Dict[str, Any]):
        # Day Header
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, f"DAY {day_data.get('day', '?')}: {day_data.get('title', '').upper()}", 0, 1, 'L')
        
        # Scripture
        self.ln(5)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "SCRIPTURE READING", 0, 1)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('scripture', ''))
        
        # Reflection
        self.ln(8)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "REFLECTION", 0, 1)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('reflection', ''))
        
        # Questions
        self.ln(8)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "APPLICATION QUESTIONS", 0, 1)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        
        questions = day_data.get('questions', [])
        for i, q in enumerate(questions, 1):
            self.multi_cell(0, 6, f"{i}. {q}")
            self.ln(2)
            
        # Prayer
        self.ln(5)
        self.set_fill_color(240, 240, 240) # Light grey bg
        self.rect(self.get_x(), self.get_y(), 190, 25, 'F')
        
        self.set_xy(self.get_x() + 2, self.get_y() + 2)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "PRAYER", 0, 1)
        
        self.set_x(self.get_x() + 2)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(185, 6, day_data.get('prayer', ''))
