import flet as ft
from datetime import datetime, timedelta
import json
import random

def main(page: ft.Page):
    page.title = "Smart Home Controller Pro"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Global state
    current_user = {'username': 'User', 'role': 'admin'}
    dark_mode = ft.Ref[ft.Switch]()
    
    # Device state with rooms
    devices = {
        'light1': {'name': 'Living Room Light', 'type': 'light', 'state': False, 'room': 'Living Room', 'power': 60},
        'light2': {'name': 'Bedroom Light', 'type': 'light', 'state': False, 'room': 'Bedroom', 'power': 40},
        'door1': {'name': 'Front Door', 'type': 'door', 'state': True, 'room': 'Entrance', 'power': 5},
        'camera1': {'name': 'Front Camera', 'type': 'camera', 'state': True, 'room': 'Entrance', 'power': 10},
        'fan1': {'name': 'Bedroom Fan', 'type': 'fan', 'value': 0, 'room': 'Bedroom', 'power': 75},
        'thermostat1': {'name': 'Living Room Thermostat', 'type': 'thermostat', 'value': 22.0, 'room': 'Living Room', 'power': 150},
    }
    
    # Action log with more details
    action_log = [
        {'time': datetime.now() - timedelta(hours=2), 'device': 'light1', 'action': 'Turn ON', 'user': 'admin', 'room': 'Living Room'}
    ]
    
    # Automation rules
    automation_rules = [
        {'id': 1, 'name': 'Evening Lights', 'time': '18:00', 'device': 'light1', 'action': 'Turn ON', 'enabled': True},
        {'id': 2, 'name': 'Night Mode', 'time': '22:00', 'device': 'light1', 'action': 'Turn OFF', 'enabled': True},
    ]
    
    # Notifications
    notifications = []
    
    # Energy data for charts (simulated hourly consumption)
    energy_data = [random.randint(50, 200) for _ in range(24)]
    
    def get_theme_colors():
        if page.theme_mode == ft.ThemeMode.DARK:
            return {
                'bg': "#1a1a1a",
                'card': "#2d2d2d",
                'text': "#ffffff",
                'text_secondary': "#b0b0b0",
                'border': "#404040",
                'nav': "#252525",
                'accent': "#3b82f6"
            }
        else:
            return {
                'bg': "#f5f5f5",
                'card': "#ffffff",
                'text': "#1f2937",
                'text_secondary': "#6b7280",
                'border': "#e5e7eb",
                'nav': "#ffffff",
                'accent': "#2563eb"
            }
    
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.bgcolor = get_theme_colors()['bg']
        refresh_current_page()
    
    def log_action(device_id, action):
        now = datetime.now()
        action_log.insert(0, {
            'time': now,
            'device': device_id,
            'action': action,
            'user': current_user['username'],
            'room': devices[device_id]['room']
        })
        
        # Add notification
        add_notification(f"{devices[device_id]['name']}: {action}", "info")
    
    def add_notification(message, type="info"):
        notifications.insert(0, {
            'time': datetime.now(),
            'message': message,
            'type': type
        })
        if len(notifications) > 50:
            notifications.pop()
    
    def toggle_device(e):
        device_id = e.control.data
        devices[device_id]['state'] = not devices[device_id]['state']
        device = devices[device_id]
        
        if device['type'] == 'light':
            action = 'Turn ON' if device['state'] else 'Turn OFF'
        elif device['type'] == 'door':
            action = 'Lock' if device['state'] else 'Unlock'
        elif device['type'] == 'camera':
            action = 'Enable' if device['state'] else 'Disable'
        
        log_action(device_id, action)
        refresh_current_page()
    
    def on_slider_change(e):
        device_id = e.control.data
        value = float(e.control.value)
        devices[device_id]['value'] = value
        refresh_current_page()
    
    def on_slider_end(e):
        device_id = e.control.data
        value = devices[device_id]['value']
        device = devices[device_id]
        
        if device['type'] == 'thermostat':
            action = f"Set to {value:.1f}°C"
        else:
            action = f"Set speed to {int(value)}"
        
        log_action(device_id, action)
    
    current_page_state = {'page': 'overview'}
    
    def refresh_current_page():
        page_name = current_page_state['page']
        if page_name == 'overview':
            show_overview()
        elif page_name == 'statistics':
            show_statistics()
        elif page_name == 'automation':
            show_automation()
        elif page_name == 'notifications':
            show_notifications()
        elif page_name.startswith('details_'):
            device_id = page_name.split('_')[1]
            show_details(device_id)
        elif page_name.startswith('room_'):
            room = page_name.split('_', 1)[1]
            show_room(room)
    
    def create_nav_bar(current_page_name):
        colors = get_theme_colors()
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("🏠 Smart Home Pro", color=colors['text'], size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Text(f"👤 {current_user['username']}", color=colors['text_secondary'], size=14),
                            ft.Switch(
                                ref=dark_mode,
                                label="🌙",
                                value=page.theme_mode == ft.ThemeMode.DARK,
                                on_change=toggle_theme,
                                active_color=colors['accent']
                            )
                        ], spacing=10)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15,
                    bgcolor=colors['nav'],
                ),
                ft.Container(
                    content=ft.Row([
                        ft.TextButton(
                            "Overview",
                            on_click=lambda e: show_overview(),
                            style=ft.ButtonStyle(
                                color=colors['accent'] if current_page_name == "overview" else colors['text_secondary']
                            )
                        ),
                        ft.TextButton(
                            "Rooms",
                            on_click=lambda e: show_rooms(),
                            style=ft.ButtonStyle(
                                color=colors['accent'] if current_page_name == "rooms" else colors['text_secondary']
                            )
                        ),
                        ft.TextButton(
                            "Statistics",
                            on_click=lambda e: show_statistics(),
                            style=ft.ButtonStyle(
                                color=colors['accent'] if current_page_name == "statistics" else colors['text_secondary']
                            )
                        ),
                        ft.TextButton(
                            "Automation",
                            on_click=lambda e: show_automation(),
                            style=ft.ButtonStyle(
                                color=colors['accent'] if current_page_name == "automation" else colors['text_secondary']
                            )
                        ),
                        ft.TextButton(
                            "Notifications",
                            on_click=lambda e: show_notifications(),
                            style=ft.ButtonStyle(
                                color=colors['accent'] if current_page_name == "notifications" else colors['text_secondary']
                            )
                        ),
                    ], spacing=5),
                    padding=ft.padding.only(left=15, right=15, bottom=10),
                    bgcolor=colors['nav'],
                    border=ft.border.only(bottom=ft.BorderSide(1, colors['border']))
                ),
            ], spacing=0),
            bgcolor=colors['nav'],
        )

    def get_device_icon(device_type):
        icons = {
            'light': '💡',
            'door': '🚪',
            'thermostat': '🌡️',
            'fan': '🌀',
            'camera': '📹'
        }
        return icons.get(device_type, '📱')
    
    def get_device_color(device_type):
        colors_map = {
            'light': "#fef3c7",
            'door': "#f3f4f6",
            'thermostat': "#fce7f3",
            'fan': "#dbeafe",
            'camera': "#d1fae5"
        }
        if page.theme_mode == ft.ThemeMode.DARK:
            colors_map = {
                'light': "#3d3520",
                'door': "#2d2d2d",
                'thermostat': "#3d2535",
                'fan': "#1e3a5f",
                'camera': "#1e3d2f"
            }
        return colors_map.get(device_type, "#f3f4f6")
    
    def create_device_card(device_id, device, show_room=False):
        colors = get_theme_colors()
        bgcolor = get_device_color(device['type'])
        
        if device['type'] in ['light', 'door', 'camera']:
            status = device['state']
            if device['type'] == 'light':
                status_text = "ON" if status else "OFF"
                button_text = "Turn OFF" if status else "Turn ON"
                subtitle = "Tap to switch"
            elif device['type'] == 'door':
                status_text = "LOCKED" if status else "UNLOCKED"
                button_text = "Unlock" if status else "Lock"
                subtitle = "Tap to lock/unlock"
            else:  # camera
                status_text = "ACTIVE" if status else "DISABLED"
                button_text = "Disable" if status else "Enable"
                subtitle = "Tap to enable/disable"
            
            icon_text = get_device_icon(device['type'])
            
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(icon_text, size=28),
                        ft.Column([
                            ft.Text(device['name'], size=16, weight=ft.FontWeight.BOLD, color=colors['text']),
                            ft.Text(f"Room: {device['room']}" if show_room else device['room'], 
                                   size=12, color=colors['text_secondary']),
                        ], spacing=2, expand=True),
                    ], spacing=10),
                    ft.Divider(height=1, color=colors['border']),
                    ft.Text(f"Status: {status_text}", color=colors['text'], weight=ft.FontWeight.W_500),
                    ft.Text(subtitle, size=12, color=colors['text_secondary']),
                    ft.Text(f"Power: {device['power']}W", size=11, color=colors['text_secondary']),
                    ft.Row([
                        ft.TextButton(
                            "Details",
                            data=device_id,
                            on_click=lambda e: show_details(e.control.data),
                            style=ft.ButtonStyle(color=colors['accent'])
                        ),
                        ft.ElevatedButton(
                            button_text,
                            data=device_id,
                            on_click=toggle_device,
                            bgcolor=colors['accent'],
                            color="#ffffff",
                        ),
                    ], spacing=10),
                ], spacing=8),
                padding=20,
                bgcolor=bgcolor,
                border_radius=12,
                width=320,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.1, "#000000"),
                    offset=ft.Offset(0, 2),
                )
            )
        else:  # slider devices
            value = device['value']
            if device['type'] == 'thermostat':
                value_text = f"{value:.1f}°C"
                subtitle = "Adjust temperature"
                min_val, max_val, divisions = 15, 30, 30
            else:  # fan
                value_text = f"Speed {int(value)}"
                subtitle = "0=OFF, 3=MAX"
                min_val, max_val, divisions = 0, 3, 3
            
            icon_text = get_device_icon(device['type'])
            
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(icon_text, size=28),
                        ft.Column([
                            ft.Text(device['name'], size=16, weight=ft.FontWeight.BOLD, color=colors['text']),
                            ft.Text(f"Room: {device['room']}" if show_room else device['room'], 
                                   size=12, color=colors['text_secondary']),
                        ], spacing=2, expand=True),
                    ], spacing=10),
                    ft.Divider(height=1, color=colors['border']),
                    ft.Text(f"Current: {value_text}", color=colors['text'], weight=ft.FontWeight.W_500),
                    ft.Text(subtitle, size=12, color=colors['text_secondary']),
                    ft.Text(f"Power: {device['power']}W", size=11, color=colors['text_secondary']),
                    ft.Slider(
                        min=min_val,
                        max=max_val,
                        divisions=divisions,
                        value=value,
                        data=device_id,
                        on_change=on_slider_change,
                        on_change_end=on_slider_end,
                        active_color=colors['accent'],
                    ),
                    ft.TextButton(
                        "Details",
                        data=device_id,
                        on_click=lambda e: show_details(e.control.data),
                        style=ft.ButtonStyle(color=colors['accent'])
                    ),
                ], spacing=8),
                padding=20,
                bgcolor=bgcolor,
                border_radius=12,
                width=320,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.1, "#000000"),
                    offset=ft.Offset(0, 2),
                )
            )
    
    def show_login():
        current_page_state['page'] = 'login'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        username_field = ft.TextField(
            label="Username",
            hint_text="admin, user, or guest",
            width=300,
            border_color=colors['accent']
        )
        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            hint_text="Enter password",
            width=300,
            border_color=colors['accent']
        )
        error_text = ft.Text("", color=ft.Colors.RED, size=12)
        
        def do_login(e):
            username = username_field.value
            password = password_field.value
            
            if username in users_db and users_db[username]['password'] == password:
                current_user['username'] = username
                current_user['role'] = users_db[username]['role']
                add_notification(f"Welcome back, {username}!", "success")
                show_overview()
            else:
                error_text.value = "Invalid username or password"
                page.update()
        
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Container(height=50),
                    ft.Text("🏠 Smart Home Controller Pro", 
                           size=32, 
                           weight=ft.FontWeight.BOLD,
                           color=colors['text']),
                    ft.Text("Secure Login", size=18, color=colors['text_secondary']),
                    ft.Container(height=30),
                    ft.Container(
                        content=ft.Column([
                            username_field,
                            password_field,
                            error_text,
                            ft.ElevatedButton(
                                "Login",
                                width=300,
                                on_click=do_login,
                                bgcolor=colors['accent'],
                                color="#ffffff",
                                height=45
                            ),
                            ft.Container(height=10),
                            ft.Text("Demo accounts:", size=12, color=colors['text_secondary']),
                            ft.Text("admin/admin123, user/user123, guest/guest123", 
                                   size=11, color=colors['text_secondary']),
                        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        bgcolor=colors['card'],
                        border_radius=12,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.Colors.with_opacity(0.2, "#000000"),
                        )
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                alignment=ft.alignment.center
            )
        )
        page.update()

    def show_overview():
        current_page_state['page'] = 'overview'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        # Calculate total power consumption
        total_power = 0
        active_devices = 0
        for device in devices.values():
            if device['type'] in ['light', 'door', 'camera']:
                if device['state']:
                    total_power += device['power']
                    active_devices += 1
            else:
                if device['value'] > 0:
                    total_power += device['power'] * (device['value'] / (30 if device['type'] == 'thermostat' else 3))
                    active_devices += 1
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("overview"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Dashboard Overview", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        
                        # Stats cards
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Active Devices", size=14, color=colors['text_secondary']),
                                    ft.Text(str(active_devices), size=32, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=20,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, 
                                                   color=ft.Colors.with_opacity(0.1, "#000000"))
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Total Power", size=14, color=colors['text_secondary']),
                                    ft.Text(f"{total_power:.0f}W", size=32, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=20,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, 
                                                   color=ft.Colors.with_opacity(0.1, "#000000"))
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Total Devices", size=14, color=colors['text_secondary']),
                                    ft.Text(str(len(devices)), size=32, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=20,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                                shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, 
                                                   color=ft.Colors.with_opacity(0.1, "#000000"))
                            ),
                        ], spacing=15),
                        
                        ft.Container(height=20),
                        ft.Text("All Devices", size=22, weight=ft.FontWeight.BOLD, color=colors['text']),
                        
                        ft.Row([
                            create_device_card(device_id, device, show_room=True)
                            for device_id, device in devices.items()
                        ], spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                        
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    def show_rooms():
        current_page_state['page'] = 'rooms'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        # Group devices by room
        rooms = {}
        for device_id, device in devices.items():
            room = device['room']
            if room not in rooms:
                rooms[room] = []
            rooms[room].append((device_id, device))
        
        room_cards = []
        for room, room_devices in rooms.items():
            device_count = len(room_devices)
            active_count = sum(1 for _, d in room_devices 
                             if (d['type'] in ['light', 'door', 'camera'] and d['state']) 
                             or (d['type'] in ['thermostat', 'fan'] and d['value'] > 0))
            
            room_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"📍 {room}", size=20, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ft.Text(f"{device_count} devices", size=14, color=colors['text_secondary']),
                        ft.Text(f"{active_count} active", size=14, color=colors['accent']),
                        ft.ElevatedButton(
                            "View Room",
                            data=room,
                            on_click=lambda e: show_room(e.control.data),
                            bgcolor=colors['accent'],
                            color="#ffffff"
                        )
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.START),
                    padding=25,
                    bgcolor=colors['card'],
                    border_radius=12,
                    width=280,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, 
                                       color=ft.Colors.with_opacity(0.1, "#000000"))
                )
            )
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("rooms"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Rooms", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ft.Text("Browse devices by room", size=16, color=colors['text_secondary']),
                        ft.Container(height=10),
                        ft.Row(room_cards, spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    def show_room(room_name):
        current_page_state['page'] = f'room_{room_name}'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        room_devices = [(device_id, device) for device_id, device in devices.items() 
                       if device['room'] == room_name]
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("rooms"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: show_rooms(),
                                icon_color=colors['accent']
                            ),
                            ft.Text(f"📍 {room_name}", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ], spacing=10),
                        ft.Text(f"{len(room_devices)} devices in this room", 
                               size=16, color=colors['text_secondary']),
                        ft.Container(height=10),
                        ft.Row([
                            create_device_card(device_id, device, show_room=False)
                            for device_id, device in room_devices
                        ], spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()

    def show_statistics():
        current_page_state['page'] = 'statistics'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        # Filter controls
        filter_device = ft.Ref[ft.Dropdown]()
        filter_room = ft.Ref[ft.Dropdown]()
        filter_user = ft.Ref[ft.Dropdown]()
        
        def get_filtered_logs():
            filtered = action_log.copy()
            
            if filter_device.current and filter_device.current.value and filter_device.current.value != "All":
                filtered = [log for log in filtered if log['device'] == filter_device.current.value]
            
            if filter_room.current and filter_room.current.value and filter_room.current.value != "All":
                filtered = [log for log in filtered if log['room'] == filter_room.current.value]
            
            if filter_user.current and filter_user.current.value and filter_user.current.value != "All":
                filtered = [log for log in filtered if log['user'] == filter_user.current.value]
            
            return filtered
        
        def apply_filters(e):
            show_statistics()
        
        def export_logs(e):
            filtered = get_filtered_logs()
            filename = f"action_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump([{
                    'time': log['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'device': log['device'],
                    'action': log['action'],
                    'user': log['user'],
                    'room': log['room']
                } for log in filtered], f, indent=2)
            add_notification(f"Logs exported to {filename}", "success")
            page.update()
        
        # Get unique values for filters
        device_options = ["All"] + list(devices.keys())
        room_options = ["All"] + list(set(d['room'] for d in devices.values()))
        user_options = ["All"] + list(set(log['user'] for log in action_log))
        
        # Calculate energy consumption by hour
        hours = [f"{i:02d}:00" for i in range(24)]
        
        # Create simple bar chart
        max_energy = max(energy_data) if energy_data else 1
        chart_bars = []
        for i, value in enumerate(energy_data):
            height = (value / max_energy) * 200
            chart_bars.append(
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            bgcolor=colors['accent'],
                            width=20,
                            height=height,
                            border_radius=4,
                        ),
                        ft.Text(hours[i], size=8, color=colors['text_secondary'], rotate=ft.Rotate(angle=-0.5))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    tooltip=f"{hours[i]}: {value}W"
                )
            )
        
        # Calculate total energy (kWh)
        total_energy_kwh = sum(energy_data) / 1000
        avg_power = sum(energy_data) / len(energy_data)
        peak_power = max(energy_data)
        
        filtered_logs = get_filtered_logs()
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("statistics"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Statistics & Analytics", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        
                        # Energy stats
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Total Energy (24h)", size=12, color=colors['text_secondary']),
                                    ft.Text(f"{total_energy_kwh:.2f} kWh", size=24, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Average Power", size=12, color=colors['text_secondary']),
                                    ft.Text(f"{avg_power:.0f}W", size=24, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Peak Power", size=12, color=colors['text_secondary']),
                                    ft.Text(f"{peak_power}W", size=24, weight=ft.FontWeight.BOLD, color=colors['accent']),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=15,
                                bgcolor=colors['card'],
                                border_radius=12,
                                expand=True,
                            ),
                        ], spacing=15),
                        
                        ft.Container(height=10),
                        
                        # Energy chart
                        ft.Container(
                            content=ft.Column([
                                ft.Text("24-Hour Power Consumption", size=18, weight=ft.FontWeight.BOLD, color=colors['text']),
                                ft.Container(
                                    content=ft.Row(
                                        chart_bars,
                                        spacing=8,
                                        scroll=ft.ScrollMode.AUTO,
                                        alignment=ft.MainAxisAlignment.START
                                    ),
                                    padding=20,
                                ),
                            ], spacing=10),
                            bgcolor=colors['card'],
                            border_radius=12,
                            padding=15,
                        ),
                        
                        ft.Container(height=20),
                        
                        # Action log section
                        ft.Row([
                            ft.Text("Action Log", size=22, weight=ft.FontWeight.BOLD, color=colors['text']),
                            ft.ElevatedButton(
                                "Export",
                                icon=ft.Icons.DOWNLOAD,
                                on_click=export_logs,
                                bgcolor=colors['accent'],
                                color="#ffffff"
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        # Filters
                        ft.Row([
                            ft.Dropdown(
                                ref=filter_device,
                                label="Device",
                                options=[ft.dropdown.Option(opt) for opt in device_options],
                                value="All",
                                width=200,
                                on_change=apply_filters,
                            ),
                            ft.Dropdown(
                                ref=filter_room,
                                label="Room",
                                options=[ft.dropdown.Option(opt) for opt in room_options],
                                value="All",
                                width=200,
                                on_change=apply_filters,
                            ),
                            ft.Dropdown(
                                ref=filter_user,
                                label="User",
                                options=[ft.dropdown.Option(opt) for opt in user_options],
                                value="All",
                                width=200,
                                on_change=apply_filters,
                            ),
                        ], spacing=15, wrap=True),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.W_600, color=colors['text'])),
                                        ft.DataColumn(ft.Text("Device", weight=ft.FontWeight.W_600, color=colors['text'])),
                                        ft.DataColumn(ft.Text("Room", weight=ft.FontWeight.W_600, color=colors['text'])),
                                        ft.DataColumn(ft.Text("Action", weight=ft.FontWeight.W_600, color=colors['text'])),
                                        ft.DataColumn(ft.Text("User", weight=ft.FontWeight.W_600, color=colors['text'])),
                                    ],
                                    rows=[
                                        ft.DataRow(cells=[
                                            ft.DataCell(ft.Text(log['time'].strftime('%H:%M:%S'), color=colors['text'])),
                                            ft.DataCell(ft.Text(log['device'], color=colors['text'])),
                                            ft.DataCell(ft.Text(log['room'], color=colors['text'])),
                                            ft.DataCell(ft.Text(log['action'], color=colors['text'])),
                                            ft.DataCell(ft.Text(log['user'], color=colors['text'])),
                                        ]) for log in filtered_logs[:50]
                                    ],
                                    border=ft.border.all(1, colors['border']),
                                    border_radius=8,
                                    heading_row_color=colors['card'],
                                )
                            ], scroll=ft.ScrollMode.AUTO, height=400),
                            bgcolor=colors['card'],
                            border_radius=12,
                            padding=10,
                        )
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()

    def show_details(device_id):
        current_page_state['page'] = f'details_{device_id}'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        if device_id not in devices:
            return
        
        device = devices[device_id]
        device_actions = [log for log in action_log if log['device'] == device_id]
        
        if device['type'] in ['light', 'door', 'camera']:
            if device['type'] == 'light':
                state_text = "ON" if device['state'] else "OFF"
            elif device['type'] == 'door':
                state_text = "LOCKED" if device['state'] else "UNLOCKED"
            else:
                state_text = "ACTIVE" if device['state'] else "DISABLED"
            state_display = ft.Text(f"State: {state_text}", color=colors['text'], size=16)
        else:
            value = device['value']
            if device['type'] == 'thermostat':
                value_text = f"{value:.1f}°C"
            else:
                value_text = f"Speed {int(value)}"
            state_display = ft.Text(f"Value: {value_text}", color=colors['text'], size=16)
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("details"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: show_overview(),
                                icon_color=colors['accent']
                            ),
                            ft.Text(f"{get_device_icon(device['type'])} {device['name']}", 
                                   size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ], spacing=10),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Device Information", size=18, weight=ft.FontWeight.BOLD, color=colors['text']),
                                ft.Divider(color=colors['border']),
                                ft.Text(f"ID: {device_id}", color=colors['text']),
                                ft.Text(f"Type: {device['type'].title()}", color=colors['text']),
                                ft.Text(f"Room: {device['room']}", color=colors['text']),
                                ft.Text(f"Power Consumption: {device['power']}W", color=colors['text']),
                                state_display,
                            ], spacing=10),
                            padding=20,
                            bgcolor=colors['card'],
                            border_radius=12,
                        ),
                        
                        ft.Container(height=10),
                        
                        ft.Text("Recent Actions", size=20, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"{log['time'].strftime('%Y-%m-%d %H:%M:%S')} - {log['action']} by {log['user']}", 
                                       color=colors['text'])
                                for log in device_actions[:10]
                            ] if device_actions else [
                                ft.Text("No recent actions", color=colors['text_secondary'])
                            ], spacing=8),
                            padding=20,
                            bgcolor=colors['card'],
                            border_radius=12,
                        ),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    def show_automation():
        current_page_state['page'] = 'automation'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        def toggle_rule(e):
            rule_id = e.control.data
            for rule in automation_rules:
                if rule['id'] == rule_id:
                    rule['enabled'] = not rule['enabled']
                    add_notification(f"Rule '{rule['name']}' {'enabled' if rule['enabled'] else 'disabled'}", "info")
                    break
            show_automation()
        
        rule_cards = []
        for rule in automation_rules:
            rule_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(rule['name'], size=18, weight=ft.FontWeight.BOLD, color=colors['text']),
                            ft.Switch(
                                value=rule['enabled'],
                                data=rule['id'],
                                on_change=toggle_rule,
                                active_color=colors['accent']
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"Time: {rule['time']}", color=colors['text_secondary']),
                        ft.Text(f"Device: {rule['device']}", color=colors['text_secondary']),
                        ft.Text(f"Action: {rule['action']}", color=colors['text_secondary']),
                    ], spacing=8),
                    padding=20,
                    bgcolor=colors['card'],
                    border_radius=12,
                    width=350,
                )
            )
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("automation"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Automation Rules", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                        ft.Text("Schedule and automate your devices", size=16, color=colors['text_secondary']),
                        ft.Container(height=10),
                        ft.Row(rule_cards, spacing=15, wrap=True, scroll=ft.ScrollMode.AUTO),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    def show_notifications():
        current_page_state['page'] = 'notifications'
        colors = get_theme_colors()
        page.bgcolor = colors['bg']
        
        def clear_notifications(e):
            notifications.clear()
            add_notification("All notifications cleared", "info")
            show_notifications()
        
        notification_items = []
        for notif in notifications:
            icon = "ℹ️" if notif['type'] == "info" else "✅" if notif['type'] == "success" else "⚠️"
            notification_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(icon, size=20),
                        ft.Column([
                            ft.Text(notif['message'], color=colors['text'], size=14),
                            ft.Text(notif['time'].strftime('%H:%M:%S'), 
                                   color=colors['text_secondary'], size=12),
                        ], spacing=2, expand=True),
                    ], spacing=10),
                    padding=15,
                    bgcolor=colors['card'],
                    border_radius=8,
                )
            )
        
        page.clean()
        page.add(
            ft.Column([
                create_nav_bar("notifications"),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Notifications", size=28, weight=ft.FontWeight.BOLD, color=colors['text']),
                            ft.ElevatedButton(
                                "Clear All",
                                on_click=clear_notifications,
                                bgcolor=colors['accent'],
                                color="#ffffff"
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=10),
                        ft.Column(
                            notification_items if notifications else [
                                ft.Text("No notifications", color=colors['text_secondary'], size=16)
                            ],
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO
                        ),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20,
                    expand=True,
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    # Initialize with overview page
    show_overview()

ft.app(target=main)
