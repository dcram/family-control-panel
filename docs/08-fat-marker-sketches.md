# Fat marker sketches — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

## Vue kiosque

Bandeau supérieur fixe : saint du jour + nom du jour à gauche,
citation du moment au centre, météo (icône + température + vent) à droite.

Navigation : chevrons gauche/droite sans label, bouton Aujourd'hui
centré visible uniquement si on n'est pas sur le jour courant.

Grille 7 colonnes. Colonne aujourd'hui mise en avant par une bordure
accentuée. Dans chaque colonne, tâches groupées par moment (matin /
midi / soir). Chaque carte tâche : icône + libellé en élément dominant,
point couleur + prénom enfant en secondaire, icône état à droite
(✓ verte / ✓ grise / ✗ rouge / ? grise).

Lien admin discret en bas à droite via icône engrenage.

## Vue planning admin

Sidebar persistante à gauche : Planning (actif) / Enfants / Catalogue /
Configuration / séparateur / Déconnexion.

Contenu principal : navigation semaine (chevrons + label semaine),
bandeau charge hebdomadaire par enfant (point couleur + prénom + total
minutes), bouton "Copier une semaine" aligné à droite du bandeau.

Même grille 7 colonnes que le kiosque. Différences admin :
bouton [+ Ajouter] en pointillés dans chaque créneau vide,
bouton [✕] sur chaque carte tâche pour suppression,
boutons [Valider] vert et [Invalider] rouge visibles uniquement
sur les tâches en état "Déclarée faite" (carte avec bordure accentuée).

Note itération 2 : envisager un carrousel centré sur aujourd'hui
avec J-1/J+1 visibles en contexte réduit, particulièrement
adapté au mobile portrait.