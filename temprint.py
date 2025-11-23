# import pdfkit
# import os
#
# def generate_invoice_pdf(customer_name, customer_phone, total_discount, existing_invitation,
#                          created_by_user_name, delivery_data=None, discount=0.0, output_file="invoice.pdf"):
#     logo_path = os.path.abspath(r"C:\מירי\מבט\assets\shop_bg.png")
#
#     subtotal = sum(i.get('line_total', 0) for i in existing_invitation["items"])
#     total_price = max(subtotal - total_discount - discount, 0)
#
#     # פונקציה לריבוע עם וי
#     def checkbox_html(value):
#         return f"""
#         <span style="
#             display:inline-block;
#             width:20px; height:20px;
#             border:2px solid #888;
#             border-radius:4px;
#             text-align:center;
#             line-height:18px;
#             font-size:14px;
#             color:#28a745;
#             margin-left:5px;
#         ">{'✓' if value else ''}</span>
#         """
#
#     html_content = f"""
#     <!DOCTYPE html>
#     <html lang="he" dir="rtl">
#     <head>
#     <meta charset="UTF-8">
#     <style>
#     @import url('https://fonts.googleapis.com/css2?family=Assistant&display=swap');
#     body {{
#         font-family: 'Assistant', Arial, sans-serif;
#         margin: 20px;
#         background-color: #ffffff;
#         color: #333;
#     }}
#     .header {{
#         text-align: center;
#         margin-bottom: 25px;
#     }}
#     .logo {{
#         width: 400px;
#         margin-bottom: 15px;
#     }}
#     .top-info-table {{
#         width: 100%;
#         margin-bottom: 20px;
#         border-collapse: collapse;
#     }}
#     .top-info-table td {{
#         vertical-align: top;
#         border: none;
#     }}
#     .status-label {{
#         font-weight: bold;
#         margin-bottom: 8px;
#         font-size: 16px;
#     }}
#     table {{
#         width: 100%;
#         border-collapse: collapse;
#         margin-top: 15px;
#     }}
#     th, td {{
#         border: 1px solid #eee;
#         padding: 10px;
#         text-align: center;
#     }}
#     th {{
#         background-color: #f28c7d;
#         color: white;
#     }}
#     tr:nth-child(even) {{ background-color: #f9f9f9; }}
#     tr:hover {{ background-color: #d2ebff; transition: 0.2s; }}
#     .total {{
#         text-align: left;
#         font-weight: bold;
#         font-size: 22px;
#         color: #d93025;
#         margin-top: 20px;
#     }}
#     .notes {{
#         margin-top: 15px;
#         padding: 12px;
#         background-color: #fff3cd;
#         border-left: 5px solid #ffeeba;
#         border-radius: 6px;
#         font-size: 14px;
#     }}
#     .delivery-card {{
#         border:2px solid #52b69a;
#         border-radius:8px;
#         padding:15px;
#         margin-top:25px;
#         background-color:#f9fffc;
#     }}
#     .delivery-card h3 {{
#         text-align:center;
#         color:#21867a;
#         margin-bottom:10px;
#     }}
#     .delivery-card table {{
#         width:100%;
#         border-collapse:collapse;
#         margin-top:10px;
#     }}
#     .delivery-card th, .delivery-card td {{
#         border:1px solid #eee;
#         padding:8px;
#         text-align:center;
#         font-size:14px;
#     }}
#     .delivery-card th {{
#         background-color:#52b69a;
#         color:white;
#     }}
#     </style>
#     </head>
#     <body>
#
#     <div class="header">
#         <img src="file:///{logo_path}" class="logo" />
#         <div>הזמנה מספר {existing_invitation.get('id')}</div>
#     </div>
#
#     <table class="top-info-table">
#         <tr>
#             <td style="text-align:right; font-weight:bold;">
#                 <div>לקוח: {customer_name}</div>
#                 <div>טלפון: {customer_phone}</div>
#                 <div>עובד: {created_by_user_name}</div>
#                 <div>תאריך: {existing_invitation.get('date', '').split('T')[0]}</div>
#                 <div>שעה: {existing_invitation.get('date', '').split('T')[1][:5] if 'T' in existing_invitation.get('date', '') else ''}</div>
#             </td>
#             <td style="text-align:left;">
#                 <div class="status-label">{checkbox_html(existing_invitation.get('answered',0))} ענו</div>
#                <div>בתאריך: {existing_invitation.get('answering_date', '').split('T')[0] if existing_invitation.get('answering_date') else '___________'}</div>
#                 <div class="status-label">{checkbox_html(existing_invitation.get('want_shipping',0))} משלוח</div>
#                 {f'<div class="status-label">{checkbox_html(existing_invitation.get("shipped",0))} נשלח</div>' if existing_invitation.get('want_shipping',0) else ''}
#             </td>
#         </tr>
#     </table>
#
#     <table>
#         <tr>
#             <th>#</th>
#             <th>מוצר</th>
#             <th>מידה</th>
#             <th>כמות</th>
#             <th>מחיר יח'</th>
#             <th>סה"כ</th>
#             <th>סופק</th>
#         </tr>
#     """
#
#     for i, item in enumerate(existing_invitation.get('items', [])):
#         supplied = item.get('supplied', 0)
#         ordered = item.get('quantity', 0)
#         if supplied == ordered:
#             supplied_display = "V"
#         else:
#             supplied_display = f"{supplied} מתוך {ordered}"
#         html_content += f"""
#         <tr>
#             <td>{i + 1}</td>
#             <td>{item['product_name']}</td>
#             <td>{item['size']}</td>
#             <td>{ordered}</td>
#             <td>{item['unit_price']:.2f} ₪</td>
#             <td>{item['line_total']:.2f} ₪</td>
#             <td>{supplied_display}</td>
#         </tr>
#         """
#
#     html_content += f"""
#     </table>
#
#     <p class="total">סה"כ: {subtotal:.2f} ₪ | לאחר הנחה: {total_price:.2f} ₪</p>
#     <div class="notes"><strong>הערות:</strong> {existing_invitation.get('notes') or "-"}</div>
#     """
#
#     # === הוספת פרטי משלוח אם קיימים ===
#     if delivery_data:
#         d = delivery_data
#         html_content += f"""
#         <div class="delivery-card">
#             <h3>פרטי משלוח #{d.get('id', '')} — {d.get('name', '')}</h3>
#             <table>
#                 <tr>
#                     <td>כתובת</td><td>{d.get('address','-')}</td>
#                 </tr>
#                 <tr> <td>טלפון 1</td><td>{d.get('phone1','-')}</td></tr>
#                 <tr>
#                     <td>טלפון 2</td><td>{d.get('phone2') or '-'}</td></tr>
#                     <tr> <td>שולם</td><td>{"כן" if d.get("paid") else "לא"}</td>
#                 </tr>
#                 <tr>
#                     <td>עד הבית</td><td>{"כן" if d.get("home_delivery") else "לא"}</td></tr>
#                     <tr> <td>תאריך</td><td>{d.get('created_at') or '-'}</td>
#                 </tr>
#                 <tr>
#                     <td colspan="4">הערות: {d.get('notes') or "-"}</td>
#                 </tr>
#             </table>
#         </div>
#         """
#
#     html_content += "</body></html>"
#
#     options = {'enable-local-file-access': ''}
#     config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#     pdfkit.from_string(html_content, output_file, configuration=config, options=options)
#     return output_file
import pdfkit
import os

