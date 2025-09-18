import flet as ft


def CalculatorScreen(page, user, navigator):
    page.title = "מחשבון"


    result_field = ft.TextField(
        value="",
        text_align=ft.TextAlign.RIGHT,
        width=250,
        read_only=True,
        text_size=24
    )

    def append_number(e):
        result_field.value += e.control.data
        result_field.update()

    def clear_result(e):
        result_field.value = ""
        result_field.update()

    def calculate_result(e):
        try:
            result_field.value = str(eval(result_field.value))
        except:
            result_field.value = "שגיאה"
        result_field.update()


    button_layout = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "C", "+"],
        ["="]
    ]

    rows = []
    for row in button_layout:
        row_buttons = []
        for label in row:
            if label == "C":
                btn = ft.ElevatedButton(label, width=60, height=60, on_click=clear_result)
            elif label == "=":
                btn = ft.ElevatedButton(label, width=60, height=60, on_click=calculate_result)
            else:
                btn = ft.ElevatedButton(label, width=60, height=60, data=label, on_click=append_number)
            row_buttons.append(btn)
        rows.append(ft.Row(controls=row_buttons, spacing=5, alignment=ft.MainAxisAlignment.CENTER))


    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                result_field,
                ft.Column(controls=rows, spacing=5),
                ft.ElevatedButton(
                    "חזרה לבית",
                    on_click=lambda e: navigator.go_home(user),
                    width=120,
                    bgcolor="#52b69a",
                    color=ft.Colors.WHITE
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )
    page.update()
