import flet as ft

def main(page: ft.Page):
    page.title = "PubQuiz Master"
    page.scroll = "always"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(ft.Image(src=f"assets/images/logoquiz.png", width=250, height=250))

    # Input for number of categories
    num_categories_input = ft.TextField(label="Liczba kategorii", width=200)
    correct_answer_input = ft.TextField(label="Poprawna odpowiedź do dogrywki", width=200)
    create_table_button = ft.ElevatedButton(text="Stwórz tabelę", on_click=lambda e: create_table(int(num_categories_input.value), correct_answer_input.value))
    
    page.add(num_categories_input, correct_answer_input, create_table_button)
    
    # Text to display the correct answer after sorting
    correct_answer_text = ft.Text("", color="blue", size=25, visible=False)
    
    def create_table(num_categories, correct_answer):
        nonlocal correct_answer_text
        # Clear previous table if exists
        page.controls.clear()

        page.add(ft.Image(src="assets/images/logoquiz.png", width=250, height=250))
        
        # Create table headers
        string = "Nazwa drużyny"
        name = string + " " * 35
        headers = ["Miejsce", name] + [f"Kategoria {i+1}" for i in range(num_categories)] + ["Dogrywka", "Suma punktów", ""]
        table = ft.DataTable(
            data_row_min_height = 75,
            data_row_max_height = 85,
            columns=[ft.DataColumn(ft.Text(header)) for header in headers],
            rows=[]
        )
        
        # Add initial row for input
        add_team_row(table, num_categories)
        
        # Add buttons below the table
        add_row_button = ft.ElevatedButton(text="Dodaj drużynę", on_click=lambda e: add_team_row(table, num_categories))
        sort_table_button = ft.ElevatedButton(text="Sortuj tabelę", on_click=lambda e: sort_table(table, correct_answer, correct_answer_text))
        
        page.add(correct_answer_text)  # Add the correct answer text above the table
        page.add(table, add_row_button, sort_table_button)
        page.update()

    def add_team_row(table, num_categories):
        # Tworzenie elementów wiersza
        place_text = ft.Text("", height=70, text_align="center")
        team_name_input = ft.TextField(width=400, height=70, text_align="center")
        category_inputs = [ft.TextField(width=150, height=70, text_align="center") for _ in range(num_categories)]
        tiebreaker_input = ft.TextField(width=150, height=70, text_align="center")
        total_score_text = ft.Text("0", size=25, height=70, text_align="center")
        delete_button = ft.IconButton(icon=ft.icons.DELETE_FOREVER_ROUNDED, on_click=lambda e: delete_row(table, row))

        # Utworzenie wiersza
        row = ft.DataRow(
            cells=[
                ft.DataCell(place_text),
                ft.DataCell(team_name_input),
                *[ft.DataCell(cat_input) for cat_input in category_inputs],
                ft.DataCell(tiebreaker_input),
                ft.DataCell(total_score_text),
                ft.DataCell(delete_button)
            ]
        )
        # Dodanie wiersza do tabeli
        table.rows.append(row)
        print("Dodano wiersz")
        
        # Dodanie nasłuchiwaczy do aktualizacji całkowitego wyniku
        for cat_input in category_inputs:
            cat_input.on_change = lambda e: update_total_score(row, num_categories)
        tiebreaker_input.on_change = lambda e: update_total_score(row, num_categories)
        
        # Aktualizacja strony
        page.update()

    def update_total_score(row, num_categories):
        category_scores = [int(cell.content.value) if cell.content.value else 0 for cell in row.cells[2:num_categories+2]]
        total_score = sum(category_scores)
        row.cells[-2].content.value = str(total_score)
        page.update()
    
    def sort_table(table, correct_answer, correct_answer_text):
        def get_tiebreaker_value(cell):
            return abs(int(cell.content.value) - int(correct_answer)) if cell.content.value else float('inf')
        
        # Sortowanie tabeli na podstawie sum punktów i wartości dogrywki
        table.rows.sort(key=lambda r: (int(r.cells[-2].content.value), -get_tiebreaker_value(r.cells[-3])), reverse=True)
        
        current_place = 1
        closest_non_podium = None

        # Sprawdzanie, czy wszystkie pola dogrywki są wypełnione
        all_tiebreaker_filled = True
        for row in table.rows:
            tiebreaker_value = row.cells[-3].content.value
            if not tiebreaker_value or not tiebreaker_value.strip():
                all_tiebreaker_filled = False
                break
        
        # Ustawianie miejsc i aktualizowanie widoku
        for i, row in enumerate(table.rows):
            if i > 0 and row.cells[-2].content.value == table.rows[i-1].cells[-2].content.value and get_tiebreaker_value(row.cells[-3]) == get_tiebreaker_value(table.rows[i-1].cells[-3]):
                if isinstance(table.rows[i-1].cells[0].content, ft.Image):
                    row.cells[0].content = ft.Image(src=table.rows[i-1].cells[0].content.src, width=50, height=50)
                else:
                    row.cells[0].content.value = table.rows[i-1].cells[0].content.value
            else:
                if current_place == 1:
                    row.cells[0].content = ft.Image(src="assets/images/1.png", width=70, height=70)
                elif current_place == 2:
                    row.cells[0].content = ft.Image(src="assets/images/2.png", width=60, height=60)
                elif current_place == 3:
                    row.cells[0].content = ft.Image(src="assets/images/3.png", width=50, height=50)
                else:
                    row.cells[0].content = ft.Text(value=str(current_place))
                    if closest_non_podium is None or get_tiebreaker_value(row.cells[-3]) < get_tiebreaker_value(table.rows[closest_non_podium].cells[-3]):
                        closest_non_podium = i
            current_place += 1 if i == 0 or row.cells[-2].content.value != table.rows[i-1].cells[-2].content.value or get_tiebreaker_value(row.cells[-3]) != get_tiebreaker_value(table.rows[i-1].cells[-3]) else 0

        if len(table.rows) > 3 and closest_non_podium is not None:
            table.rows[closest_non_podium].cells[0].content = ft.Image(src="assets/images/4.png", width=40, height=40)

        # Wyświetlanie komunikatu o dogrywce, jeśli wszystkie pola są wypełnione
        if all_tiebreaker_filled:
            correct_answer_text.value = f"Poprawna odpowiedź do dogrywki: {correct_answer}"
            correct_answer_text.visible = True
        else:
            correct_answer_text.visible = False

        page.update()


    def delete_row(table, row):
        table.rows.remove(row)
        page.update()

ft.app(target=main, assets_dir="assets")