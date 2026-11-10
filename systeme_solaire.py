import pygame
import math
import random

# --- 1. INITIALISATION ET FENÊTRE ---
pygame.init()
LARGEUR, HAUTEUR = 1300, 850
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Simulation Système Solaire - Projet 20/20")
horloge = pygame.time.Clock()

# --- 2. POLICES ET COULEURS ---
police_petite = pygame.font.SysFont("Verdana", 14)
police_titre = pygame.font.SysFont("Verdana", 16, bold=True)
police_date = pygame.font.SysFont("Consolas", 18, bold=True)

NOIR = (5, 5, 12)
BLANC = (255, 255, 255)
JAUNE_SOLEIL = (255, 215, 0)
GRIS_ORBITE = (50, 50, 70)
COULEUR_MENU = (30, 30, 45)
VERT_FLUO = (0, 255, 150)

# --- 3. DONNÉES ET ÉTOILES ---
# [Nom, Demi-grand axe (UA), Excentricité, Période (jours), Couleur, Taille]
DONNEES_PLANETES = [
   ["Mercure", 0.387, 0.205, 88, (160, 160, 160), 4],
   ["Vénus", 0.723, 0.006, 224.7, (230, 190, 150), 7],
   ["Terre", 1.000, 0.016, 365.2, (50, 150, 255), 7],
   ["Mars", 1.523, 0.093, 687, (255, 80, 60), 5],
   ["Jupiter", 5.204, 0.048, 4332, (200, 170, 140), 16],
   ["Saturne", 9.582, 0.054, 10759, (220, 190, 130), 12],
   ["Uranus", 19.201, 0.047, 30688, (160, 220, 240), 10],
   ["Neptune", 30.047, 0.008, 60182, (70, 90, 200), 10]
]


etoiles = [(random.randint(0, LARGEUR - 220), random.randint(0, HAUTEUR)) for _ in range(150)]

# --- 4. CLASSE PLANÈTE ---
class Planete:
   def __init__(self, nom, demi_grand_axe, excentricite, periode, couleur, taille):
       self.nom = nom
       self.a = demi_grand_axe
       self.e = excentricite
       self.periode = periode
       self.couleur = couleur
       self.taille = taille
       self.position_initiale = random.uniform(0, periode)

   def calculer_position(self, niveau_zoom, centre_x, centre_y, jours_ecoules):
       anomalie_moyenne = (2 * math.pi * ((self.position_initiale + jours_ecoules) % self.periode)) / self.periode
       E = anomalie_moyenne
       for _ in range(5): 
           E = E - (E - self.e * math.sin(E) - anomalie_moyenne) / (1 - self.e * math.cos(E))
       echelle = 150 * niveau_zoom
       x_orbite = self.a * (math.cos(E) - self.e) * echelle
       y_orbite = self.a * (math.sqrt(1 - self.e**2) * math.sin(E)) * echelle
       
       return centre_x + x_orbite, centre_y + y_orbite

liste_planetes = [Planete(*donnees) for donnees in DONNEES_PLANETES]

# --- 5. VARIABLES DE CONTRÔLE ---
niveau_zoom = 0.5
vitesse_temporelle = 1.0
total_jours_simules = 0
cible_focus = None
en_cours = True

