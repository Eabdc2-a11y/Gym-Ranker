import json
import os
import customtkinter as ctk
from tkinter import messagebox

# Configuration du thème CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- CONSTANTES & RANKS ---
RANKS = [
    {"name": "Bronze", "color": "#CD7F32", "ratio": 0.0},
    {"name": "Silver", "color": "#C0C0C0", "ratio": 0.8},
    {"name": "Gold", "color": "#FFD700", "ratio": 1.1},
    {"name": "Platinum", "color": "#00ECEC", "ratio": 1.4},
    {"name": "Diamond", "color": "#B9F2FF", "ratio": 1.7},
    {"name": "Master", "color": "#A020F0", "ratio": 2.0},
    {"name": "GODLIKE ⚡", "color": "#FF003C", "ratio": 2.3}  # Rang Mythique Ultra Dur
]

MUSCLES = ["Chest", "Back", "Legs", "Shoulders", "Biceps", "Triceps"]

DB_FILE = "gym_rpg_data.json"

# --- LOGIQUE DE CALCUL DE BASE ---
def get_default_data():
    return {
        "user_info": {"weight": 75.0, "height": 175.0},
        "muscles": {m: {"xp": 0, "best_1rm": 0.0} for m in MUSCLES},
        "history": []
    }

def load_data():
    if not os.path.exists(DB_FILE):
        return get_default_data()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_1rm(weight, reps):
    """Formule d'Epley pour estimer le 1RM"""
    if reps == 1:
        return weight
    return weight * (1 + reps / 30.0)

def get_rank_info(ratio):
    """Détermine le rang selon le ratio force/poids corporel"""
    current_rank = RANKS[0]
    for r in RANKS:
        if ratio >= r["ratio"]:
            current_rank = r
        else:
            break
    return current_rank

