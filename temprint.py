import pdfkit
import os

def generate_invoice_pdf(customer_name, customer_phone, total_discount, existing_invitation,
                          created_by_user_name, discount=0.0, output_file="invoice.pdf"):
    logo_path = os.path.abspath(r"C:\מירי\מבט\assets\shop_bg.png")

    subtotal = sum(i.get('line_total', 0) for i in existing_invitation["items"])
    total_price = max(subtotal - total_discount - discount, 0)

    # פונקציה לריבוע עם וי
    def checkbox_html(value):
        return f"""
        <span style="
            display:inline-block;
            width:20px; height:20px;
            border:2px solid #888;
            border-radius:4px;
            text-align:center;
            line-height:18px;
            font-size:14px;
            color:#28a745;
            margin-left:5px;
        ">{'✓' if value else ''}</span>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
    <meta charset="UTF-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant&display=swap');
    body {{
        font-family: 'Assistant', Arial, sans-serif;
        margin: 20px;
        background-color: #ffffff;
        color: #333;
    }}
    .header {{
        text-align: center;
        margin-bottom: 25px;
    }}
    .logo {{
        width: 400px; /* לוגו גדול יותר */
        margin-bottom: 15px;
    }}

    /* טבלה עליונה */
    .top-info-table {{
        width: 100%;
        margin-bottom: 20px;
        border-collapse: collapse;
    }}
    .top-info-table td {{
        vertical-align: top;
        border: none; /* גבולות בצבע הרקע */
    }}

    .status-label {{
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 16px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }}
    th, td {{
        border: 1px solid #eee;
        padding: 10px;
        text-align: center;
    }}
    th {{
        background-color: #f28c7d;
        color: white;
    }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    tr:hover {{ background-color: #d2ebff; transition: 0.2s; }}

    .total {{
        text-align: left;
        font-weight: bold;
        font-size: 22px;
        color: #d93025;
        margin-top: 20px;
    }}
    .notes {{
        margin-top: 15px;
        padding: 12px;
        background-color: #fff3cd;
        border-left: 5px solid #ffeeba;
        border-radius: 6px;
        font-size: 14px;
    }}
    </style>
    </head>
    <body>

    <div class="header">
        <img src="file:///{logo_path}" class="logo" />
        <div>הזמנה מספר {existing_invitation.get('id')}</div>
    </div>

    <table class="top-info-table">
        <tr>
            <!-- פרטים בצד ימין -->
            <td style="text-align:right; font-weight:bold;">
                <div>לקוח: {customer_name}</div>
                <div>טלפון: {customer_phone}</div>
                <div>עובד: {created_by_user_name}</div>
                <div>תאריך: {existing_invitation.get('date', '').split('T')[0]}</div>
                <div>שעה: {existing_invitation.get('date', '').split('T')[1][:5] if 'T' in existing_invitation.get('date', '') else ''}</div>
            </td>

            <!-- סטטוס בצד שמאל -->
            <td style="text-align:left;">
                <div class="status-label">{checkbox_html(existing_invitation.get('answered',0))} ענו</div>
                <div class="status-label">{checkbox_html(existing_invitation.get('want_shipping',0))} משלוח</div>
                {f'<div class="status-label">{checkbox_html(existing_invitation.get("shipped",0))} נשלח</div>' if existing_invitation.get('want_shipping',0) else ''}
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <th>#</th>
            <th>מוצר</th>
            <th>מידה</th>
            <th>כמות</th>
            <th>מחיר יח'</th>
            <th>סה"כ</th>
            <th>סופק</th>
        </tr>
    """

    for i, item in enumerate(existing_invitation.get('items')):
        supplied = item.get('supplied', 0)
        ordered = item.get('qty', 0)
        if supplied == ordered:
            supplied_display = "✔️"
        else:
            supplied_display = f"{supplied} מתוך {ordered}"
        html_content += f"""
        <tr>
            <td>{i + 1}</td>
            <td>{item['product_name']}</td>
            <td>{item['size']}</td>
            <td>{ordered}</td>
            <td>{item['unit_price']:.2f} ₪</td>
            <td>{item['line_total']:.2f} ₪</td>
            <td>{supplied_display}</td>
        </tr>
        """

    html_content += f"""
    </table>

    <p class="total">סה"כ: {subtotal:.2f} ₪ | לאחר הנחה: {total_price:.2f} ₪</p>
    <div class="notes"><strong>הערות:</strong> {existing_invitation.get('notes') or "-"}</div>

    </body>
    </html>
    """

    options = {'enable-local-file-access': ''}
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_string(html_content, output_file, configuration=config, options=options)
    return output_file