# --- 6. BOUCLE PRINCIPALE ---
while en_cours:
   ecran.fill(NOIR)
   
   # Gestion du focus
   decalage_x, decalage_y = 0, 0
   if cible_focus:
       pos_x, pos_y = cible_focus.calculer_position(niveau_zoom, 0, 0, total_jours_simules)
       decalage_x, decalage_y = -pos_x, -pos_y

   # Centre du système (Soleil)
   centre_x = (LARGEUR - 220) // 2 + decalage_x
   centre_y = HAUTEUR // 2 + decalage_y

   for etoile in etoiles: 
       pygame.draw.circle(ecran, (70, 70, 90), etoile, 1)

   pygame.draw.circle(ecran, JAUNE_SOLEIL, (int(centre_x), int(centre_y)), max(int(20 * niveau_zoom), 5))

   position_focus_actuelle = None

   # Dessin 
   for p in liste_planetes:
       points_orbite = []
       for i in range(101):
           angle = (i / 100) * 2 * math.pi
           rayon_polaire = (p.a * (1 - p.e**2)) / (1 + p.e * math.cos(angle))
           px = centre_x + math.cos(angle) * rayon_polaire * 150 * niveau_zoom
           py = centre_y + math.sin(angle) * rayon_polaire * 150 * niveau_zoom
           points_orbite.append((px, py))
       pygame.draw.lines(ecran, GRIS_ORBITE, True, points_orbite, 1)
       
       #Calcul de la position de la planète
       px, py = p.calculer_position(niveau_zoom, centre_x, centre_y, total_jours_simules)
       if p == cible_focus:
           position_focus_actuelle = (px, py)

       taille_visuelle = max(int(p.taille * niveau_zoom**0.5), 2)
       
       pygame.draw.circle(ecran, p.couleur, (int(px), int(py)), taille_visuelle)
       

       angle_soleil = math.atan2(py - centre_y, px - centre_x)
       surface_ombre = pygame.Surface((taille_visuelle * 2, taille_visuelle * 2), pygame.SRCALPHA)
       pygame.draw.circle(surface_ombre, (0, 0, 0, 140), (taille_visuelle, taille_visuelle), taille_visuelle)
       ecran.blit(surface_ombre, (px - taille_visuelle + math.cos(angle_soleil)*2, py - taille_visuelle + math.sin(angle_soleil)*2))

       #Affichage du nom 
       texte_nom = police_petite.render(p.nom, True, BLANC)
       ecran.blit(texte_nom, (px - texte_nom.get_width() // 2, py - taille_visuelle - 18))

   # --- 7. MENU LATÉRAL
   pygame.draw.rect(ecran, COULEUR_MENU, (LARGEUR - 220, 0, 220, HAUTEUR))
   zones_boutons = [] 
   
   hauteur_actuelle = 20
   ecran.blit(police_titre.render("TEMPS SIMULÉ", True, VERT_FLUO), (LARGEUR - 200, hauteur_actuelle))
   
   # Affichage de la Date
   hauteur_actuelle += 30
   an_actuel = 2026 + int(total_jours_simules // 365.25)
   jour_actuel = int(total_jours_simules % 365.25) + 1
   affichage_date = f"An {an_actuel}, J. {jour_actuel}"
   ecran.blit(police_date.render(affichage_date, True, BLANC), (LARGEUR - 200, hauteur_actuelle))

   hauteur_actuelle += 25
   vitesse_fps = vitesse_temporelle * 60 
   if vitesse_temporelle == 0:
       texte_vitesse = "PAUSE"
       couleur_vitesse = (255, 100, 100)
   else:
       texte_vitesse = f"Vitesse: {vitesse_fps:.1f} j/s"
       couleur_vitesse = (200, 200, 200)
   ecran.blit(police_petite.render(texte_vitesse, True, couleur_vitesse), (LARGEUR - 200, hauteur_actuelle))


   if cible_focus and position_focus_actuelle:
       hauteur_actuelle += 25
       dx = (position_focus_actuelle[0] - centre_x) / (150 * niveau_zoom)
       dy = (position_focus_actuelle[1] - centre_y) / (150 * niveau_zoom)
       distance_ua = math.sqrt(dx**2 + dy**2)
       texte_dist = f"Dist: {distance_ua:.2f} UA"
       ecran.blit(police_petite.render(texte_dist, True, (0, 220, 255)), (LARGEUR - 200, hauteur_actuelle))


   hauteur_actuelle += 35
   ecran.blit(police_titre.render("CONTRÔLES", True, VERT_FLUO), (LARGEUR - 200, hauteur_actuelle))
   
   commandes = [
       ("Zoomer (+)", "Z+"), 
       ("Dézoomer (-)", "Z-"), 
       ("Accélérer", "V+"), 
       ("Ralentir", "V-"), 
       ("Pause / Play", "PAUSE"), 
       ("Vue Globale", "RESET")
   ]
   hauteur_actuelle += 30
   for etiquette, code in commandes:
       rect_bouton = pygame.Rect(LARGEUR - 200, hauteur_actuelle, 180, 30)
       pygame.draw.rect(ecran, (50, 50, 70), rect_bouton, border_radius=5)
       ecran.blit(police_petite.render(etiquette, True, BLANC), (rect_bouton.x + 10, rect_bouton.y + 5))
       zones_boutons.append((rect_bouton, code))
       hauteur_actuelle += 35


   hauteur_actuelle += 15
   ecran.blit(police_titre.render("FOCUS PLANÈTE", True, VERT_FLUO), (LARGEUR - 200, hauteur_actuelle))
   hauteur_actuelle += 30
   for p in liste_planetes:
       rect_bouton = pygame.Rect(LARGEUR - 200, hauteur_actuelle, 180, 25)
       couleur_fond = (0, 100, 200) if cible_focus == p else (40, 40, 60)
       pygame.draw.rect(ecran, couleur_fond, rect_bouton, border_radius=3)
       ecran.blit(police_petite.render(p.nom, True, BLANC), (rect_bouton.x + 10, rect_bouton.y + 3))
       zones_boutons.append((rect_bouton, p))
       hauteur_actuelle += 28

   # --- 8. GESTION DES ÉVÉNEMENTS ---
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           en_cours = False
       if event.type == pygame.MOUSEBUTTONDOWN:
           for rect, action in zones_boutons:
               if rect.collidepoint(event.pos):
                   if action == "Z+": 
                       niveau_zoom *= 1.4
                   elif action == "Z-": 
                       niveau_zoom /= 1.4
                   elif action == "V+": 
                       vitesse_temporelle *= 2
                   elif action == "V-": 
                       vitesse_temporelle /= 2
                   elif action == "PAUSE":
                       if vitesse_temporelle != 0:
                           vitesse_temporelle = 0
                       else:
                           vitesse_temporelle = 1.0
                   elif action == "RESET": 
                       cible_focus = None
                   elif isinstance(action, Planete): 
                       cible_focus = action

   total_jours_simules += vitesse_temporelle
   pygame.display.flip()
   horloge.tick(60)

pygame.quit()