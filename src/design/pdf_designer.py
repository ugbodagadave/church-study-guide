import os
from typing import Dict, Any
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from src.utils.logger import setup_logger

logger = setup_logger("pdf_designer")


class PDFDesigner(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.primary_color = (24, 37, 72)
        self.secondary_color = (120, 130, 150)
        self.accent_color = (211, 83, 121)
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

    def header(self):
        if self.page_no() > 1:
            self._set_font('I', 8)
            self.set_text_color(*self.secondary_color)
            self.cell(0, 10, f'{self.series_title} - Discipleship Guide', new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')
            self.ln(10)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self._set_font('I', 8)
            self.set_text_color(128)
            self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

    def create_pdf(self, content: Dict[str, Any], output_path: str, logo_path: str = None):
        """
        Generates the PDF based on content dictionary.
        """
        self.series_title = content.get("series_title", "Study Guide")
        
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
        if logo_path and os.path.exists(logo_path):
            try:
                self.image(logo_path, x=20, y=20, w=30)
            except Exception as e:
                logger.warning(f"Could not add logo image: {e}")

        band_top = 32
        band_height = 34
        self.set_y(band_top)
        self._set_font('B', 24)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(*self.primary_color)
        self.set_x(0)
        self.cell(self.w, band_height, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.set_y(band_top + 8)
        self._set_font('B', 22)
        self.cell(0, 10, content.get("series_title", "Sermon Series").upper(), align='C')

        preacher_name = content.get("preacher_name") or ""
        if preacher_name:
            self.ln(12)
            self._set_font('I', 11)
            self.set_text_color(230, 230, 230)
            self.cell(0, 6, "By", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

            self.ln(2)
            self._set_font('B', 16)
            name_width = self.get_string_width(preacher_name) + 16
            name_x = (self.w - name_width) / 2
            self.set_fill_color(*self.accent_color)
            self.set_text_color(255, 255, 255)
            self.set_xy(name_x, self.get_y())
            self.cell(name_width, 10, preacher_name, border=0, align='C', fill=True)

        self.set_y(96)
        self.set_fill_color(252, 244, 249)
        self.set_draw_color(*self.accent_color)
        box_y = self.get_y()
        self.rect(20, box_y, self.w - 40, 45, 'DF')

        self.set_xy(25, box_y + 6)
        self._set_font('B', 12)
        self.set_text_color(*self.accent_color)
        self.cell(0, 6, "MEMORY VERSE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

        self.set_x(25)
        self._set_font('I', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(self.w - 50, 6, content.get("memory_verse", ""), align='L')

    def _create_day_page(self, day_data: Dict[str, Any]):
        # Day Header
        self._set_font('B', 16)
        self.set_text_color(*self.primary_color)
        self.multi_cell(0, 10, f"DAY {day_data.get('day', '?')}: {day_data.get('title', '').upper()}", align='L')
        self.ln(1)
        self.set_draw_color(*self.secondary_color)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(5)
        
        # Scripture
        self._set_font('B', 11)
        label = "SCRIPTURE READING"
        label_width = self.get_string_width(label) + 6
        self.set_fill_color(*self.accent_color)
        self.set_text_color(255, 255, 255)
        self.cell(label_width, 8, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('scripture', ''))
        
        # Reflection
        self.ln(8)
        self._set_font('B', 11)
        label = "REFLECTION"
        label_width = self.get_string_width(label) + 6
        self.set_fill_color(*self.accent_color)
        self.set_text_color(255, 255, 255)
        self.cell(label_width, 8, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, day_data.get('reflection', ''))
        
        # Question
        self.ln(8)
        self._set_font('B', 11)
        label = "APPLICATION QUESTION"
        label_width = self.get_string_width(label) + 6
        self.set_fill_color(*self.accent_color)
        self.set_text_color(255, 255, 255)
        self.cell(label_width, 8, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self._set_font('', 11)
        self.set_text_color(0, 0, 0)
        
        # Support both new 'question' string and legacy 'questions' list
        question = day_data.get('question')
        if not question and 'questions' in day_data:
            qs = day_data['questions']
            if isinstance(qs, list) and qs:
                question = qs[0]
            elif isinstance(qs, str):
                question = qs
                
        if question:
            self.multi_cell(0, 6, question)
            
        self.ln(2)
            
        # Prayer
        self.ln(7)
        self.set_draw_color(*self.secondary_color)
        self.set_line_width(0.2)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
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
        
        self.set_fill_color(252, 244, 249)
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