def generate_invoice_pdf(customer_name, customer_phone, total_discount, existing_invitation,
                         created_by_user_name, delivery_data=None, discount=0.0, output_file="invoice.pdf"):
    logo_path = os.path.abspath(r"C:\מירי\מבט\assets\shop_bg.png")

    subtotal = sum(i.get('line_total', 0) for i in existing_invitation["items"])
    total_price = max(subtotal - total_discount - discount, 0)

    def checkbox_html(value):
        return f"<span style='display:inline-block;width:20px;height:20px;border:2px solid #888;border-radius:4px;text-align:center;line-height:18px;font-size:14px;color:#28a745;margin-left:5px;'>{'✓' if value else ''}</span>"

    # פרטי הזמנה
    left_html = f"""
    <div style="width:100%; height:50vh; border-bottom:1px dashed #000; box-sizing:border-box; padding:10px;">
        <div style="text-align:center;">
            <img src="file:///{logo_path}" style="width:300px;"/>
            <div>הזמנה מספר {existing_invitation.get('id')}</div>
        </div>
        <div style="font-weight:bold; margin-top:10px;">
            <div>לקוח: {customer_name}</div>
            <div>טלפון: {customer_phone}</div>
            <div>עובד: {created_by_user_name}</div>
            <div>תאריך: {existing_invitation.get('date','').split('T')[0]}</div>
            <div>שעה: {existing_invitation.get('date','').split('T')[1][:5] if 'T' in existing_invitation.get('date','') else ''}</div>
        </div>
        <table style="width:100%; border-collapse: collapse; margin-top:10px;">
            <tr>
                <th>#</th><th>מוצר</th><th>מידה</th><th>כמות</th><th>מחיר יח'</th><th>סה"כ</th><th>סופק</th>
            </tr>
    """

    for i, item in enumerate(existing_invitation.get('items', [])):
        supplied = item.get('supplied',0)
        ordered = item.get('quantity',0)
        supplied_display = "V" if supplied==ordered else f"{supplied} מתוך {ordered}"
        left_html += f"""
            <tr>
                <td>{i+1}</td>
                <td>{item['product_name']}</td>
                <td>{item['size']}</td>
                <td>{ordered}</td>
                <td>{item['unit_price']:.2f} ₪</td>
                <td>{item['line_total']:.2f} ₪</td>
                <td>{supplied_display}</td>
            </tr>
        """

    left_html += f"""
        </table>
        <p style="font-weight:bold; font-size:18px; margin-top:10px;">סה"כ: {subtotal:.2f} ₪ | לאחר הנחה: {total_price:.2f} ₪</p>
        <div style="margin-top:5px; padding:5px; background-color:#fff3cd; border-left:5px solid #ffeeba;">
            <strong>הערות:</strong> {existing_invitation.get('notes','-')}
        </div>
    </div>
    """

    # פרטי משלוח בחצי התחתון, מסובבים 180°
    right_html = ""
    if delivery_data:
        d = delivery_data
        right_html = f"""
        <div style="width:100%; height:50vh; transform: rotate(180deg); transform-origin: center center; box-sizing:border-box; padding:10px; background-color:#f9fffc; border-top:1px dashed #000;">
            <h3 style="text-align:center; color:#21867a;">פרטי משלוח #{d.get('id','')}</h3>
            <div><strong>שם:</strong> {d.get('name','-')}</div>
            <div><strong>כתובת:</strong> {d.get('address','-')}</div>
            <div><strong>טלפון 1:</strong> {d.get('phone1','-')}</div>
            <div><strong>טלפון 2:</strong> {d.get('phone2','-')}</div>
            <div><strong>שולם:</strong> {"כן" if d.get("paid") else "לא"}</div>
            <div><strong>עד הבית:</strong> {"כן" if d.get("home_delivery") else "לא"}</div>
            <div><strong>תאריך:</strong> {d.get('created_at','-')}</div>
            <div style="margin-top:5px;"><strong>הערות:</strong> {d.get('notes','-')}</div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
<<<<<<< HEAD
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Assistant', Arial, sans-serif; margin:0; padding:0; }}
        </style>
    </head>
    <body>
        {left_html}
        {right_html}
    </body>
    </html>
=======
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
        width: 400px;
        margin-bottom: 15px;
    }}
    .top-info-table {{
        width: 100%;
        margin-bottom: 20px;
        border-collapse: collapse;
    }}
    .top-info-table td {{
        vertical-align: top;
        border: none;
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
    .delivery-card {{
        border:2px solid #52b69a;
        border-radius:8px;
        padding:15px;
        margin-top:25px;
        background-color:#f9fffc;
    }}
    .delivery-card h3 {{
        text-align:center;
        color:#21867a;
        margin-bottom:10px;
    }}
    .delivery-card table {{
        width:100%;
        border-collapse:collapse;
        margin-top:10px;
    }}
    .delivery-card th, .delivery-card td {{
        border:1px solid #eee;
        padding:8px;
        text-align:center;
        font-size:14px;
    }}
    .delivery-card th {{
        background-color:#52b69a;
        color:white;
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
            <td style="text-align:right; font-weight:bold;">
                <div>לקוח: {customer_name}</div>
                <div>טלפון: {customer_phone}</div>
                <div>עובד: {created_by_user_name}</div>
                <div>תאריך: {existing_invitation.get('date', '').split('T')[0]}</div>
                <div>שעה: {existing_invitation.get('date', '').split('T')[1][:5] if 'T' in existing_invitation.get('date', '') else ''}</div>
            </td>
            <td style="text-align:left;">
                <div class="status-label">{checkbox_html(existing_invitation.get('answered',0))} ענו</div>
               <div>בתאריך: {existing_invitation.get('answering_date', '').split('T')[0] if existing_invitation.get('answering_date') else '___________'}</div>
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

    for i, item in enumerate(existing_invitation.get('items', [])):
        supplied = item.get('supplied', 0)
        ordered = item.get('quantity', 0)
        if supplied == ordered:
            supplied_display = "V"
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
>>>>>>> origin/main
    """

    # === הוספת פרטי משלוח אם קיימים ===
    if delivery_data:
        d = delivery_data
        html_content += f"""
        <div class="delivery-card">
            <h3>פרטי משלוח #{d.get('id', '')} — {d.get('name', '')}</h3>
            <table>
                <tr>
                    <td>כתובת</td><td>{d.get('address','-')}</td>
                </tr>
                <tr> <td>טלפון 1</td><td>{d.get('phone1','-')}</td></tr>
                <tr>
                    <td>טלפון 2</td><td>{d.get('phone2') or '-'}</td></tr>
                    <tr> <td>שולם</td><td>{"כן" if d.get("paid") else "לא"}</td>
                </tr>
                <tr>
                    <td>עד הבית</td><td>{"כן" if d.get("home_delivery") else "לא"}</td></tr>
                    <tr> <td>תאריך</td><td>{d.get('created_at') or '-'}</td>
                </tr>
                <tr>
                    <td colspan="4">הערות: {d.get('notes') or "-"}</td>
                </tr>
            </table>
        </div>
        """

    html_content += "</body></html>"

    options = {'enable-local-file-access': ''}
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdfkit.from_string(html_content, output_file, configuration=config, options=options)
    return output_file
