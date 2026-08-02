import json
import os
import flet as ft

# --- CONSTANTES & RANKS ---
RANKS = [
    {"name": "Bronze", "color": "#CD7F32", "ratio": 0.0},
    {"name": "Silver", "color": "#C0C0C0", "ratio": 0.8},
    {"name": "Gold", "color": "#FFD700", "ratio": 1.1},
    {"name": "Platinum", "color": "#00ECEC", "ratio": 1.4},
    {"name": "Diamond", "color": "#B9F2FF", "ratio": 1.7},
    {"name": "Master", "color": "#A020F0", "ratio": 2.0},
    {"name": "GODLIKE ⚡", "color": "#FF003C", "ratio": 2.3}  # Rang 7 : Ultra Dur
]

MUSCLES = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps"]
DB_FILE = "gym_rpg_data.json"

def get_default_data():
    return {
        "user_info": {"weight": 75.0, "height": 175.0},
        "muscles": {m: {"xp": 0, "best_1rm": 0.0} for m in MUSCLES},
        "history": []
    }

def load_data():
    if not os.path.exists(DB_FILE):
        return get_default_data()
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return get_default_data()

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_1rm(weight, reps):
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)

def get_rank_info(ratio):
    current_rank = RANKS[0]
    for r in RANKS:
        if ratio >= r["ratio"]:
            current_rank = r
        else:
            break
    return current_rank

def main(page: ft.Page):
    page.title = "Gym RPG Ranker"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    data = load_data()

    # Dynamic Components
    muscle_list_view = ft.Column(spacing=10)
    feedback_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD)

    # Form Fields
    weight_input = ft.TextField(label="Poids (kg)", value=str(data["user_info"]["weight"]), width=110)
    height_input = ft.TextField(label="Taille (cm)", value=str(data["user_info"]["height"]), width=110)

    muscle_dropdown = ft.Dropdown(
        label="Muscle ciblé",
        options=[ft.dropdown.Option(m) for m in MUSCLES],
        value=MUSCLES[0]
    )
    exercise_input = ft.TextField(label="Nom de l'exercice", hint_text="ex: Développé Couché")
    sets_input = ft.TextField(label="Sets", keyboard_type=ft.KeyboardType.NUMBER, width=90)
    reps_input = ft.TextField(label="Reps", keyboard_type=ft.KeyboardType.NUMBER, width=90)
    load_input = ft.TextField(label="Poids (kg)", keyboard_type=ft.KeyboardType.NUMBER, width=100)

    def refresh_muscles():
        muscle_list_view.controls.clear()
        u_weight = float(data["user_info"]["weight"]) if data["user_info"]["weight"] > 0 else 75.0

        for m in MUSCLES:
            m_data = data["muscles"][m]
            best_1rm = m_data["best_1rm"]
            ratio = best_1rm / u_weight
            rank = get_rank_info(ratio)

            card = ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Column([
                        ft.Text(m, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"Rang : {rank['name']} (1RM: {best_1rm:.1f} kg | XP: {m_data['xp']})",
                            color=rank["color"],
                            weight=ft.FontWeight.BOLD
                        )
                    ])
                )
            )
            muscle_list_view.controls.append(card)
        page.update()

    def update_profile(e):
        try:
            data["user_info"]["weight"] = float(weight_input.value)
            data["user_info"]["height"] = float(height_input.value)
            save_data(data)
            refresh_muscles()
            feedback_text.value = "✅ Profil mis à jour !"
            feedback_text.color = ft.Colors.GREEN
        except ValueError:
            feedback_text.value = "⚠️ Entrez des valeurs valides pour le poids/taille."
            feedback_text.color = ft.Colors.RED
        page.update()

    def log_workout(e):
        try:
            m = muscle_dropdown.value
            ex = exercise_input.value.strip() if exercise_input.value else ""
            sets = int(sets_input.value)
            reps = int(reps_input.value)
            weight = float(load_input.value)

            if not ex:
                feedback_text.value = "⚠️ Merci de spécifier le nom de l'exercice."
                feedback_text.color = ft.Colors.RED
                page.update()
                return

            current_1rm = calculate_1rm(weight, reps)

            # Recherche du 1RM précédent pour vérifier la surcharge
            previous_best_1rm = 0.0
            for log in data["history"]:
                if log["muscle"] == m and log["exercise"].lower() == ex.lower():
                    if log["est_1rm"] > previous_best_1rm:
                        previous_best_1rm = log["est_1rm"]

            if previous_best_1rm == 0:
                xp = int(current_1rm * sets)
                msg = f"🎉 Nouvel exercice complété ! +{xp} XP sur {m}."
                color = ft.Colors.GREEN
            elif current_1rm > previous_best_1rm:
                diff = current_1rm - previous_best_1rm
                xp = int(diff * 10 + (sets * reps))
                msg = f"🔥 SURCHARGE PROGRESSIVE ! +{xp} XP sur {m}."
                color = ft.Colors.GREEN
            else:
                xp = 0
                msg = f"⚠️ Pas de progression (1RM: {current_1rm:.1f}kg <= Record: {previous_best_1rm:.1f}kg). +0 XP."
                color = ft.Colors.AMBER

            data["muscles"][m]["xp"] += xp
            if current_1rm > data["muscles"][m]["best_1rm"]:
                data["muscles"][m]["best_1rm"] = current_1rm

            data["history"].append({
                "muscle": m,
                "exercise": ex,
                "sets": sets,
                "reps": reps,
                "weight": weight,
                "est_1rm": current_1rm,
                "xp_gained": xp
            })

            save_data(data)
            feedback_text.value = msg
            feedback_text.color = color
            refresh_muscles()

        except ValueError:
            feedback_text.value = "⚠️ Merci de remplir correctement les Sets, Reps et Poids."
            feedback_text.color = ft.Colors.RED
            page.update()

    # Layout Mobile / Web
    page.add(
        ft.Text("🏆 GYM RPG RANKER", size=22, weight=ft.FontWeight.BOLD),
        ft.Row([weight_input, height_input]),
        ft.ElevatedButton("Mettre à jour le profil", on_click=update_profile),
        ft.Divider(),
        ft.Text("🏋️ Enregistrer un entraînement", size=18, weight=ft.FontWeight.BOLD),
        muscle_dropdown,
        exercise_input,
        ft.Row([sets_input, reps_input, load_input]),
        ft.ElevatedButton("Valider le Workout 🔥", on_click=log_workout),
        feedback_text,
        ft.Divider(),
        ft.Text("💪 Niveau des Muscles", size=18, weight=ft.FontWeight.BOLD),
        muscle_list_view
    )

    refresh_muscles()

# Lancement du serveur Web Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
