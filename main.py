import flet as ft
import requests

DEFAULT_SERVER = "http://192.168.1.15:8000"  # သို့မဟုတ် Cloudflare Link

ROOMS_A = [f"A-1{i:02d}" for i in range(1, 11)] + [f"A-2{i:02d}" for i in range(1, 11)]
ROOMS_B = [f"B-1{i:02d}" for i in range(1, 11)] + [f"B-2{i:02d}" for i in range(1, 11)]
ALL_ROOMS = ROOMS_A + ROOMS_B


def main(page: ft.Page):
    page.title = "မီတာခ စီမံခန့်ခွဲမှုစနစ် (Mobile App)"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = 16

    # Inputs dictionary
    inputs_prev = {}
    inputs_curr = {}

    server_url_field = ft.TextField(
        label="Server URL (LAN IP သို့မဟုတ် Cloudflare Link)",
        value=DEFAULT_SERVER,
        dense=True,
    )

    prev_date_field = ft.TextField(label="ယခင်လ ရက်စွဲ", width=160, dense=True)
    curr_date_field = ft.TextField(label="ယခုလ ရက်စွဲ", width=160, dense=True)

    status_txt = ft.Text(value="", color=ft.Colors.GREEN_400)

    def show_snack(msg: str, color=ft.Colors.BLUE_400):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def sync_data(e=None):
        base_url = server_url_field.value.strip().rstrip("/")
        try:
            res = requests.get(f"{base_url}/api/active-session", timeout=4.0)
            if res.status_code == 200:
                data = res.json()
                prev_date_field.value = data.get("prev_date", "")
                curr_date_field.value = data.get("curr_date", "")
                readings = data.get("readings", {})
                for r in ALL_ROOMS:
                    info = readings.get(r, {"prev": 0.0, "curr": 0.0})
                    if r in inputs_prev:
                        inputs_prev[r].value = str(info.get("prev", 0.0))
                    if r in inputs_curr:
                        inputs_curr[r].value = str(info.get("curr", 0.0))
                show_snack("✅ Server မှ ဒေတာများ အောင်မြင်စွာ ရယူပြီးပါပြီ။")
            else:
                show_snack("❌ Server မှ ဒေတာရယူမရပါ", ft.Colors.RED_400)
        except Exception as err:
            show_snack(f"ချိတ်ဆက်မရပါ: {err}", ft.Colors.RED_400)
        page.update()

    def save_data(e=None):
        base_url = server_url_field.value.strip().rstrip("/")
        readings = {}
        for r in ALL_ROOMS:
            try:
                p_val = float(inputs_prev[r].value or 0)
                c_val = float(inputs_curr[r].value or 0)
            except ValueError:
                p_val, c_val = 0.0, 0.0
            readings[r] = {"prev": p_val, "curr": c_val}

        payload = {
            "prev_date": prev_date_field.value.strip(),
            "curr_date": curr_date_field.value.strip(),
            "readings": readings,
        }

        try:
            res = requests.post(f"{base_url}/api/save-to-history", json=payload, timeout=4.0)
            if res.status_code == 200:
                show_snack("🎉 Database ထဲသို့ ဒေတာများ သိမ်းဆည်းပြီးပါပြီ။", ft.Colors.GREEN_600)
            else:
                show_snack("❌ သိမ်းဆည်းရာတွင် အမှားရှိပါသည်", ft.Colors.RED_400)
        except Exception as err:
            show_snack(f"Server သို့ မပို့နိုင်ပါ: {err}", ft.Colors.RED_400)
        page.update()

    # Room list builder
    def build_room_cards(room_list):
        controls = []
        for r in room_list:
            p_in = ft.TextField(label="ယခင်", width=95, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
            c_in = ft.TextField(label="ယခု", width=95, dense=True, keyboard_type=ft.KeyboardType.NUMBER)
            inputs_prev[r] = p_in
            inputs_curr[r] = c_in

            card = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(r, weight=ft.FontWeight.BOLD, width=65),
                        p_in,
                        c_in,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=6,
                border_radius=8,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                margin=ft.margin.only(bottom=4),
            )
            controls.append(card)
        return ft.Column(controls)

    # UI Layout
    page.add(
        ft.Text("⚡ လှိုင်သာယာ မီတာခ စီမံခန့်ခွဲမှု", size=20, weight=ft.FontWeight.BOLD),
        server_url_field,
        ft.Row([prev_date_field, curr_date_field], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row(
            [
                ft.ElevatedButton("🔄 Server မှ ဒေတာဆွဲမည်", on_click=sync_data, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
                ft.ElevatedButton("💾 Save သိမ်းမည်", on_click=save_data, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Divider(),
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="တိုက် (A) အခန်း ၂၀", content=build_room_cards(ROOMS_A)),
                ft.Tab(text="တိုက် (B) အခန်း ၂၀", content=build_room_cards(ROOMS_B)),
            ],
            expand=True,
        ),
    )

    # စဖွင့်ချင်း ဒေတာဆွဲယူခြင်း
    sync_data()


if __name__ == "__main__":
    ft.app(target=main)