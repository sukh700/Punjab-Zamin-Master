import flet as ft
import math
import datetime
from fpdf import FPDF, XPos, YPos
import os

def main(page: ft.Page):
    pk = lambda x: from_karm(x).replace("K"," Karm").replace("F"," Feet").replace("I"," Inch").replace("S"," Sut")
    page.title = "ਪੰਜਾਬ ਜ਼ਮੀਨ ਮਾਸਟਰ V61.0"
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    running_total_marla = 0.0
    calculation_history = ft.Column(spacing=10)
    history_data = []
    MY_MOB = "9592571715"

    def format_input_caps(e):
        if e.control.value:
            current_text = e.control.value
            words = current_text.split(" ")
            capitalized_words = [word.capitalize() for word in words]
            new_text = " ".join(capitalized_words)
            if current_text != new_text:
                e.control.value = new_text
                e.control.update()

    def validate_phone(e):
        e.control.value = "".join(filter(str.isdigit, e.control.value))
        if len(e.control.value) > 10:
            e.control.value = e.control.value[:10]
        e.control.update()

    # --- Customer Details (Fields Definition) ---
    c_name = ft.TextField(label="ਨਾਮ / Name", width=250, dense=True, on_change=format_input_caps)
    c_father_name = ft.TextField(label="ਪਿਤਾ ਦਾ ਨਾਮ / Father's Name", width=250, dense=True, on_change=format_input_caps)
    c_grandfather_name = ft.TextField(label="ਦਾਦੇ ਦਾ ਨਾਮ / Grandfather's Name", width=250, dense=True, on_change=format_input_caps)
    
    c_address = ft.TextField(label="ਪਤਾ / Address", width=250, dense=True, on_change=format_input_caps)
    c_phone = ft.TextField(label="ਮੋਬਾਈਲ / Mobile", width=250, dense=True, keyboard_type=ft.KeyboardType.NUMBER, on_change=validate_phone)

    c_district = ft.Dropdown(
        label="ਜ਼ਿਲ੍ਹਾ / District",
        width=250,
        dense=True,
        options=[
            ft.dropdown.Option("Amritsar"), ft.dropdown.Option("Barnala"), ft.dropdown.Option("Bathinda"),
            ft.dropdown.Option("Faridkot"), ft.dropdown.Option("Fatehgarh Sahib"), ft.dropdown.Option("Fazilka"),
            ft.dropdown.Option("Ferozepur"), ft.dropdown.Option("Gurdaspur"), ft.dropdown.Option("Hoshiarpur"),
            ft.dropdown.Option("Jalandhar"), ft.dropdown.Option("Kapurthala"), ft.dropdown.Option("Ludhiana"),
            ft.dropdown.Option("Malerkotla"), ft.dropdown.Option("Mansa"), ft.dropdown.Option("Moga"),
            ft.dropdown.Option("Pathankot"), ft.dropdown.Option("Patiala"), ft.dropdown.Option("Rupnagar"),
            ft.dropdown.Option("S.A.S Nagar (Mohali)"), ft.dropdown.Option("Sangrur"),
            ft.dropdown.Option("Shaheed Bhagat Singh Nagar"), ft.dropdown.Option("Sri Muktsar Sahib"),
            ft.dropdown.Option("Tarn Taran"),
        ],
    )

    # --- Layout for Customer Details ---
    customer_section = ft.Row(
        controls=[
            # ਖੱਬਾ ਪਾਸਾ (Left Side)
            ft.Column([
                c_name,
                c_father_name,
                c_grandfather_name,
            ], spacing=10),
            
            # ਸੱਜਾ ਪਾਸਾ (Right Side)
            ft.Column([
                c_address,
                c_district,
                c_phone,
            ], spacing=10),
        ],
        spacing=40,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START
    )

    # --- Helpers ---
    def to_karm(k, f, i, s):
        try: return float(k or 0) + (float(f or 0)/5.5) + (float(i or 0)/66) + (float(s or 0)/528)
        except: return 0

    def from_karm(total_karm):
        if total_karm <= 0: return "0K"
        total_sut = round(total_karm * 528)
        k, rem = divmod(total_sut, 528)
        f, rem = divmod(rem, 96)
        i, s = divmod(rem, 8)
        parts = []
        if k > 0: parts.append(f"{int(k)}K")
        if f > 0: parts.append(f"{int(f)}F")
        if i > 0: parts.append(f"{int(i)}I")
        if s > 0: parts.append(f"{int(s)}S")
        return " ".join(parts) if parts else "0K"

    def format_area_full(total_marla):
        abs_m = abs(total_marla)
        ki, rem = divmod(round(abs_m * 9), 1440)
        ka, rem = divmod(rem, 180)
        ma, sa = divmod(rem, 9)
        txt = ""
        if ki > 0: txt += f"{int(ki)} Kila "
        if ka > 0: txt += f"{int(ka)} Kanal "
        if ma > 0: txt += f"{int(ma)} Marla "
        if sa > 0: txt += f"{round(sa,1)} Sarsai"
        gaz = round(abs_m * 30.25, 1)
        return f"{txt if txt else '0 Marle'} ({gaz} Gaz)"
    
    def get_punjabi_units(total_m):
        """ਮਰਲਿਆਂ ਨੂੰ ਕਿੱਲਾ-ਕਨਾਲ-ਮਰਲਾ-ਸਰਸਾਈ ਵਿੱਚ ਬਦਲਣ ਲਈ"""
        abs_m = abs(total_m)
        ki, rem = divmod(round(abs_m * 9), 1440)
        ka, rem = divmod(rem, 180)
        ma, sa = divmod(rem, 9)
        txt = []
        if ki > 0: txt.append(f"{int(ki)} ਕਿੱਲਾ")
        if ka > 0: txt.append(f"{int(ka)} ਕਨਾਲ")
        if ma > 0: txt.append(f"{int(ma)} ਮਰਲਾ")
        if sa > 0: txt.append(f"{round(sa,1)} ਸਰਸਾਈ")
        return " ".join(txt) if txt else "0 ਮਰਲਾ"

    def clear_fields(fields_list):
        for field in fields_list: field.value = ""
        page.update()

    def clean_caps(text):
        if not text: return "N/A"
        return " ".join(word.capitalize() for word in str(text).split())
    
    # --- PDF Generator (Only History & Terms Updated) ---
    def generate_pdf(e):
        try:
            pdf = FPDF()
            pdf.add_page()

            # --- Header (ਪੁਰਾਣਾ ਹੀ ਹੈ) ---
            pdf.set_draw_color(0, 80, 0)
            pdf.rect(10, 10, 190, 24)
            pdf.set_text_color(0, 80, 0)
            pdf.set_font('helvetica', 'B', 22)
            pdf.set_xy(10, 13)
            pdf.cell(190, 10, text="SUKH LAND SOLUTIONS", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(190, 6, text=f"CONTACT: 95925-71715", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # --- Customer Details (Two Column Layout) ---
            pdf.set_xy(10, 40)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('helvetica', 'B', 11)
            pdf.cell(190, 8, text=" CUSTOMER & REPORT DETAILS", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            start_y = pdf.get_y()
            current_date = datetime.datetime.now().strftime('%d-%m-%Y %I:%M %p')
            
            # ਡੇਟਾ ਨੂੰ ਦੋ ਹਿੱਸਿਆਂ ਵਿੱਚ ਵੰਡਿਆ
            left_side = [
                ("Name", clean_caps(c_name.value)),
                ("Father", clean_caps(c_father_name.value)),
                ("G.Father", clean_caps(c_grandfather_name.value))
            ]
            
            right_side = [
                ("Address", clean_caps(c_address.value)),
                ("District", c_district.value or 'xxxxxx'),
                ("Mobile", c_phone.value or 'xxxxxx')
            ]

            # ਦੋਵਾਂ ਕਾਲਮਾਂ ਨੂੰ ਪ੍ਰਿੰਟ ਕਰਨਾ
            for i in range(3):
                # --- ਖੱਬਾ ਕਾਲਮ (Left Side) ---
                pdf.set_x(12)
                pdf.set_font('helvetica', 'B', 10)
                # ਲੇਬਲ ਅਤੇ ਕਲਨ (:) ਇਕੱਠੇ
                pdf.cell(20, 7, text=f"{left_side[i][0]}:") 
                pdf.set_font('helvetica', '', 10)
                pdf.cell(70, 7, text=str(left_side[i][1]))
                
                # --- ਸੱਜਾ ਕਾਲਮ (Right Side) ---
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(20, 7, text=f"{right_side[i][0]}:") 
                pdf.set_font('helvetica', '', 10)
                # ਨਵੀਂ ਲਾਈਨ 'ਤੇ ਜਾਣ ਲਈ NEXT ਦੀ ਵਰਤੋਂ
                pdf.cell(70, 7, text=str(right_side[i][1]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # ਤਾਰੀਖ ਅਤੇ ਬਾਕਸ ਦੀ ਫਿਨਿਸ਼ਿੰਗ
            pdf.set_font('helvetica', '', 8)
            pdf.cell(190, 6, text=f"Date: {current_date}", align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.rect(10, start_y, 190, pdf.get_y() - start_y)

            # --- Grand Total (ਸਹੀ ਫਾਰਮੈਟ) ---
            pdf.ln(5)
            pdf.set_text_color(0, 0, 0)        # ਕਾਲਾ ਰੰਗ
            pdf.set_fill_color(255, 255, 255)  # ਚਿੱਟਾ ਬੈਕਗ੍ਰਾਊਂਡ
            pdf.set_font('helvetica', 'B', 12) 
            
            total_raw = format_area_full(running_total_marla)
            
            # multi_cell ਲਿਖਾਈ ਨੂੰ ਲਾਈਨ ਤੋਂ ਬਾਹਰ ਜਾਣ ਤੋਂ ਰੋਕਦਾ ਹੈ
            pdf.multi_cell(190, 10, text=f"GRAND TOTAL AREA: {total_raw}", border=1, align='C', fill=True)
            pdf.ln(5)
            
           # --- History (Updated for Details and Fractions) ---
            pdf.ln(5)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(190, 8, text="MEASUREMENT HISTORY:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

            # ਟੇਬਲ ਹੈਡਰ (Table Header)
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(40, 8, text="Action", border=1, fill=True)
            pdf.cell(100, 8, text="Details (Input/Fraction)", border=1, fill=True)
            pdf.cell(50, 8, text="Area Result", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font('helvetica', '', 10) 
            for entry_str in history_data:
                if pdf.get_y() > 250: pdf.add_page()
                
                # entry_str ਨੂੰ ਤੋੜੋ (ਜੋ ਤੁਸੀਂ update_history ਵਿੱਚ ਬਣਾਇਆ ਸੀ)
                # ਉਮੀਦ ਹੈ ਫਾਰਮੈਟ "Label | Detail | Area" ਹੈ
                parts = entry_str.split(" | ")
                if len(parts) >= 3:
                    label = parts[0].encode('ascii', 'ignore').decode('ascii')
                    # Detail ਵਿੱਚ Fraction (23/140) ਅਤੇ Units (K,Kn,M) ਹੋਣਗੇ
                    detail = parts[1].encode('ascii', 'ignore').decode('ascii')
                    area = parts[2].encode('ascii', 'ignore').decode('ascii')
                    
                    # ਰੋਅ (Row) ਪ੍ਰਿੰਟ ਕਰੋ
                    pdf.cell(40, 8, text=label, border=1)
                    pdf.cell(100, 8, text=detail, border=1)
                    pdf.cell(50, 8, text=area, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(1)

            # --- Signatures ---
            pdf.set_y(-35)
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(95, 5, text="........................................", align='C')
            pdf.cell(95, 5, text="........................................", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(95, 5, text="Customer Signature", align='C')
            pdf.cell(95, 5, text="Authorized Sign", align='C')

            fname = f"Land_Report_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
            pdf.output(fname)
            os.startfile(fname)
            
        except Exception as ex: 
            print(f"PDF Error: {ex}")

    # --- History Update ---
    def update_history(val, label, detail, is_info=False):
        nonlocal running_total_marla
        if not is_info and round(val, 4) == 0:
            if "Tool" not in label:
                 return
        if not is_info: running_total_marla += val
        area_txt = format_area_full(val) if (not is_info and val != 0) else ""
        entry_str = f"{label} | {detail} | {area_txt}"
        history_data.insert(0, entry_str)
        
        entry = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(label, weight="bold", color="green" if val >= 0 else "red"),
                    ft.Text(f"ਵੇਰਵਾ: {detail}", size=11, italic=True),
                    ft.Text(area_txt, size=13, weight="bold") if not is_info else ft.Container(),
                ], expand=True),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=lambda _: remove_entry(val, entry, entry_str, is_info))
            ]),
            padding=10, border=ft.Border.all(1, "#eee"), border_radius=8, bgcolor="#ffffff"
        )
        calculation_history.controls.insert(0, entry)
        grand_total_display.value = f"ਕੁੱਲ ਰਕਬਾ: {format_area_full(running_total_marla)}"
        page.update()

    def remove_entry(val, control, data_str, is_info):
        nonlocal running_total_marla
        if not is_info: running_total_marla -= val
        calculation_history.controls.remove(control)
        if data_str in history_data: history_data.remove(data_str)
        grand_total_display.value = f"ਕੁੱਲ ਰਕਬਾ: {format_area_full(running_total_marla)}"
        page.update()

    # --- ਕਰਮ, ਫੁੱਟ, ਇੰਚ, ਸੂਤ ਦੇ ਡੱਬੇ ਬਣਾਉਣ ਲਈ ---
    def urow():
        # ਇੱਥੇ ਅਸੀਂ ਲੇਬਲ ਅਤੇ ਉਹਨਾਂ ਦੇ ਪੂਰੇ ਨਾਮ ਦੀ ਇੱਕ ਲਿਸਟ ਬਣਾਈ ਹੈ
        labels = [
            ("K", "ਕਰਮ"), 
            ("F", "ਫੁੱਟ"), 
            ("I", "ਇੰਚ"), 
            ("S", "ਸੂਤ")
        ]
        
        # ਹਰ ਇੱਕ ਲਈ ਅਲੱਗ TextField ਤਿਆਰ ਹੋਵੇਗੀ
        return [
            ft.TextField(
                label=f"{short} ({full})", # ਉਦਾਹਰਨ: K (ਕਰਮ)
                width=80,                  # ਚੌੜਾਈ ਥੋੜੀ ਵਧਾਈ ਹੈ ਤਾਂ ਜੋ ਲੇਬਲ ਸਾਫ਼ ਦਿਖੇ
                dense=True,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER # ਸਿਰਫ਼ ਨੰਬਰ ਭਰਨ ਲਈ
            ) 
            for short, full in labels
        ]

   # --- Inputs (ਸਾਰਾ ਕੋਡ ਇਕੱਠਾ ਅਤੇ ਸੈੱਟ ਕੀਤਾ ਹੋਇਆ) ---
    grand_total_display = ft.Text("ਕੁੱਲ ਰਕਬਾ: 0", size=22, weight="bold", color="blue")

    # 1. ਕੁੱਲ ਮਾਲਕੀ ਭਰਨ ਲਈ ਡੱਬੇ (Total area fields)
    sh_kila = ft.TextField(label="ਕਿੱਲਾ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sh_kanal = ft.TextField(label="ਕਨਾਲ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sh_marla = ft.TextField(label="ਮਰਲਾ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sh_sarsai = ft.TextField(label="ਸਰਸਾਈ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    
    # 2. ਹਿੱਸਾ (Fraction) ਭਰਨ ਲਈ (ਜਿਵੇਂ 23/140)
    sh_num = ft.TextField(label="ਹਿੱਸਾ (ਉੱਪਰ)", width=120, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sh_den = ft.TextField(label="ਹਿੱਸਾ (ਹੇਠਾਂ)", width=120, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    
    # 3. ਰਜਿਸਟਰੀ ਵੇਚਣ ਲਈ ਰਕਬਾ (Sale area fields)
    sell_kila = ft.TextField(label="ਕਿੱਲਾ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sell_kanal = ft.TextField(label="ਕਨਾਲ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sell_marla = ft.TextField(label="ਮਰਲਾ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    sell_sarsai = ft.TextField(label="ਸਰਸਾਈ", width=80, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
    
    # ਨਤੀਜਾ ਦਿਖਾਉਣ ਲਈ ਟੈਕਸਟ
    sh_res_txt = ft.Text("", weight="bold", size=16)
    
    # 1. ਆਇਤਾਕਾਰ (Rectangular Tool)
    # ----------------------------------------
    r1, r2 = urow(), urow()
    for f in r1: f.label = f"ਲੰਬਾਈ {f.label}"
    for f in r2: f.label = f"ਚੌੜਾਈ {f.label}"
    
    rect_ui = ft.Column([
        ft.Text("--- ਆਇਤਾਕਾਰ (Rect) ---", weight="bold", color="green"),
        ft.Row(r1, wrap=True, spacing=5),
        ft.Row(r2, wrap=True, spacing=5),
    ])

    # 2. ਤਿਕੋਣ (Triangle Tool)
    # ----------------------------------------
    t1, t2, t3 = urow(), urow(), urow()
    
    # ਪਹਿਲੀ ਬਾਹੀ ਲਈ ਲੇਬਲ
    for f in t1: 
        f.label = f"ਬਾਹੀ 1 {f.label}"
        
    # ਦੂਜੀ ਬਾਹੀ ਲਈ ਲੇਬਲ (ਇੱਥੇ f2 ਦੀ ਜਗ੍ਹਾ t2 ਕਰ ਦਿੱਤਾ ਹੈ)
    for f in t2: 
        f.label = f"ਬਾਹੀ 2 {f.label}" 
        
    # ਤੀਜੀ ਬਾਹੀ ਲਈ ਲੇਬਲ
    for f in t3: 
        f.label = f"ਬਾਹੀ 3 {f.label}"
    
    tri_ui = ft.Column([
        ft.Text("--- ਤਿਕੋਣ (Triangle) ---", weight="bold", color="green"),
        ft.Row(t1, wrap=True, spacing=5),
        ft.Row(t2, wrap=True, spacing=5),
        ft.Row(t3, wrap=True, spacing=5),
    ])

    # 3. ਚੌਂਠ (Four Sides Tool)
    # ----------------------------------------
    c1, c2, c3, c4 = urow(), urow(), urow(), urow()
    for f in c1: f.label = f"ਬਾਹੀ 1 {f.label}"
    for f in c2: f.label = f"ਬਾਹੀ 2 {f.label}"
    for f in c3: f.label = f"ਬਾਹੀ 3 {f.label}"
    for f in c4: f.label = f"ਬਾਹੀ 4 {f.label}"

    # 4. ਮੈਨੂਅਲ ਐਂਟਰੀ (Manual Entry)
    # ----------------------------------------
    man_f = [
        ft.TextField(label="ਕਿੱਲਾ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਕਨਾਲ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਮਰਲਾ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਸਰਸਾਈ", width=65, dense=True, text_size=12)
    ]

    # 5. ਗੁਣੀਆ (Gunya Tool)
    # ----------------------------------------
    g1, g2 = urow(), urow()
    for f in g1: f.label = f"ਬਾਹੀ 1 {f.label}"
    for f in g2: f.label = f"ਬਾਹੀ 2 {f.label}"

    # 6. ਸ਼ਾਫੀ (Shafi/Division Tool) - Error ਠੀਕ ਕਰਨ ਲਈ
    # ----------------------------------------
    sf_total = [
        ft.TextField(label="ਕਿੱਲਾ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਕਨਾਲ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਮਰਲਾ", width=65, dense=True, text_size=12),
        ft.TextField(label="ਸਰਸਾਈ", width=65, dense=True, text_size=12)
    ]
    sf_b1, sf_b2, sf_b3 = urow(), urow(), urow()
    for f in sf_b1: f.label = f"ਬਾਹੀ 1 {f.label}"
    for f in sf_b2: f.label = f"ਬਾਹੀ 2 {f.label}"
    for f in sf_b3: f.label = f"ਬਾਹੀ 3 {f.label}"
    
    # ਸਾਰੇ ਸੈਕਸ਼ਨਾਂ ਲਈ ਨਤੀਜਾ ਦਿਖਾਉਣ ਵਾਲੇ ਡੱਬੇ
    tool_res = ft.Text("", size=16, color="purple", weight="bold")
    rect_res_label = ft.Text("", size=16, color="blue", weight="bold")
    tri_res_label = ft.Text("", size=16, color="blue", weight="bold")
    quad_res_label = ft.Text("", size=16, color="blue", weight="bold")
    man_res_label = ft.Text("", size=16, color="blue", weight="bold")
    # ਟੂਲਸ ਲਈ ਅਲੱਗ-ਅਲੱਗ ਰਿਜ਼ਲਟ ਲੇਬਲ
    gunya_res_label = ft.Text("", size=16, color="purple", weight="bold")
    sf_b2_res = ft.Text("", size=16, color="red", weight="bold")
    sf_b3_res = ft.Text("", size=16, color="red", weight="bold")
    sf_b4_res = ft.Text("", size=16, color="red", weight="bold")

    # --- Logics ---
    # --- ਨਵਾਂ ਹਿੱਸਾ ਅਤੇ ਰਜਿਸਟਰੀ ਲੋਜਿਕ (Updated with Clear Fields & Detail) ---
    def process_fraction_logic(is_add):
        try:
            k, kn, m, s = sh_kila.value or "0", sh_kanal.value or "0", sh_marla.value or "0", sh_sarsai.value or "0"
            num, den = sh_num.value or "1", sh_den.value or "1"
            
            total_m = (float(k) * 160) + (float(kn) * 20) + float(m) + (float(s) / 9)
            share_marla = (total_m * float(num)) / float(den)
            
            if share_marla > 0:
                ans_units = format_area_full(share_marla)
                status = "(+)" if is_add else "(-)"
                
                # PDF ਸ਼ੀਟ ਦੇ ਹਿਸਾਬ ਨਾਲ ਡਿਟੇਲ ਤਿਆਰ ਕਰੋ
                # ਉਦਾਹਰਨ: 2K-3Kn-0M-0S  2/13
                detail_txt = f"{k}K-{kn}Kn-{m}M-{s}S  {num}/{den}"
                
                update_history(share_marla if is_add else -share_marla, status, detail_txt)
                
                sh_res_txt.value = f"✅ ਸੇਵ ਹੋਇਆ: {ans_units}"
                sh_res_txt.color = ft.Colors.BLUE
                
                # ਡੱਬੇ ਖਾਲੀ ਕਰੋ
                for f in [sh_kila, sh_kanal, sh_marla, sh_sarsai, sh_num, sh_den]:
                    f.value = ""
            page.update()
        except Exception as e:
            sh_res_txt.value = "❌ ਅੰਕ ਸਹੀ ਭਰੋ"
            page.update()

    def registry_sale_logic(e):
        try:
            tk, tkn, tm, ts = sh_kila.value or "0", sh_kanal.value or "0", sh_marla.value or "0", sh_sarsai.value or "0"
            sk, skn, sm, ss = sell_kila.value or "0", sell_kanal.value or "0", sell_marla.value or "0", sell_sarsai.value or "0"
            
            total_m = (float(tk)*160 + float(tkn)*20 + float(tm) + float(ts)/9)
            sold_m = (float(sk)*160 + float(skn)*20 + float(sm) + float(ss)/9)
            
            if total_m > 0 and sold_m > 0:
                n, d = int(round(sold_m * 9)), int(round(total_m * 9))
                import math
                common = math.gcd(n, d)
                registry_fraction = f"{n // common}/{d // common}"
                
                # PDF ਲਈ ਡਿਟੇਲ: ਕੁੱਲ ਰਕਬਾ ਅਤੇ ਵੇਚਿਆ ਰਕਬਾ
                # ਉਦਾਹਰਨ: ਕੁੱਲ: 0K-3Kn  ਵੇਚਿਆ: 2K-1Kn
                detail_txt = f"{tk}K-{tkn}Kn {tm}M  {sk}K-{skn}Kn {sm}M"
                
                # ਰਜਿਸਟਰੀ ਹਮੇਸ਼ਾ ਘਟਾਓ (-) ਹੁੰਦੀ ਹੈ
                update_history(-sold_m, "(-)", detail_txt)
                
                sh_res_txt.value = f"📜 ਹਿੱਸਾ: {registry_fraction}"
                sh_res_txt.color = ft.Colors.ORANGE
                
                for f in [sh_kila, sh_kanal, sh_marla, sh_sarsai, sell_kila, sell_kanal, sell_marla, sell_sarsai]:
                    f.value = ""
            page.update()
        except:
            sh_res_txt.value = "❌ ਰਕਬਾ ਸਹੀ ਭਰੋ"
            page.update()


    def add_rect(is_add):
        try:
            s1, s2 = to_karm(*[f.value for f in r1]), to_karm(*[f.value for f in r2])
            if s1 > 0 and s2 > 0:
                v = (s1*s2)/9
                # ਬਟਨ ਦੇ ਨੀਚੇ ਨਤੀਜਾ ਦਿਖਾਉਣਾ
                rect_res_label.value = f"ਨਤੀਜਾ: {format_area_full(v)}"
                # ਹਿਸਟਰੀ ਲਈ ਪੂਰੀ ਡਿਟੇਲ ਤਿਆਰ ਕਰਨਾ
                detail_txt = f"ਬਾਹੀਆਂ: ({from_karm(s1)}) x ({from_karm(s2)})"
                update_history(v if is_add else -v, "2-Side Rect", detail_txt)
                clear_fields(r1 + r2)
                page.update()
        except: pass

    def add_tri(is_add):
        try:
            s1, s2, s3 = to_karm(*[f.value for f in t1]), to_karm(*[f.value for f in t2]), to_karm(*[f.value for f in t3])
            if (s1 + s2 > s3) and (s1 + s3 > s2) and (s2 + s3 > s1):
                s = (s1+s2+s3)/2
                v = math.sqrt(s*(s-s1)*(s-s2)*(s-s3))/9
                tri_res_label.value = f"ਨਤੀਜਾ: {format_area_full(v)}"
                detail_txt = f"ਬਾਹੀਆਂ: {from_karm(s1)}, {from_karm(s2)}, {from_karm(s3)}"
                update_history(v if is_add else -v, "Triangle Plot", detail_txt)
                clear_fields(t1 + t2 + t3)
                page.update()
            else:
                tri_res_label.value = "ਗਲਤ ਪੈਮਾਇਸ਼: ਤਿਕੋਣ ਨਹੀਂ ਬਣ ਸਕਦਾ!"
                page.update()
        except: pass

    def add_quad(is_add):
        try:
            l1, l2, w1, w2 = to_karm(*[f.value for f in c1]), to_karm(*[f.value for f in c2]), to_karm(*[f.value for f in c3]), to_karm(*[f.value for f in c4])
            if (l1+l2) > 0 and (w1+w2) > 0:
                v = ((l1+l2)/2 * (w1+w2)/2)/9
                quad_res_label.value = f"ਨਤੀਜਾ: {format_area_full(v)}"
                detail_txt = f"ਲੰਬਾਈ:({from_karm(l1)}, {from_karm(l2)}) ਚੌੜਾਈ:({from_karm(w1)}, {from_karm(w2)})"
                update_history(v if is_add else -v, "4-Side Avg", detail_txt)
                clear_fields(c1 + c2 + c3 + c4)
                page.update()
        except: pass

    def find_missing_side(e):
        try: # ਇੱਥੇ 4 ਸਪੇਸ ਜਾਂ ਇੱਕ Tab ਜ਼ਰੂਰ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ
            # 1. ਕੈਲਕੂਲੇਸ਼ਨ
            target_m = (float(sf_total[0].value or 0)*160 + float(sf_total[1].value or 0)*20 + float(sf_total[2].value or 0) + float(sf_total[3].value or 0)/9)
            target_sq_karm, b1, b2, b3 = target_m * 9, to_karm(*[f.value for f in sf_b1]), to_karm(*[f.value for f in sf_b2]), to_karm(*[f.value for f in sf_b3])
            
            sf_b2_res.value = sf_b3_res.value = sf_b4_res.value = ""
            res_karm, label = 0, ""

            if b1 > 0 and b2 == 0:
                res_karm, label = target_sq_karm / b1, "2nd Side"
            elif b1 > 0 and b2 > 0 and b3 == 0:
                res_karm, label = (target_sq_karm * 2) / b1, "3rd Side"
            elif b1 > 0 and b3 > 0:
                res_karm, label = (target_sq_karm / ((b1+b2)/2)) * 2 - b3, "4th Side"

            if res_karm > 0:
                # ਇੱਥੇ pk ਫੰਕਸ਼ਨ ਦੀ ਵਰਤੋਂ
                res_proper = pk(res_karm)
                
                if label == "2nd Side": sf_b2_res.value = f"ਦੂਜੀ ਬਾਹੀ: {res_proper}"
                elif label == "3rd Side": sf_b3_res.value = f"ਤੀਜੀ ਬਾਹੀ: {res_proper}"
                elif label == "4th Side": sf_b4_res.value = f"ਚੌਥੀ ਬਾਹੀ: {res_proper}"

                # 2. ਹਿਸਟਰੀ ਲਈ ਡਾਟਾ ਤਿਆਰ ਕਰਨਾ
                t_en = format_area_full(target_m).replace("ਕਿੱਲਾ","Kila").replace("ਕਨਾਲ","Kanal").replace("ਮਰਲਾ","Marla").replace("ਸਰਸਾਈ","Sarsai")
                detail = f"Target: {t_en} | Result: {res_proper}"
                
                # 3. ਹਿਸਟਰੀ ਸੇਵ ਕਰਨਾ (ਇਹ ਲਾਈਨ ਹੁਣ ਚੱਲੇਗੀ)
                update_history(0, f"Shafi Tool ({label})", detail, False) 
            
            page.update()
        except Exception as ex:
            print(f"Error: {ex}") # ਜੇ ਕੋਈ ਹੋਰ ਗਲਤੀ ਹੋਈ ਤਾਂ ਇੱਥੇ ਦਿਖ ਜਾਵੇਗੀ
        
        # --- 4. ਰਕਬਾ ਕਨਵਰਟਰ ਵਿਜੇਟਸ (ਇਹ ਲਾਈਨਾਂ ਇੱਥੇ ਪੇਸਟ ਕਰੋ) ---
    conv_input = ft.TextField(label="ਨੰਬਰ ਭਰੋ", width=120, dense=True)
    conv_res = ft.Text("", size=16, color="blue", weight="bold")
    conv_dropdown = ft.Dropdown(
        label="ਇਕਾਈ ਚੁਣੋ",
        width=250,
        options=[
            ft.dropdown.Option("Karm to Feet"), ft.dropdown.Option("Feet to Karm"),
            ft.dropdown.Option("Feet to Inch"), ft.dropdown.Option("Inch to Feet"),
            ft.dropdown.Option("Inch to Sut"), ft.dropdown.Option("Sut to Inch"),
            ft.dropdown.Option("Gaz to Feet"), ft.dropdown.Option("Feet to Gaz"),
            ft.dropdown.Option("Meter to Feet"), ft.dropdown.Option("Feet to Meter"),
            ft.dropdown.Option("Kila to Kanal"), ft.dropdown.Option("Kanal to Kila"),
            ft.dropdown.Option("Kila to Marla"), ft.dropdown.Option("Marla to Kila"),
            ft.dropdown.Option("Kanal to Marla"), ft.dropdown.Option("Marla to Kanal"),
            ft.dropdown.Option("Marla to Sarsai"), ft.dropdown.Option("Sarsai to Marla"),
            ft.dropdown.Option("Kila to Bigha"), ft.dropdown.Option("Bigha to Kila"),
            ft.dropdown.Option("Bigha to Biswa"), ft.dropdown.Option("Kila to Hectare"),
            ft.dropdown.Option("Hectare to Kila"), ft.dropdown.Option("Marla to Gaz"),
            ft.dropdown.Option("Gaz to Marla"), ft.dropdown.Option("Marla to Sq.Ft"),
            ft.dropdown.Option("Sarsai to Feet"), ft.dropdown.Option("Feet to Sarsai")
        ],
    )

        # --- 5. All-in-One Unit Converter Logic (ਸਿਰਫ ਇਹ ਇੱਕ ਹੀ ਰੱਖੋ) ---
    def convert_units(e):
        try:
            # ਪਹਿਲਾਂ ਚੈੱਕ ਕਰੋ ਕਿ ਇਨਪੁਟ ਖਾਲੀ ਤਾਂ ਨਹੀਂ
            if not conv_input.value:
                conv_res.value = "ਪਹਿਲਾਂ ਨੰਬਰ ਭਰੋ"
                page.update()
                return
            
            val = float(conv_input.value)
            u = conv_dropdown.value
            r = ""
            
            # ਸਾਰੇ ਰੂਲਜ਼ ਇੱਕੋ ਥਾਂ 'ਤੇ
            if u == "Karm to Feet": r = f"{val} Karm = {val * 5.5:.2f} Feet"
            elif u == "Feet to Karm": r = f"{val} Feet = {val / 5.5:.3f} Karm"
            elif u == "Feet to Inch": r = f"{val} Feet = {val * 12:.0f} Inch"
            elif u == "Inch to Feet": r = f"{val} Inch = {val / 12:.2f} Feet"
            elif u == "Inch to Sut": r = f"{val} Inch = {val * 8:.0f} Sut"
            elif u == "Sut to Inch": r = f"{val} Sut = {val / 8:.3f} Inch"
            elif u == "Gaz to Feet": r = f"{val} Gaz = {val * 3:.0f} Feet"
            elif u == "Feet to Gaz": r = f"{val} Feet = {val / 3:.2f} Gaz"
            elif u == "Meter to Feet": r = f"{val} Meter = {val * 3.281:.2f} Feet"
            elif u == "Feet to Meter": r = f"{val} Feet = {val / 3.281:.2f} Meter"
            elif u == "Kila to Kanal": r = f"{val} Kila = {val * 8:.0f} Kanal"
            elif u == "Kanal to Kila": r = f"{val} Kanal = {val / 8:.3f} Kila"
            elif u == "Kila to Marla": r = f"{val} Kila = {val * 160:.0f} Marla"
            elif u == "Marla to Kila": r = f"{val} Marla = {val / 160:.4f} Kila"
            elif u == "Kanal to Marla": r = f"{val} Kanal = {val * 20:.0f} Marla"
            elif u == "Marla to Kanal": r = f"{val} Marla = {val / 20:.2f} Kanal"
            elif u == "Marla to Sarsai": r = f"{val} Marla = {val * 9:.0f} Sarsai"
            elif u == "Sarsai to Marla": r = f"{val} Sarsai = {val / 9:.3f} Marla"
            elif u == "Kila to Bigha": r = f"{val} Kila = {val * 4:.0f} Bigha (Pb)"
            elif u == "Bigha to Kila": r = f"{val} Bigha = {val / 4:.2f} Kila"
            elif u == "Bigha to Biswa": r = f"{val} Bigha = {val * 20:.0f} Biswa"
            elif u == "Kila to Hectare": r = f"{val} Kila = {val * 0.4047:.3f} Hectare"
            elif u == "Hectare to Kila": r = f"{val} Hectare = {val / 0.4047:.2f} Kila"
            elif u == "Marla to Gaz": r = f"{val} Marla = {val * 30.25:.2f} Gaz"
            elif u == "Gaz to Marla": r = f"{val} Gaz = {val / 30.25:.2f} Marla"
            elif u == "Marla to Sq.Ft": r = f"{val} Marla = {val * 272.25:.2f} Sq.Ft"
            elif u == "Sarsai to Feet": r = f"{val} Sarsai = {val * 30.25:.2f} Sq.Ft"
            elif u == "Feet to Sarsai": r = f"{val} Sq.Ft = {val / 30.25:.3f} Sarsai"
            
            conv_res.value = r
            page.update()
        except:
            conv_res.value = "ਗਲਤੀ: ਸਹੀ ਨੰਬਰ ਭਰੋ"
            page.update()

   # --- UI Layout ---
    page.add(
        ft.Row([
            ft.Text("ਪੰਜਾਬ ਜ਼ਮੀਨ ਮਾਸਟਰ V61.0", size=22, weight="bold", color="green"), 
            ft.IconButton(ft.Icons.PICTURE_AS_PDF, on_click=generate_pdf, icon_color="red")
        ], alignment="spaceBetween"),
        
        ft.Container(
            padding=15, 
            bgcolor="#f0f4f8", 
            border_radius=10, 
            content=ft.Column([
                # ਪਹਿਲੀ ਰੋਅ (Row): ਨਾਮ ਅਤੇ ਪਤਾ
                ft.Row([c_name, c_address], spacing=20),
                
                # ਦੂਜੀ ਰੋਅ (Row): ਪਿਤਾ ਦਾ ਨਾਮ ਅਤੇ ਜ਼ਿਲ੍ਹਾ
                ft.Row([c_father_name, c_district], spacing=20),
                
                # ਤੀਜੀ ਰੋਅ (Row): ਦਾਦੇ ਦਾ ਨਾਮ ਅਤੇ ਮੋਬਾਈਲ
                ft.Row([c_grandfather_name, c_phone], spacing=20),
                
                ft.Text(f"Developer: {MY_MOB}", size=10, italic=True)
            ])
        ),
        
        grand_total_display,

        # --- ਸਟੈਪ 4: ਨਵਾਂ ਹਿੱਸਾ ਅਤੇ ਰਜਿਸਟਰੀ UI (Fixed) ---
       # --- ਸਟੈਪ 4: ਨਵਾਂ ਹਿੱਸਾ ਅਤੇ ਰਜਿਸਟਰੀ UI (Fixed for New Flet Version) ---
        # --- ਸਟੈਪ 4: ਨਵਾਂ ਹਿੱਸਾ ਅਤੇ ਰਜਿਸਟਰੀ UI (Flet 0.25+ ਲਈ ਪੂਰੀ ਤਰ੍ਹਾਂ ਸਹੀ) ---
        ft.ExpansionTile(
            title=ft.Text("0. ਹਿੱਸਾ ਅਤੇ ਰਜਿਸਟਰੀ (Share & Sale)", weight="bold", color=ft.Colors.BLUE),
            expanded=True, # 'initially_expanded' ਦੀ ਜਗ੍ਹਾ ਹੁਣ 'expanded' ਵਰਤੋ
            controls=[
                ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text("1. ਫਰਦ ਦਾ ਕੁੱਲ ਰਕਬਾ ਭਰੋ (Total Area):", size=12, weight="bold"),
                        ft.Row([sh_kila, sh_kanal, sh_marla, sh_sarsai], wrap=True),
                        ft.Divider(),
                        
                        ft.Text("2. ਹਿਸਾਬ ਜਾਂ ਰਜਿਸਟਰੀ ਚੁਣੋ:", size=12, weight="bold"),
                        
                        # ਹਿੱਸਾ (Share) ਸੈਕਸ਼ਨ
                        ft.Container(
                            bgcolor=ft.Colors.BLUE_GREY_50, 
                            padding=10,
                            border_radius=10,
                            content=ft.Column([
                                ft.Text("ਹਿਸਾਬ (Share Calculation)", weight="bold"),
                                ft.Text("ਹਿੱਸਾ (ਜਿਵੇਂ 23 / 140):", size=11),
                                ft.Row([sh_num, ft.Text("/", size=25), sh_den]),
                                ft.Row([
                                    ft.FilledButton("ਜੋੜੋ (+)", on_click=lambda _: process_fraction_logic(True), bgcolor=ft.Colors.GREEN),
                                    ft.FilledButton("ਕੱਢੋ (-)", on_click=lambda _: process_fraction_logic(False), bgcolor=ft.Colors.RED),
                                ]),
                            ])
                        ),
                        
                        ft.Container(height=10), # Space
                        
                        # ਰਜਿਸਟਰੀ (Sale) ਸੈਕਸ਼ਨ
                        ft.Container(
                            bgcolor=ft.Colors.ORANGE_50,
                            padding=10,
                            border_radius=10,
                            content=ft.Column([
                                ft.Text("ਰਜਿਸਟਰੀ (Sale / Fraction)", weight="bold"),
                                ft.Text("ਜਿੰਨੀ ਜ਼ਮੀਨ ਵੇਚਣੀ ਹੈ:", size=11),
                                ft.Row([sell_kila, sell_kanal, sell_marla, sell_sarsai], wrap=True),
                                ft.FilledButton("ਹਿੱਸਾ ਕੱਢੋ (Get Fraction)", on_click=registry_sale_logic, bgcolor=ft.Colors.ORANGE),
                            ])
                        ),
                        
                        ft.Divider(),
                        sh_res_txt, 
                    ], spacing=15)
                )
            ]
        ),
                
       # 1. ਮੈਨੂਅਲ ਸੈਕਸ਼ਨ (Manual Entry) - Punjabi Display + Correct PDF Spelling
        ft.ExpansionTile(title=ft.Text("1. ਮੈਨੂਅਲ ਜੋੜੋ/ਘਟਾਓ (Kila/Kanal +/-)", weight="bold"), controls=[
            ft.Container(padding=10, content=ft.Column([
                ft.Row(man_f, wrap=True),
                ft.Row([
                    ft.FilledButton("ਜੋੜੋ (+)", bgcolor="green", 
                        on_click=lambda _: (
                            (lambda v, det_pdf: (
                                update_history(v, "Manual", det_pdf),
                                setattr(man_res_label, 'value', f"ਨਤੀਜਾ: {format_area_full(v)}")
                            ))((float(man_f[0].value or 0)*160 + float(man_f[1].value or 0)*20 + float(man_f[2].value or 0) + float(man_f[3].value or 0)/9),
                               # PDF ਲਈ English Units (ਸਪੈਲਿੰਗ ਗਲਤੀ ਠੀਕ ਕਰਨ ਲਈ)
                               f"{man_f[0].value or 0} Kila, {man_f[1].value or 0} Kanal, {man_f[2].value or 0} Marla, {man_f[3].value or 0} Sarsai"),
                            clear_fields(man_f), page.update()
                        )),
                    ft.FilledButton("ਘਟਾਓ (-)", bgcolor="red", 
                        on_click=lambda _: (
                            (lambda v, det_pdf: (
                                update_history(-v, "Manual", det_pdf),
                                setattr(man_res_label, 'value', f"ਨਤੀਜਾ: -{format_area_full(v)}")
                            ))((float(man_f[0].value or 0)*160 + float(man_f[1].value or 0)*20 + float(man_f[2].value or 0) + float(man_f[3].value or 0)/9),
                               # PDF ਲਈ English Units
                               f"{man_f[0].value or 0} Kila, {man_f[1].value or 0} Kanal, {man_f[2].value or 0} Marla, {man_f[3].value or 0} Sarsai"),
                            clear_fields(man_f), page.update()
                        ))
                ]),
                man_res_label, 
            ]))
        ]),

        # 2. ਨਕਸ਼ੇ ਅਤੇ ਹਿਸਾਬ (Maps +/-) - Punjabi Display + Correct PDF Spelling
        ft.ExpansionTile(title=ft.Text("2. ਨਕਸ਼ੇ ਅਤੇ ਹਿਸਾਬ (Maps +/-)", weight="bold"), controls=[
            ft.Container(padding=10, content=ft.Column([
                # --- Rectangle Section ---
                ft.Text("ਦੋ ਬਾਹੀਆਂ (Rectangle):", color="blue"),
                ft.Row(r1), ft.Row(r2),
                ft.Row([
                    ft.FilledButton("+", bgcolor="green", on_click=lambda _: (
                        (lambda s1, s2: (
                            (lambda v: (
                                update_history(v, "Rectangle", f"L: {from_karm(s1)}, W: {from_karm(s2)}"),
                                setattr(rect_res_label, 'value', f"ਨਤੀਜਾ: {format_area_full(v)}")
                            ))((s1*s2)/9)
                        ))(to_karm(*[f.value for f in r1]), to_karm(*[f.value for f in r2])),
                        clear_fields(r1+r2), page.update()
                    )),
                    ft.FilledButton("-", bgcolor="red", on_click=lambda _: (
                        (lambda s1, s2: (
                            (lambda v: (
                                update_history(-v, "Rectangle", f"L: {from_karm(s1)}, W: {from_karm(s2)}"),
                                setattr(rect_res_label, 'value', f"ਨਤੀਜਾ: -{format_area_full(v)}")
                            ))((s1*s2)/9)
                        ))(to_karm(*[f.value for f in r1]), to_karm(*[f.value for f in r2])),
                        clear_fields(r1+r2), page.update()
                    ))
                ]),
                rect_res_label, 
                ft.Divider(),
                
                # --- Triangle Section ---
                ft.Text("ਤਿੰਨ ਬਾਹੀਆਂ (Triangle):", color="blue"),
                ft.Row(t1), ft.Row(t2), ft.Row(t3),
                ft.Row([
                    ft.FilledButton("+", bgcolor="green", on_click=lambda _: (
                        (lambda s1, s2, s3: (
                            (lambda s: (
                                (lambda v: (
                                    update_history(v, "Triangle", f"S1: {from_karm(s1)}, S2: {from_karm(s2)}, S3: {from_karm(s3)}"),
                                    setattr(tri_res_label, 'value', f"ਨਤੀਜਾ: {format_area_full(v)}")
                                ))(math.sqrt(s*(s-s1)*(s-s2)*(s-s3))/9) if (s1+s2>s3 and s1+s3>s2 and s2+s3>s1) else setattr(tri_res_label, 'value', "ਤਿਕੋਣ ਨਹੀਂ ਬਣ ਸਕਦਾ!")
                            ))((s1+s2+s3)/2)
                        ))(to_karm(*[f.value for f in t1]), to_karm(*[f.value for f in t2]), to_karm(*[f.value for f in t3])),
                        clear_fields(t1+t2+t3), page.update()
                    )),
                    ft.FilledButton("-", bgcolor="red", on_click=lambda _: (
                        (lambda s1, s2, s3: (
                            (lambda s: (
                                (lambda v: (
                                    update_history(-v, "Triangle", f"S1: {from_karm(s1)}, S2: {from_karm(s2)}, S3: {from_karm(s3)}"),
                                    setattr(tri_res_label, 'value', f"ਨਤੀਜਾ: -{format_area_full(v)}")
                                ))(math.sqrt(s*(s-s1)*(s-s2)*(s-s3))/9) if (s1+s2>s3 and s1+s3>s2 and s2+s3>s1) else setattr(tri_res_label, 'value', "ਤਿਕੋਣ ਨਹੀਂ ਬਣ ਸਕਦਾ!")
                            ))((s1+s2+s3)/2)
                        ))(to_karm(*[f.value for f in t1]), to_karm(*[f.value for f in t2]), to_karm(*[f.value for f in t3])),
                        clear_fields(t1+t2+t3), page.update()
                    ))
                ]),
                tri_res_label, 
                ft.Divider(),
                
                # --- Four Sides Section ---
                ft.Text("ਚਾਰ ਬਾਹੀਆਂ (4-Side Avg):", color="blue"),
                ft.Row(c1), ft.Row(c2), ft.Row(c3), ft.Row(c4),
                ft.Row([
                    ft.FilledButton("+", bgcolor="green", on_click=lambda _: (
                        (lambda l1, l2, w1, w2: (
                            (lambda v: (
                                update_history(v, "4-Side Plot", f"L:({from_karm(l1)},{from_karm(l2)}), W:({from_karm(w1)},{from_karm(w2)})"),
                                setattr(quad_res_label, 'value', f"ਨਤੀਜਾ: {format_area_full(v)}")
                            ))(((l1+l2)/2 * (w1+w2)/2)/9)
                        ))(to_karm(*[f.value for f in c1]), to_karm(*[f.value for f in c2]), to_karm(*[f.value for f in c3]), to_karm(*[f.value for f in c4])),
                        clear_fields(c1+c2+c3+c4), page.update()
                    )),
                    ft.FilledButton("-", bgcolor="red", on_click=lambda _: (
                        (lambda l1, l2, w1, w2: (
                            (lambda v: (
                                update_history(-v, "4-Side Plot", f"L:({from_karm(l1)},{from_karm(l2)}), W:({from_karm(w1)},{from_karm(w2)})"),
                                setattr(quad_res_label, 'value', f"ਨਤੀਜਾ: -{format_area_full(v)}")
                            ))(((l1+l2)/2 * (w1+w2)/2)/9)
                        ))(to_karm(*[f.value for f in c1]), to_karm(*[f.value for f in c2]), to_karm(*[f.value for f in c3]), to_karm(*[f.value for f in c4])),
                        clear_fields(c1+c2+c3+c4), page.update()
                    ))
                ]),
                quad_res_label, 
            ]))
        ]),

       # 3. ਟੂਲਸ ਸੈਕਸ਼ਨ (Tools)
        ft.ExpansionTile(
            title=ft.Text("3. ਟੂਲਸ: ਗੁਨੀਆ ਅਤੇ ਗੁੰਮ ਬਾਹੀ (Tools)", weight="bold"), 
            controls=[
                ft.Container(
                    padding=10, 
                    content=ft.Column([
                        # --- ਗੁਨੀਆ ਸੈਕਸ਼ਨ (Diagonal) ---
                        ft.Text("ਗੁਨੀਆ ਚੈੱਕ ਕਰੋ (Diagonal):", weight="bold", color="blue"),

                        # ਇਹ ਦੋ ਲਾਈਨਾਂ ਤੁਹਾਡੇ ਬਾਕਸ ਦਿਖਾਉਣਗੀਆਂ
                        ft.Row(g1),  # ਪਹਿਲੀ ਬਾਹੀ (Side 1) ਦੇ 4 ਬਾਕਸ: K, F, I, S
                        ft.Row(g2),  # ਦੂਜੀ ਬਾਹੀ (Side 2) ਦੇ 4 ਬਾਕਸ: K, F, I, S

                        ft.Button("ਗੁਨੀਆ ਚੈੱਕ ਕਰੋ", on_click=lambda _: (
                            (lambda v1, v2: (
                                (lambda res_k: (
                                    setattr(gunya_res_label, 'value', f"ਗੁਨੀਆ: {pk(res_k)}"),
                                    update_history(0, "Tool: Diagonal", f"S1: {pk(v1)}, S2: {pk(v2)} -> Res: {pk(res_k)}", False),
                                    page.update()
                                ))(math.sqrt(v1**2 + v2**2))
                            ))(to_karm(*[f.value for f in g1]), to_karm(*[f.value for f in g2]))
                        )),
                        gunya_res_label,
                        ft.Divider(),

                        # --- ਗੁੰਮ ਬਾਹੀ ਸੈਕਸ਼ਨ ---
                        ft.Text("ਗੁੰਮ ਬਾਹੀ ਲੱਭੋ (Shafi Tool):", weight="bold", color="blue"),
                        ft.Text("1. ਜਿੰਨਾ ਰਕਬਾ ਪੂਰਾ ਕਰਨਾ ਹੈ (Target Area):", size=12),
                        ft.Row(sf_total), 
                        ft.Text("2. ਪਤਾ ਲੱਗ ਚੁੱਕੀਆਂ ਬਾਹੀਆਂ ਭਰੋ:", size=12),
                        ft.Text("ਲੰਬਾਈ 1:", size=11, italic=True), 
                        ft.Row(sf_b1),
                        ft.Text("ਲੰਬਾਈ 2 (ਤਿਕੋਣ ਜਾਂ ਚੌਂਠ ਲਈ):", size=11, italic=True), 
                        ft.Row(sf_b2),
                        sf_b2_res,
                        ft.Text("ਚੌੜਾਈ 1 (ਸਿਰਫ ਚੌਂਠ ਲਈ):", size=11, italic=True), 
                        ft.Row(sf_b3),
                        sf_b3_res,
                        
                        ft.Row([
                            ft.FilledButton("ਬਾਹੀ ਲੱਭੋ (Calculate)", on_click=find_missing_side, bgcolor="orange", width=200),
                        ]),
                        sf_b4_res,
                        
                        ft.Divider(height=10, color="transparent"),
                        ft.Button("ਹਿਸਟਰੀ 'ਚ ਸੇਵ ਕਰੋ", on_click=lambda _: (
                            page.overlay.append(ft.SnackBar(ft.Text("ਰਿਜ਼ਲਟ ਪਹਿਲਾਂ ਹੀ ਹਿਸਟਰੀ ਵਿੱਚ ਸੇਵ ਹੋ ਚੁੱਕਾ ਹੈ!"), open=True)),
                            page.update()
                        ))
                    ])
                )
            ]
        ), # <--- ਇਹ ਕਾਮਾ ਲਗਾਉਣਾ ਬਹੁਤ ਜ਼ਰੂਰੀ ਸੀ

        # 4. ਰਕਬਾ ਕਨਵਰਟਰ UI
        ft.ExpansionTile(
            title=ft.Text("4. ਰਕਬਾ ਕਨਵਰਟਰ (Unit Converter)", weight="bold", color="blue"), 
            controls=[
                ft.Container(
                    padding=15, 
                    content=ft.Column([
                        ft.Row([conv_input, conv_dropdown], wrap=True, alignment="center"),
                        ft.FilledButton("ਬਦਲੋ (Convert)", on_click=convert_units, bgcolor="blue", icon=ft.Icons.CALCULATE),
                        ft.Divider(),
                        conv_res 
                    ], horizontal_alignment="center")
                )
            ]
        ), # <--- ਇੱਥੇ ਵੀ ਕਾਮਾ ਲੱਗੇਗਾ

        ft.Divider(),
        
        # ਹਿਸਟਰੀ ਸੈਕਸ਼ਨ
        ft.Row([
            ft.Text("ਕੈਲਕੂਲੇਸ਼ਨ ਹਿਸਟਰੀ (History):", size=16, weight="bold"),
            ft.IconButton(
                ft.Icons.DELETE_SWEEP, 
                icon_color="red", 
                tooltip="Clear All", 
                on_click=lambda _: (calculation_history.controls.clear(), history_data.clear(), page.update())
            )
        ], alignment="spaceBetween"),
        
        calculation_history
    ) # <--- page.add ਦੀ ਬਰੈਕਟ ਬੰਦ

# ਐਪ ਨੂੰ ਚਲਾਉਣ ਲਈ
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550)