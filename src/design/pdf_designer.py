import os
from typing import Tuple, Dict, Any, List
from fpdf import FPDF
from fpdf.enums import XPos, YPos
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
        
        # Load Montserrat Fonts
        font_dir = os.path.join("assets", "fonts")
        if os.path.exists(font_dir):
            try:
                self.add_font("Montserrat", style="", fname=os.path.join(font_dir, "Montserrat-Regular.ttf"))
                self.add_font("Montserrat", style="B", fname=os.path.join(font_dir, "Montserrat-Bold.ttf"))
                self.add_font("Montserrat", style="I", fname=os.path.join(font_dir, "Montserrat-Italic.ttf"))
                logger.info("Montserrat fonts loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load fonts: {e}. Fallback to Helvetica.")
        else:
            logger.warning("Font directory not found. Fallback to Helvetica.")

    def _set_font(self, style='', size=11):
        try:
            self.set_font("Montserrat", style, size)
        except Exception:
            self.set_font("Helvetica", style, size)

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
            self._set_font('I', 8)
            self.set_text_color(*self.secondary_color)
            self.cell(0, 10, f'{self.series_title} - Discipleship Guide', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self._set_font('I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

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
        self._set_font('B', 24)
        self.set_text_color(*self.primary_color)
        self.multi_cell(0, 10, content.get("series_title", "Sermon Series").upper(), align='C')
        self.ln(10)
        
        # Subtitle
        self._set_font('', 14)
        self.set_text_color(*self.accent_color)
        self.cell(0, 10, "Discipleship & Study Guide", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Preacher Name
        if "preacher_name" in content and content["preacher_name"]:
            self._set_font('I', 12)
            self.cell(0, 8, f"By {content['preacher_name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.ln(20)
        
        # Memory Verse Box
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(*self.primary_color)
        self.rect(20, self.get_y(), 170, 40, 'DF')
        
        self.set_xy(25, self.get_y() + 5)
        self._set_font('B', 12)
        self.cell(0, 10, "MEMORY VERSE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        
        self.set_x(25)
        self._set_font('I', 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(160, 6, content.get("memory_verse", ""), align='L')
        
        # Key Quotes
        self.ln(30)
        if "key_quotes" in content:
            self._set_font('B', 12)
            self.set_text_color(*self.primary_color)
            self.cell(0, 10, "KEY QUOTES", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            self.ln(5)
            
            self._set_font('', 10)
            self.set_text_color(0, 0, 0)
            for quote in content["key_quotes"]:
                self.multi_cell(0, 6, f'"{quote}"', align='C')
                self.ln(4)

    def _create_day_page(self, day_data: Dict[str, Any]):
        # Day Header
        self._set_font('B', 16)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, f"DAY {day_data.get('day', '?')}: {day_data.get('title', '').upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        
        # Scripture
        self.ln(5)
        self._set_font('B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "SCRIPTURE READING", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('scripture', ''))
        
        # Reflection
        self.ln(8)
        self._set_font('B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "REFLECTION", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('reflection', ''))
        
        # Questions
        self.ln(8)
        self._set_font('B', 11)
        self.set_text_color(*self.accent_color)
        self.cell(0, 8, "APPLICATION QUESTIONS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        
        questions = day_data.get('questions', [])
        for i, q in enumerate(questions, 1):
            self.multi_cell(0, 6, f"{i}. {q}")
            self.ln(2)
            
        # Prayer
        self.ln(5)
        
        prayer_text = day_data.get('prayer', '')
        
        # Calculate height needed for prayer text
        # Width = Page Width - Margins - Padding
        # Assuming page width A4 (210) - margin (15*2) = 180
        # Rect width is 190? Wait, default margin is 10mm or set to 15?
        # In init: self.set_auto_page_break(auto=True, margin=15)
        # So effective width is 180.
        # Rect is drawn with hardcoded 190 width in previous code, which might be too wide if margin is 15.
        # Let's check: 210 - 15 - 15 = 180.
        # If I draw rect 190, it spills into right margin.
        # I should use reliable width. self.epw gives effective page width.
        
        box_width = self.epw
        self._set_font('I', 11)
        
        # Calculate lines
        # multi_cell height calculation is tricky without simulating.
        # FPDF2 has getting string width, but wrapping is complex.
        # Best way is to use get_string_width logic or just estimate?
        # FPDF2 allows printing to a dummy object or just calculating.
        # Actually, let's just use multi_cell with split_only=True to count lines (available in newer fpdf2)
        # Or just use a heuristic: chars per line ~ 90-100 for 11pt?
        # Better: let's use multi_cell and let it flow, but we want a background rect.
        # To do background rect dynamically, we can output the cell, measure Y change.
        
        start_y = self.get_y()
        
        # We need to draw rect first? No, if we draw rect first we need height.
        # Approach: Calculate height first.
        # lines = self.multi_cell(box_width - 10, 6, prayer_text, split_only=True) # split_only returns list of lines
        # But split_only might not be available in all versions.
        # Let's try to just print the text, capture the height, then backtrack? No.
        
        # Safe approach with FPDF2:
        # 1. Save current Y.
        # 2. Print text (invisible? No).
        # 3. Calculate height.
        
        # Let's use the .multi_cell(dry_run=True) if available, or just estimate.
        # Since I can't easily verify fpdf2 version features right now, let's use a safe estimation.
        # 11pt font ~ 4mm height? line height is 6mm.
        # Approx chars per line: 180mm / 2mm per char (avg) = 90 chars.
        
        # Let's try to use the multi_cell return value if possible, or just print it inside a cell that has fill.
        # FPDF multi_cell can take 'fill=True'.
        
        self.set_fill_color(240, 240, 240) # Light grey bg
        self.set_text_color(0, 0, 0)
        
        # Header "PRAYER"
        self._set_font('B', 11)
        self.set_text_color(*self.accent_color)
        
        # Draw header background? Or whole box background.
        # Let's make the whole prayer section one block.
        
        # If we just want the box to resize, we can use multi_cell with fill.
        # But we have a title "PRAYER" and then the text.
        
        # Let's print the title, then the text.
        # To have a background for both, we need total height.
        # Let's just print them sequentially with fill=True?
        # But that leaves gaps between lines if not careful? No, multi_cell fills the line rect.
        
        # Simplified robust approach:
        # 1. Print "PRAYER" with fill.
        # 2. Print text with fill.
        
        self.cell(0, 8, "PRAYER", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        
        self._set_font('I', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, prayer_text, fill=True)