# --- APPLICATION GRAPHIQUE ---
class GymRPGApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gym RPG - Evolution & Ranks")
        self.geometry("850x650")
        self.resizable(False, False)

        self.data = load_data()

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panneau Latéral (Profil & Rangs Musculaires)
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=12)
        self.sidebar_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.build_sidebar()

        # Panneau Principal (Enregistrement Workout & Historique)
        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.build_main_panel()

    def build_sidebar(self):
        # Profil Utilisateur
        title = ctk.CTkLabel(self.sidebar_frame, text="👤 PROFIL ATHLÈTE", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(15, 10))

        # Entrées Poids/Taille
        info_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(info_frame, text="Poids (kg):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.weight_entry = ctk.CTkEntry(info_frame, width=70)
        self.weight_entry.insert(0, str(self.data["user_info"]["weight"]))
        self.weight_entry.grid(row=0, column=1, padx=5, pady=2)

        ctk.CTkLabel(info_frame, text="Taille (cm):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.height_entry = ctk.CTkEntry(info_frame, width=70)
        self.height_entry.insert(0, str(self.data["user_info"]["height"]))
        self.height_entry.grid(row=1, column=1, padx=5, pady=2)

        save_btn = ctk.CTkButton(self.sidebar_frame, text="Mettre à jour le profil", command=self.update_profile, height=25)
        save_btn.pack(pady=8)

        # Niveaux Musculaires
        ctk.CTkLabel(self.sidebar_frame, text="💪 NIVEAUX PAR MUSCLE", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))

        self.muscle_labels = {}
        self.refresh_muscle_display()

    def refresh_muscle_display(self):
        # Effacer l'existant s'il y a un conteneur
        if hasattr(self, 'muscle_container'):
            self.muscle_container.destroy()

        self.muscle_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.muscle_container.pack(fill="both", expand=True, padx=10, pady=5)

        user_weight = float(self.data["user_info"]["weight"])

        for muscle in MUSCLES:
            m_data = self.data["muscles"][muscle]
            best_1rm = m_data["best_1rm"]
            ratio = (best_1rm / user_weight) if user_weight > 0 else 0
            rank = get_rank_info(ratio)

            card = ctk.CTkFrame(self.muscle_container, corner_radius=8)
            card.pack(fill="x", pady=4)

            # Muscle + XP
            lbl_title = ctk.CTkLabel(card, text=f"{muscle}", font=ctk.CTkFont(weight="bold"))
            lbl_title.pack(anchor="w", padx=10, pady=(2, 0))

            # Tag de Rang avec Couleur
            rank_tag = ctk.CTkLabel(
                card, 
                text=f"{rank['name']} (1RM: {best_1rm:.1f}kg | {m_data['xp']} XP)", 
                text_color=rank["color"],
                font=ctk.CTkFont(size=12, weight="bold")
            )
            rank_tag.pack(anchor="w", padx=10, pady=(0, 4))

    def build_main_panel(self):
        ctk.CTkLabel(self.main_frame, text="🏋️ ENREGISTRER UN WORKOUT", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)

        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Sélection Muscle
        ctk.CTkLabel(form_frame, text="Groupe Musculaire:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.muscle_option = ctk.CTkOptionMenu(form_frame, values=MUSCLES)
        self.muscle_option.grid(row=0, column=1, padx=10, pady=8)

        # Exercice Name
        ctk.CTkLabel(form_frame, text="Nom de l'Exercice:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.exercise_entry = ctk.CTkEntry(form_frame, placeholder_text="ex: Développé Couché", width=200)
        self.exercise_entry.grid(row=1, column=1, padx=10, pady=8)

        # Sets / Reps / Weight
        ctk.CTkLabel(form_frame, text="Nombre de Sets:").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.sets_entry = ctk.CTkEntry(form_frame, width=100)
        self.sets_entry.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form_frame, text="Répétitions par Set:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.reps_entry = ctk.CTkEntry(form_frame, width=100)
        self.reps_entry.grid(row=3, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form_frame, text="Charge Utilisée (kg):").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.weight_used_entry = ctk.CTkEntry(form_frame, width=100)
        self.weight_used_entry.grid(row=4, column=1, padx=10, pady=8, sticky="w")

        # Bouton Validation
        log_btn = ctk.CTkButton(self.main_frame, text="Valider la Séance 🔥", command=self.log_workout, fg_color="#1f538d", height=40)
        log_btn.pack(pady=15)

        # Zone d'Alerte / Feedback
        self.feedback_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.feedback_label.pack(pady=5)

    def update_profile(self):
        try:
            w = float(self.weight_entry.get())
            h = float(self.height_entry.get())
            self.data["user_info"]["weight"] = w
            self.data["user_info"]["height"] = h
            save_data(self.data)
            self.refresh_muscle_display()
            messagebox.showinfo("Succès", "Profil mis à jour avec succès!")
        except ValueError:
            messagebox.showerror("Erreur", "Poids et taille doivent être des nombres.")

    def log_workout(self):
        try:
            muscle = self.muscle_option.get()
            exercise = self.exercise_entry.get().strip()
            sets = int(self.sets_entry.get())
            reps = int(self.reps_entry.get())
            weight = float(self.weight_used_entry.get())

            if not exercise:
                messagebox.showwarning("Attention", "Veuillez entrer un nom d'exercice.")
                return

            # Calcul du 1RM actuel de la séance
            current_1rm = calculate_1rm(weight, reps)
            
            # Recherche du meilleur 1RM précédent pour cet exercice dans l'historique
            previous_best_1rm = 0.0
            for log in self.data["history"]:
                if log["muscle"] == muscle and log["exercise"].lower() == exercise.lower():
                    if log["est_1rm"] > previous_best_1rm:
                        previous_best_1rm = log["est_1rm"]

            # --- RÈGLE SURCHARGE PROGRESSIVE ---
            xp_gained = 0
            if previous_best_1rm == 0:
                # Premier enregistrement de cet exercice
                xp_gained = int(current_1rm * sets)
                msg = f"🎉 Nouvel exercice débloqué ! +{xp_gained} XP sur {muscle}."
            elif current_1rm > previous_best_1rm:
                # Progression confirmée !
                diff = current_1rm - previous_best_1rm
                xp_gained = int(diff * 10 + (sets * reps))
                msg = f"🔥 SURCHARGE PROGRESSIVE ! Nouveau PR ! +{xp_gained} XP sur {muscle}."
            else:
                # Pas de progression en charge ou en reps
                xp_gained = 0
                msg = f"⚠️ Pas de progression détectée (1RM: {current_1rm:.1f}kg <= Précédent: {previous_best_1rm:.1f}kg). +0 XP."

            # Mise à jour des données
            self.data["muscles"][muscle]["xp"] += xp_gained
            
            # Mettre à jour le 1RM max du muscle si battu
            if current_1rm > self.data["muscles"][muscle]["best_1rm"]:
                self.data["muscles"][muscle]["best_1rm"] = current_1rm

            # Enregistrer dans l'historique
            self.data["history"].append({
                "muscle": muscle,
                "exercise": exercise,
                "sets": sets,
                "reps": reps,
                "weight": weight,
                "est_1rm": current_1rm,
                "xp_gained": xp_gained
            })

            save_data(self.data)

            # Affichage du feedback
            color = "#00FF66" if xp_gained > 0 else "#FFCC00"
            self.feedback_label.configure(text=msg, text_color=color)

            # Rafraîchir l'IHM
            self.refresh_muscle_display()

        except ValueError:
            messagebox.showerror("Erreur", "Saisissez des nombres valides pour Sets, Reps et Poids.")

if __name__ == "__main__":
    app = GymRPGApp()
    app.mainloop()
