# User flows — Family Control Panel App
_Version 0.2 — mai 2025 — Cycle 1 MVP_

---

## Flow A — Le parent configure le planning

```mermaid
flowchart TD
    A([Thomas ouvre l'app]) --> B[Écran de login]
    B --> C{Identifiants valides ?}
    C -- Non --> B
    C -- Oui --> D[Vue planning — semaine courante\nCharge hebdo par enfant]

    D --> NAV{Navigation semaine ?}
    NAV -- Précédente --> PAST[Semaine passée\nLecture seule]
    NAV -- Suivante --> FUT[Semaine future\nÉditable]
    NAV -- Reste --> ACTION

    PAST --> CLONE[Utiliser comme base\nSélecteur semaine cible]
    CLONE --> VIDE{Semaine cible vide ?}
    VIDE -- Oui --> CLONED[Planning cloné]
    VIDE -- Non --> CONFIRM[Confirmation]
    CONFIRM --> CLONED
    CLONED --> D

    FUT --> EXIST{Planning existant ?}
    EXIST -- Non --> PROP[Proposition : copier\nsemaine précédente ?]
    PROP -- Accepte --> DISPLAY
    PROP -- Refuse --> DISPLAY
    EXIST -- Oui --> DISPLAY

    DISPLAY[Planning affiché\nCharge hebdo par enfant] --> ACTION

    ACTION{Action ?}

    ACTION -- Enfants --> E1[Liste enfants\nCréer / modifier / supprimer]
    E1 --> E2[Formulaire : prénom, naissance, PIN]
    E2 --> E3[Profil enregistré] --> ACTION

    ACTION -- Catalogue --> T1[Liste tâches\nCréer / modifier / supprimer]
    T1 --> T2[Formulaire : libellé, âge minimum, durée]
    T2 --> T3[Tâche enregistrée] --> ACTION

    ACTION -- Planning --> P1[Assignation\nTâche + enfant + jour + moment]
    P1 --> P2{Âge minimum respecté ?}
    P2 -- Non --> P3[Warning affiché\nAssignation possible]
    P3 --> P4[Assignation enregistrée\nCharge recalculée]
    P2 -- Oui --> P4
    P4 --> P5{Autre modification ?}
    P5 -- Oui --> P1
    P5 -- Non --> ACTION

    ACTION -- Validation --> V1[Liste tâches déclarées faites\nTous les enfants]
    V1 --> V2{Action parent ?}
    V2 -- Valider --> V3[Tâche → Réalisée ✓] --> ACTION
    V2 -- Invalider --> V4[Motif : refus / autre raison]
    V4 --> V5[Tâche → Non réalisée ✗] --> ACTION

    ACTION -- Terminé --> END[Planning publié en temps réel\nVisible sur le kiosque]
    END --> Z([Fin])
```

---

## Flow B — Constance consulte et coche ses tâches

```mermaid
flowchart TD
    A([Constance s'approche du kiosque]) --> B[Vue kiosque\nSemaine, centré sur aujourd'hui\nTâches groupées par moment]
    B --> ACTION{Action ?}

    ACTION -- Naviguer --> NAV[Jour suivant ou précédent]
    NAV --> NAVD[Vue mise à jour\nJour sélectionné]
    NAVD --> ACTION

    ACTION -- Déclarer une tâche faite --> TAP[Constance tape sur une tâche\nTâche mise en surbrillance]
    TAP --> PIN[Saisie du PIN enfant\nPavé numérique affiché]
    PIN --> VALID{PIN valide ?}
    VALID -- Non --> PIN
    VALID -- Oui --> DONE[Tâche → Déclarée faite\nSous l'identité de Constance]
    DONE --> PUBLIC[Retour mode public immédiat\nKiosque sans utilisateur identifié]
    PUBLIC --> AUTRE{Autre action ?}
    AUTRE -- Oui --> ACTION
    AUTRE -- Non --> IDLE[Kiosque en attente\nPrêt pour le prochain utilisateur]
    IDLE --> Z([Fin])
```

---

## Flow C — Thomas consulte et valide depuis le kiosque

```mermaid
flowchart TD
    A([Thomas lève les yeux vers la tablette]) --> B[Vue kiosque\nSemaine, centré sur aujourd'hui\nTâches groupées par moment]
    B --> ACTION{Action ?}

    ACTION -- Consulter --> C[Thomas consulte la colonne du jour\nÉtat des tâches visible]
    C --> D{Information suffisante ?}
    D -- Non --> NAV[Navigation jour précédent ou suivant]
    NAV --> D
    D -- Oui --> E[Thomas appelle l'enfant concerné\nLe planning est indiscutable]
    E --> ACTION

    ACTION -- Valider une tâche --> V1[Thomas tape sur une tâche\ndéclarée faite]
    V1 --> V2[Saisie du PIN parent\nPavé numérique affiché]
    V2 --> V3{PIN valide ?}
    V3 -- Non --> V2
    V3 -- Oui --> V4{Action ?}
    V4 -- Valider --> V5[Tâche → Réalisée ✓\nRetour mode public]
    V4 -- Invalider --> V6[Motif : refus / autre raison]
    V6 --> V7[Tâche → Non réalisée ✗\nRetour mode public]
    V5 --> ACTION
    V7 --> ACTION

    ACTION -- Accès admin --> LOGIN[Écran de login\n→ Flow A]

    ACTION -- Terminé --> IDLE[Kiosque en attente\nPrêt pour le prochain utilisateur]
    IDLE --> Z([Fin])
```

---

## Machine à états — Assignation de tâche

```mermaid
stateDiagram-v2
    [*] --> Assignée

    Assignée --> DéclaréeFaite : Enfant déclare via PIN kiosque
    Assignée --> Réalisée : Parent valide directement
    Assignée --> NonRéalisée : Parent marque non faite + motif
    Assignée --> NonRenseignée : 30h après fin du créneau\nsans aucune action

    DéclaréeFaite --> Réalisée : Parent valide\nou 30h sans réaction parent
    DéclaréeFaite --> NonRéalisée : Parent invalide + motif

    Réalisée --> [*]
    NonRéalisée --> [*]
    NonRenseignée --> [*]
```