import flet as ft


def main(page: ft.Page):
    page.title = "Calculadora"
    page.bgcolor = "#000000" # Fundo preto

    expressao = ""

    def clicar(e):
        nonlocal expressao
        tecla = e.control.content.value

        if tecla == "AC":
            expressao = ""
            display.value = "0"

        elif tecla == "=":
            try:
                resultado = eval(expressao.replace("X", "*").replace(",", "."))
                display.value = str(resultado)
                expressao = str(resultado)
            except:
                display.value = "Erro"
                expressao = ""

        else:
            expressao += tecla
            display.value = expressao

        page.update()

    display = ft.Text(
        value="0",
        size=48,
        color=ft.Colors.WHITE,
        text_align=ft.TextAlign.RIGHT
    )

    def botao(texto, cor, cor_texto=ft.Colors.WHITE):
        return ft.Container(
            content=ft.Text(texto, size=22, color=cor_texto),
            bgcolor=cor,
            alignment=ft.Alignment.CENTER,
            width=70,
            height=70,
            border_radius=35 ,
            on_click=clicar,
            ink=True
        )

    def botao_zero():
        return ft.Container(
            content=ft.Text("0", size=22, color=ft.Colors.WHITE),
            bgcolor="#333333",
            alignment=ft.Alignment.CENTER_LEFT,  # texto à esquerda
            padding=ft.Padding.only(left=28),  # espaço interno
            width=150,  # MAIS LARGO
            height=70,
            border_radius=35
        )

    display = ft.Text(value="0", size=48, color=ft.Colors.WHITE, text_align=ft.TextAlign.RIGHT)



    page.add(
        ft.Container(
            alignment=ft.Alignment.CENTER,  # Centraliza tudo na tela
            expand=True,
            content=ft.Column(
                    spacing=12,
                    controls=[
                             ft.Container(content=display,
                                          alignment=ft.Alignment.CENTER_RIGHT,
                                          padding=20,
                                          height=120),
                             ft.Row(
                                 [
                                     botao("AC", "#A5A5A5", ft.Colors.BLACK),
                                     botao("+/-", "#A5A5A5"),
                                     botao("%", "#A5A5A5"),
                                     botao("/", "#FF9500"),
                                 ],
                                 spacing=10,
                                 alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row(
                                [
                                    botao("7", "#333333"),
                                    botao("8", "#333333"),
                                    botao("9", "#333333"),
                                    botao("X", "#FF9500"),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER),
                            ft.Row(
                                [
                                    botao("4", "#333333"),
                                    botao("5", "#333333"),
                                    botao("6", "#333333"),
                                    botao("-", "#FF9500"),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row(
                                    [
                                        botao("1", "#333333"),
                                        botao("2", "#333333"),
                                        botao("3", "#333333"),
                                        botao("+", "#FF9500"),
                                    ],
                                    spacing=10,
                                    alignment=ft.MainAxisAlignment.CENTER),
                                    ft.Row(
                                        [
                                            botao_zero(),
                                            botao(",", "#333333"),
                                            botao("=", "#FF9500"),
                                        ],
                                        spacing=10,
                                        alignment=ft.MainAxisAlignment.CENTER)
                    ]
            )
        )

    )




ft.run(main,port=8088, host="0.0.0.0")
