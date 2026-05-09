# Specs vues — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

---

## KioskView

### Responsabilité

Vue racine du kiosque public. Charge les données de la semaine,
gère la navigation entre semaines, orchestre l'ouverture du `PinPad`
et les actions qui en découlent.

### Route

`/` — écran par défaut, sans authentification requise.

### État interne

```typescript
type KioskViewState = {
  currentWeekStart: Date
  selectedInstanceId: string | null
  pinPadOpen: boolean
}
```

### Données chargées

| Donnée | Source | Rafraîchissement |
|--------|--------|-----------------|
| Planning semaine | API interne | Au changement de semaine + auto toutes les 15 min |
| Météo | API externe (ville configurée) | Toutes les 15 minutes |
| Saint du jour | API interne | Au montage + au changement de jour |
| Citation du moment | API interne | Au montage + toutes les 15 min |

Le rechargement périodique (15 min) déclenche aussi le recalcul
côté backend des transitions 30h sur les instances éligibles —
voir `docs/06-data-model.md` § Règle des 30h.

### Structure interne

```
KioskView
├── KioskBanner        (bandeau fixe)
├── WeekNavigation     (chevrons ← → + bouton Aujourd'hui)
├── WeekGrid           (mode='kiosk')
├── PinPad             (overlay, si pinPadOpen === true)
└── AdminLink          (lien discret, coin bas droit → /login)
```

### WeekNavigation — bouton Aujourd'hui

Affiché entre les deux chevrons (centré), visible uniquement si
`currentWeekStart` n'est pas le lundi de la semaine en cours.

Au tap : `currentWeekStart` ← lundi de la semaine contenant `now`,
puis rechargement du planning de cette semaine.

La mise en avant visuelle de la colonne du jour est gérée par
`DayColumn` via la prop `isToday` — pas besoin d'un état dédié
dans `KioskView`.

### Flux d'interaction

**Tap sur une tâche**
1. `selectedInstanceId` ← id de l'instance
2. `pinPadOpen` ← true
3. `PinPad` s'ouvre avec la tâche et l'enfant concernés

**PIN enfant reconnu sur tâche `assigned`**
1. API : tâche → `declared`
2. `pinPadOpen` ← false, `selectedInstanceId` ← null
3. Planning rechargé

**PIN parent reconnu**
1. `PinPad` passe en étape `parent_choice`
2. Si Valider → API : tâche → `done` → fermeture → rechargement
3. Si Invalider → étape `invalid_reason` → API : tâche → `undone`
   → fermeture → rechargement

**Navigation semaine**
1. `currentWeekStart` ← lundi semaine précédente ou suivante
2. Planning rechargé pour la nouvelle semaine

### Notes d'implémentation

- Le rechargement du planning après action est optimiste —
  mise à jour locale immédiate, confirmation API en arrière-plan.
- `WeekNavigation` n'a pas de limite — navigation possible
  dans le passé et le futur depuis le kiosque.
- Le bouton Aujourd'hui de `WeekNavigation` est conditionnel —
  masqué quand on est déjà sur la semaine courante.

---

## PlanningView

### Responsabilité

Vue principale de l'interface admin. Affiche le planning éditable
de la semaine, la charge hebdomadaire, et orchestre les actions
d'assignation, validation et clonage.

### Route

`/admin/planning` — protégée, redirige vers `/login` si pas de session.

### État interne

```typescript
type PlanningViewState = {
  currentWeekStart: Date
  editingInstanceId: string | null
  assignmentPanelOpen: boolean
  clonePanelOpen: boolean
  isReadOnly: boolean
}
```

### Données chargées

| Donnée | Source | Rafraîchissement |
|--------|--------|-----------------|
| Planning semaine | API interne | Au changement de semaine |
| Liste enfants | API interne | Au montage |
| Catalogue tâches | API interne | Au montage |
| Charge hebdomadaire | Calculée depuis le planning | Synchrone |

### Structure interne

