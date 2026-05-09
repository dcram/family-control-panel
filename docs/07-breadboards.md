# Breadboards — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

---

## 1. Vue kiosque

[ BANDEAU SUPÉRIEUR ]
  Saint du jour | Météo (ville configurée) | Citation du moment (texte + auteur)

[ BOUTON AUJOURD'HUI ] — visible uniquement si on n'est pas sur aujourd'hui

[ VUE SEMAINE ]
  ← jour précédent                                          jour suivant →

  LUN       MAR      [AUJOURD'HUI]  JEU       VEN       SAM       DIM
  ──────    ──────    ══════════    ──────    ──────    ──────    ──────

  Chaque colonne :
  ┌─ MATIN ──────────────┐
  │ 🍽️ Débarrasser table │  ← emoji + libellé, éléments dominants
  │ 🟢 Constance     ✓  │  ← couleur + prénom + état
  ├──────────────────────┤
  │ [+ Ajouter une tâche]│  ← affordance d'ajout inline (admin uniquement)
  └──────────────────────┘
  ┌─ MIDI ───────────────┐
  │ [+ Ajouter une tâche]│
  └──────────────────────┘
  ┌─ SOIR ───────────────┐
  │ 🗑️ Sortir la poubelle│
  │ 🟡 Agathe        ⏳  │
  │ [ Valider ✓ ]        │
  │ [ Invalider ✗ ]      │
  ├──────────────────────┤
  │ [+ Ajouter une tâche]│
  └──────────────────────┘

### Affordances

- Tap sur une tâche         → ouvre le pavé PIN (enfant ou parent)
- Tap ← / →                → navigation jour précédent / suivant
                              (jour suivant depuis dimanche → lundi semaine suivante)
- Tap [Aujourd'hui]         → retour centré sur aujourd'hui
- Tap [accès admin]         → écran de login (lien discret, coin bas droit)

### Pavé PIN (overlay, après tap sur une tâche)

  [ Emoji + Libellé de la tâche sélectionnée ]
  [ Couleur + Prénom enfant assigné           ]

  [ 1 ] [ 2 ] [ 3 ]
  [ 4 ] [ 5 ] [ 6 ]
  [ 7 ] [ 8 ] [ 9 ]
  [ ✕ ] [ 0 ] [ ⌫ ]

  → PIN reconnu comme enfant  : tâche → Déclarée faite (✓ grise)
                                retour kiosque immédiat
  → PIN reconnu comme parent  : choix Valider ✓ verte / Invalider ✗ rouge + motif
                                retour kiosque immédiat
  → PIN invalide              : secousse, champ réinitialisé
  → Tap ✕ ou extérieur        : fermeture overlay, retour kiosque

### États visuels d'une tâche

  Assignée        — aucune icône, affichage neutre
  Déclarée faite  — ✓ grise (déclaration enfant, en attente validation parent)
  Réalisée        — ✓ verte (validée par parent ou 30h sans réaction)
  Non réalisée    — ✗ rouge (invalidée par parent + motif)
  Non renseignée  — ? grise (30h écoulées sans aucune action)

### Notes de conception

  - 7 colonnes en paysage sur tablette. Sur mobile portrait,
    centré sur aujourd'hui avec navigation gauche/droite.
  - Bandeau supérieur fixe. Vue semaine scrollable verticalement
    si beaucoup de tâches.
  - Emoji sur la tâche : champ optionnel défini à la création.
    Si absent, icône générique par défaut.
  - Lien accès admin : discret, coin bas droit.
    Ne doit pas attirer l'attention sur le kiosque.

---

## 2. Login parent

[ LIEN ← Retour au kiosque ]

[ Identifiant ]  champ texte
[ Mot de passe ] champ texte masqué

[ Se connecter ]  bouton principal

### Affordances

- Tap [Se connecter]         → validation identifiants
  → valides                  : redirection vers vue planning admin
  → invalides                : message d'erreur inline, champs non réinitialisés
- Tap [← Retour au kiosque]  : retour vue kiosque sans authentification

### Notes de conception

  - Pas de "mot de passe oublié" dans le MVP.
  - Pas de "rester connecté" — session expire à la fermeture du navigateur.
  - Écran minimaliste par design : on ne veut pas qu'il soit invitant
    depuis le kiosque.

---

## 3. Vue planning admin

[ SIDEBAR ]                    [ CONTENU PRINCIPAL ]
  Planning
  Enfants                      [ SEMAINE DU lun. JJ/MM au dim. JJ/MM ]
  Catalogue                      ← semaine précédente    semaine suivante →
  Configuration
  ───────────                  [ CHARGE HEBDOMADAIRE ]
  Déconnexion                    🟢 Constance  120 min   🔵 Valentin   95 min
                                 🟡 Agathe     110 min   🔴 Jeanne    130 min
                                 🟣 Théophile   45 min

                               [ Copier une semaine existante comme base ]

                               [ VUE SEMAINE ]

                               LUN    MAR    [AUJOURD'HUI]  JEU    VEN    SAM    DIM
                               ────   ────   ════════════   ────   ────   ────   ────

                               Chaque colonne :
                               ┌─ MATIN ──────────────┐
                               │ 🍽️ Débarrasser table  │
                               │ 🟢 Constance      ✓  │
                               ├──────────────────────┤
                               │ [+ Ajouter une tâche]│
                               └──────────────────────┘
                               ┌─ SOIR ───────────────┐
                               │ 🗑️ Sortir la poubelle │
                               │ 🟡 Agathe         ⏳  │
                               │ [ Valider ✓ ]         │
                               │ [ Invalider ✗ ]       │
                               ├──────────────────────┤
                               │ [+ Ajouter une tâche]│
                               └──────────────────────┘

### Affordances sur une tâche existante

- Tap sur une tâche           → ouvre panneau d'édition de l'assignation
- Tap [ Valider ✓ ]           → tâche → Réalisée ✓
                                visible uniquement si état "Déclarée faite"
- Tap [ Invalider ✗ ]         → demande motif → tâche → Non réalisée ✗
                                visible uniquement si état "Déclarée faite"
- Tap [ ✕ supprimer ]         → suppression assignation avec confirmation

### Panneau d'édition d'assignation (overlay)

  [ Emoji + Libellé tâche ]   sélecteur — liste du catalogue
  [ Enfant ]                  sélecteur — liste des enfants
  [ Jour ]                    sélecteur — lun. / mar. / ... / dim.
  [ Moment ]                  sélecteur — matin / midi / soir

  ⚠️ Warning âge si enfant trop jeune — assignation possible malgré tout

  [ Enregistrer ]   [ Annuler ]

### Affordances globales

- Tap ← / → semaine          → navigation entre semaines
                                semaines passées : lecture seule
                                bouton [Utiliser comme base] visible
- Tap [Copier une semaine]    → sélecteur semaine source
                                → sélecteur semaine cible
                                → confirmation si semaine cible non vide
- Tap [+ Ajouter une tâche]   → ouvre panneau d'édition vide
                                pré-remplit jour et moment si ajout
                                depuis un créneau spécifique
- Tap [Déconnexion]           → session fermée, retour kiosque

### Semaine passée (lecture seule)

  [ ← SEMAINE DU JJ/MM — lecture seule ]
  [ Utiliser comme base pour une semaine future → ]

  Assignations affichées sans affordance d'édition ni suppression.
  États des tâches visibles (réalisée, non réalisée, non renseignée).

### Notes de conception

  - Sidebar persistante sur toutes les vues admin.
  - La charge hebdomadaire est le seul indicateur d'équité —
    pas de charge par jour (un jour à zéro peut être légitime).
  - Valider / Invalider n'apparaissent que sur les tâches
    en état "Déclarée faite".
  - [+ Ajouter] dans un créneau pré-remplit jour et moment
    dans le panneau d'édition.

---

## 4. Gestion des enfants et du catalogue de tâches

### Enfants — Liste

[ SIDEBAR ]          [ CONTENU PRINCIPAL ]

                     [ Enfants ]          [ + Ajouter un enfant ]

                     🟢 Constance   8 ans   PIN ••••   [ Modifier ] [ Archiver ]
                     🔵 Valentin   13 ans   PIN ••••   [ Modifier ] [ Archiver ]
                     🟡 Agathe     10 ans   PIN ••••   [ Modifier ] [ Archiver ]
                     🔴 Jeanne     15 ans   PIN ••••   [ Modifier ] [ Archiver ]
                     🟣 Théophile   6 ans   PIN ••••   [ Modifier ] [ Archiver ]
                     ⚫ Martin       4 ans   PIN ••••   [ Modifier ] [ Archiver ]

### Enfants — Formulaire (création et édition)

                     [ Prénom          ]   champ texte
                     [ Date de naissance ] champ date
                     [ PIN             ]   4 chiffres, masqué
                     [ Confirmer PIN   ]   4 chiffres, masqué
                     [ Couleur         ]   assignée automatiquement,
                                           affichée en lecture seule

                     Âge calculé automatiquement et affiché
                     sous la date de naissance.

                     [ Enregistrer ]   [ Annuler ]

### Enfants — Archivage

                     Confirmation : "Archiver Constance ?
                     Elle disparaîtra des sélecteurs et listes éditables.
                     Ses assignations seront retirées du planning,
                     mais l'historique de ses tâches reste consultable."

                     [ Confirmer ]   [ Annuler ]

---

### Catalogue de tâches — Liste

[ SIDEBAR ]          [ CONTENU PRINCIPAL ]

                     [ Catalogue de tâches ]    [ + Ajouter une tâche ]

                     🍽️ Débarrasser la table   âge min. 6 ans   15 min
                        [ Modifier ] [ Archiver ]

                     🗑️ Sortir la poubelle      âge min. 8 ans   10 min
                        [ Modifier ] [ Archiver ]

                     🍳 Préparer le dîner       âge min. 13 ans  30 min
                        [ Modifier ] [ Archiver ]

### Catalogue de tâches — Formulaire (création et édition)

                     [ Emoji           ]   sélecteur emoji, optionnel
                     [ Libellé         ]   champ texte
                     [ Âge minimum     ]   sélecteur numérique (4 à 18 ans)
                     [ Durée estimée   ]   sélecteur en minutes

                     [ Enregistrer ]   [ Annuler ]

### Catalogue de tâches — Archivage

                     Confirmation : "Archiver Débarrasser la table ?
                     Cette tâche disparaîtra du catalogue et des sélecteurs.
                     Ses assignations seront retirées du planning,
                     mais l'historique reste consultable."

                     [ Confirmer ]   [ Annuler ]

### Notes de conception

  - La couleur enfant est assignée automatiquement à la création,
    non modifiable dans le MVP.
  - Le PIN est affiché masqué dans la liste — le parent
    ne peut pas le consulter, seulement le réinitialiser via le formulaire.
  - L'archivage d'un enfant ou d'une tâche est un soft-delete :
    l'entité disparaît des sélecteurs et listes éditables, ses
    assignations sont retirées du planning, mais l'historique
    des instances déjà créées reste consultable (snapshot figé).
  - Pas de "désarchivage" dans le MVP — opération irréversible
    côté UI (la donnée reste en base et pourra être restaurée
    par un cycle ultérieur si besoin).
  - Les listes sont courtes (6 enfants max, catalogue limité)
    — pas de pagination nécessaire dans le MVP.

---

## 5. Configuration

[ SIDEBAR ]          [ CONTENU PRINCIPAL ]

                     [ Configuration ]

### Moments de la journée

                     Matin    [ 07:00 ] → [ 12:00 ]
                     Midi     [ 12:00 ] → [ 14:00 ]
                     Soir     [ 18:00 ] → [ 21:00 ]

                     [ Enregistrer ]

                     ℹ️ La fin de chaque créneau déclenche
                     le compte à rebours de 30h pour les tâches
                     du moment correspondant.

### Météo

                     [ Ville pour la météo ]

                     [ Paris            ]   champ texte

                     [ Enregistrer ]

### Citation du moment

                     [ Texte de la citation    ]   champ texte long
                     [ Auteur                  ]   champ texte
                     [ Ouvrage (optionnel)      ]   champ texte

                     Affichée sur le kiosque jusqu'à remplacement.

                     [ Enregistrer ]

                     Citation actuelle :
                     "Il faut faire les choses difficiles."
                     — Épictète, Manuel

### Notes de conception

  - Les labels des moments (matin / midi / soir) sont fixes
    dans le MVP — seuls les créneaux horaires sont configurables.
  - Chaque section a son propre bouton Enregistrer —
    pas de validation globale de la page.
  - La citation actuelle est affichée en dessous du formulaire
    pour rappel.
  - Pas de validation de la ville météo dans le MVP —
    si la ville est incorrecte, la météo n'affiche rien.