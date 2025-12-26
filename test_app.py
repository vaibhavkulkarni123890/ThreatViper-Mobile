import flet as ft

def main(page: ft.Page):
    page.title = "CyberNova Test"
    page.add(ft.Text("Hello from CyberNova!", size=30))

ft.app(target=main)