```
PlanningView
├── AdminSidebar           (activeSection='planning')
└── PlanningContent
    ├── WeekNavigation     (chevrons ← → + label semaine)
    ├── ReadOnlyBanner     (visible si isReadOnly)
    ├── ChargeBar          (charge hebdo par enfant)
    ├── CloneButton        (ouvre ClonePanel)
    ├── WeekGrid           (mode='admin', désactivé si isReadOnly)
    ├── AssignmentPanel    (overlay, si assignmentPanelOpen)
    └── ClonePanel         (overlay, si clonePanelOpen)
```

### Calcul isReadOnly

```typescript
const isReadOnly = (weekStart: Date, now: Date): boolean => {
  const currentWeekStart = getMonday(now)
  return weekStart < currentWeekStart
}
```

### AssignmentPanel — overlay d'édition d'assignation

Champs :

| Champ | Type |
|-------|------|
| Tâche | sélecteur — liste du catalogue (non archivées) |
| Enfant | sélecteur — liste des enfants (non archivés) |
| Jour | sélecteur — lun. → dim. |
| Moment | sélecteur — matin / midi / soir |

Comportement :
- Pré-remplit jour et moment si ouvert depuis un `MomentBlock`
- Affiche warning amber si âge enfant < âge minimum tâche
- Warning non bloquant — enregistrement possible malgré tout
- [Enregistrer] → API → fermeture → rechargement planning
- [Annuler] → fermeture sans action

### Conflit 409 lors d'une modification ou suppression d'assignation

Si l'instance de la semaine en cours a quitté l'état `assigned`
(déclarée, réalisée, non réalisée, non renseignée), l'API rejette
la modification ou la suppression d'assignation avec 409 Conflict.

L'UI affiche un message inline clair, par exemple :
*"Impossible de modifier cette assignation — l'instance de cette
semaine est déjà [état]. Réinitialisez-la d'abord depuis le
planning."*

Le parent admin doit alors fermer le panneau, cliquer
[Réinitialiser] sur la TaskCard concernée, puis ré-essayer.

### ClonePanel — overlay de clonage

Champs :

| Champ | Type |
|-------|------|
| Semaine source | sélecteur — liste des semaines passées |
| Semaine cible | sélecteur — liste des semaines futures |

Comportement :
- Si semaine cible non vide → confirmation avant écrasement
- [Cloner] → API → fermeture → navigation vers semaine cible
- [Annuler] → fermeture sans action

### Flux navigation semaine

```
← semaine précédente
    → si semaine passée : isReadOnly = true, ReadOnlyBanner visible
    → WeekGrid désactivé (pas d'affordance d'édition)
    → CloneButton libellé "Utiliser comme base"

→ semaine suivante
    → si pas de planning : proposition de copier la semaine précédente
    → si planning existant : affichage direct
```

### Notes d'implémentation

- Les modifications sont publiées en temps réel — pas de bouton
  "publier", chaque action API met à jour le kiosque immédiatement.
- La charge hebdomadaire est calculée en mémoire depuis les données
  du planning — pas d'appel API dédié.

---

## ChildrenView

### Responsabilité

Gestion des profils enfants : liste, création, édition, suppression.

### Route

`/admin/children` — protégée.

### Structure interne

```
ChildrenView
├── AdminSidebar        (activeSection='children')
└── ChildrenContent
    ├── ChildList       (liste des profils avec actions)
    └── ChildForm       (overlay — création et édition)
```

### ChildForm — champs

| Champ | Type | Validation |
|-------|------|------------|
| Prénom | texte | obligatoire |
| Date de naissance | date | obligatoire, passée |
| PIN | 4 chiffres masqué | obligatoire |
| Confirmer PIN | 4 chiffres masqué | doit correspondre au PIN |
| Couleur | lecture seule | assignée automatiquement à la création |

Âge calculé automatiquement et affiché sous la date de naissance.

### Archivage (soft-delete)

Le bouton se libelle [Archiver], pas [Supprimer].
Confirmation : "Archiver [prénom] ? Il/elle disparaîtra des
sélecteurs et listes éditables. Ses assignations seront retirées
du planning, mais l'historique de ses tâches reste consultable."

Côté API : `DELETE /api/v1/children/{id}` réalise un soft-delete
(`archived_at = NOW()`) + suppression des assignations associées.
Les instances historiques restent intactes via leur snapshot.

### Notes d'implémentation

- La couleur est assignée automatiquement à la création dans l'ordre
  de la palette — non modifiable dans le MVP.
- Le PIN est affiché masqué dans la liste — le parent ne peut pas
  le consulter, seulement le réinitialiser via le formulaire.
- Les PINs sont uniques globalement (parents et enfants partagent
  le même espace 0000–9999) — unicité garantie par la table
  partagée `kiosk_pins`. Validation côté serveur.
- La liste affiche les enfants non archivés
  (`WHERE archived_at IS NULL`).
- Pas de désarchivage dans le MVP.

---

## CatalogView

### Responsabilité

Gestion du catalogue de tâches : liste, création, édition, suppression.

### Route

`/admin/catalog` — protégée.

### Structure interne

```
CatalogView
├── AdminSidebar        (activeSection='catalog')
└── CatalogContent
    ├── TaskList        (liste des tâches avec actions)
    └── TaskForm        (overlay — création et édition)
```

### TaskForm — champs

| Champ | Type | Validation |
|-------|------|------------|
| Emoji | sélecteur emoji | optionnel |
| Libellé | texte | obligatoire |
| Âge minimum | numérique (4–18) | obligatoire |
| Durée estimée | numérique en minutes | obligatoire |

### Archivage (soft-delete)

Le bouton se libelle [Archiver], pas [Supprimer].
Confirmation : "Archiver [libellé] ? Cette tâche disparaîtra
du catalogue et des sélecteurs. Ses assignations seront retirées
du planning, mais l'historique reste consultable."

Côté API : `DELETE /api/v1/tasks/{id}` réalise un soft-delete
(`archived_at = NOW()`) + suppression des assignations associées.
Les instances historiques restent intactes via leur snapshot.

### Notes d'implémentation

- Si emoji absent, `TaskCard` affiche `ti-checklist` par défaut.
- Pas de pagination dans le MVP — le catalogue est limité en volume.
- La liste affiche les tâches non archivées
  (`WHERE archived_at IS NULL`).
- Pas de désarchivage dans le MVP.

---

## SettingsView

### Responsabilité

Configuration du kiosque : créneaux horaires des moments,
ville météo, citation du moment.

### Route

`/admin/settings` — protégée.

### Structure interne

```
SettingsView
├── AdminSidebar           (activeSection='settings')
└── SettingsContent
    ├── MomentsSection     (créneaux matin / midi / soir)
    ├── WeatherSection     (ville météo)
    └── QuoteSection       (citation du moment)
```

### MomentsSection — champs par moment

| Champ | Type | Validation |
|-------|------|------------|
| Heure de début | time (HH:mm) | obligatoire |
| Heure de fin | time (HH:mm) | obligatoire, après début |

La fin de chaque créneau déclenche le compte à rebours de 30h
pour les tâches du moment correspondant.

### WeatherSection — champs

| Champ | Type | Validation |
|-------|------|------------|
| Ville | texte | obligatoire |

Pas de validation de la ville dans le MVP — si incorrecte,
la météo n'affiche rien sur le kiosque.

### QuoteSection — champs

| Champ | Type | Validation |
|-------|------|------------|
| Texte | texte long | obligatoire |
| Auteur | texte | obligatoire |
| Ouvrage | texte | optionnel |

La citation actuelle est affichée sous le formulaire pour rappel.
Elle reste affichée sur le kiosque jusqu'à remplacement.

### Notes d'implémentation

- Les labels des moments (matin / midi / soir) sont fixes dans
  le MVP — seuls les créneaux horaires sont configurables.
- Chaque section a son propre bouton [Enregistrer] —
  pas de validation globale de la page.
