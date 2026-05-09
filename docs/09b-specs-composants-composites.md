# Specs composants composites — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

---

## MomentBlock

### Responsabilité

Affiche un créneau de la journée (matin, midi ou soir) avec
l'ensemble des tâches qui lui sont assignées pour un jour donné.
Gère l'affordance d'ajout d'une tâche (mode admin uniquement).

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `moment` | `Moment` | oui | Créneau (label, heure début, heure fin) |
| `tasks` | `TaskInstance[]` | oui | Instances de tâches du créneau |
| `mode` | `'kiosk' \| 'admin'` | oui | Contexte d'affichage |
| `now` | `Date` | oui | Heure courante pour calcul overdue |
| `onTaskTap` | `(instanceId: string) => void` | non | Tap sur une tâche (kiosque) |
| `onTaskEdit` | `(instanceId: string) => void` | non | Édition tâche (admin) |
| `onTaskDelete` | `(instanceId: string) => void` | non | Suppression tâche (admin) |
| `onTaskValidate` | `(instanceId: string) => void` | non | Validation tâche (admin) |
| `onTaskInvalidate` | `(instanceId: string) => void` | non | Invalidation tâche (admin) |
| `onTaskReset` | `(instanceId: string) => void` | non | Réinitialisation tâche (admin) |
| `onAddTask` | `(momentId: string) => void` | non | Ajout tâche (admin) |

### Types

```typescript
type Moment = {
  id: string
  label: 'matin' | 'midi' | 'soir'
  startTime: string  // format 'HH:mm'
  endTime: string    // format 'HH:mm'
}

type TaskInstance = {
  id: string
  task: Task
  child: Child
  state: TaskState
}
```

### Calcul overdue

`overdue` est calculé dans `MomentBlock` pour chaque `TaskInstance` :

```typescript
const isOverdue = (instance: TaskInstance, moment: Moment, now: Date): boolean => {
  if (['done', 'undone', 'unknown'].includes(instance.state)) return false
  const [hours, minutes] = moment.endTime.split(':').map(Number)
  const endTime = new Date(now)
  endTime.setHours(hours, minutes, 0, 0)
  return now > endTime
}
```

### Structure interne

```
MomentBlock
├── MomentLabel        (label en majuscules, ex: MATIN)
├── TaskCard[]         (une par TaskInstance, avec overdue calculé)
└── AddTaskButton      (mode admin uniquement, en pointillés)
```

### Variantes visuelles

- Créneau vide en mode kiosque : rien n'est affiché
  (pas de message "aucune tâche")
- Créneau vide en mode admin : seul `AddTaskButton` est affiché
- `AddTaskButton` pré-remplit `momentId` dans le panneau d'édition

### Notes d'implémentation

- `MomentBlock` est responsable du calcul `overdue` —
  il reçoit `now` comme prop pour faciliter les tests unitaires
  (pas de `new Date()` direct dans le composant).
- L'ordre des `TaskCard` dans un créneau est l'ordre de création
  de l'assignation — pas de tri particulier dans le MVP.
- Le label du moment est toujours en majuscules via CSS,
  pas en dur dans le texte.

---

## DayColumn

### Responsabilité

Affiche une colonne jour complète avec ses trois créneaux (matin,
midi, soir). Gère la mise en avant visuelle du jour courant.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `date` | `Date` | oui | Date du jour représenté |
| `moments` | `MomentWithTasks[]` | oui | Les trois créneaux avec leurs tâches |
| `mode` | `'kiosk' \| 'admin'` | oui | Contexte d'affichage |
| `now` | `Date` | oui | Heure courante (passée aux MomentBlock) |
| `isToday` | `boolean` | non (défaut: false) | Mise en avant visuelle |
| `onTaskTap` | `(instanceId: string) => void` | non | Propagé aux MomentBlock |
| `onTaskEdit` | `(instanceId: string) => void` | non | Propagé aux MomentBlock |
| `onTaskDelete` | `(instanceId: string) => void` | non | Propagé aux MomentBlock |
| `onTaskValidate` | `(instanceId: string) => void` | non | Propagé aux MomentBlock |
| `onTaskInvalidate` | `(instanceId: string) => void` | non | Propagé aux MomentBlock |
| `onAddTask` | `(momentId: string) => void` | non | Propagé aux MomentBlock |

### Types

```typescript
type MomentWithTasks = {
  moment: Moment
  tasks: TaskInstance[]
}
```

### Variantes visuelles

| isToday | Bordure | Fond |
|---------|---------|------|
| false | défaut 0.5px | transparent |
| true | accentuée 1.5px | background-secondary |

### En-tête de colonne

Format : `Mer 7 · auj.` si `isToday`, sinon `Mer 7`.
Jour abrégé 3 lettres + numéro du jour du mois.

### Structure interne

```
DayColumn
├── DayHeader      (jour abrégé + numéro, badge "auj." si isToday)
└── MomentBlock[]  (matin, midi, soir — toujours les trois)
```

### Notes d'implémentation

- `DayColumn` propage `now` et tous les callbacks aux `MomentBlock`
  sans les transformer — c'est un composant d'orchestration.
- Les trois `MomentBlock` sont toujours rendus, même si vides —
  la hauteur des colonnes reste cohérente visuellement.
- `isToday` est calculé par le composant parent (`WeekGrid`)
  en comparant `date` à la date du jour.
- Sur mobile portrait, `DayColumn` est le composant que le
  carrousel (itération 2) affichera en plein écran.

---

## WeekGrid

### Responsabilité

Affiche la grille des 7 colonnes jours pour une semaine donnée.
Calcule `isToday` pour chaque colonne et orchestre la navigation
temporelle entre jours.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `weekStart` | `Date` | oui | Date du lundi de la semaine affichée |
| `days` | `DayData[]` | oui | Données des 7 jours (moments + tâches) |
| `mode` | `'kiosk' \| 'admin'` | oui | Contexte d'affichage |
| `now` | `Date` | oui | Heure courante (passée aux DayColumn) |
| `onTaskTap` | `(instanceId: string) => void` | non | Propagé aux DayColumn |
| `onTaskEdit` | `(instanceId: string) => void` | non | Propagé aux DayColumn |
| `onTaskDelete` | `(instanceId: string) => void` | non | Propagé aux DayColumn |
| `onTaskValidate` | `(instanceId: string) => void` | non | Propagé aux DayColumn |
| `onTaskInvalidate` | `(instanceId: string) => void` | non | Propagé aux DayColumn |
| `onAddTask` | `(momentId: string, date: Date) => void` | non | Propagé aux DayColumn |

### Types

```typescript
type DayData = {
  date: Date
  moments: MomentWithTasks[]
}
```

### Calcul isToday

```typescript
const isToday = (date: Date, now: Date): boolean => {
  return (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  )
}
```

### Structure interne

```
WeekGrid
└── DayColumn[]  (7 colonnes, lundi → dimanche)
    chaque DayColumn reçoit isToday calculé localement
```

### Notes d'implémentation

- `WeekGrid` ne gère pas la navigation entre semaines —
  c'est la responsabilité de `KioskView` et `PlanningView`.
- La grille est en CSS Grid : `grid-template-columns: repeat(7, 1fr)`.
- Sur mobile portrait, `WeekGrid` n'est pas utilisé —
  le carrousel (itération 2) remplace ce composant.
- `days` doit toujours contenir exactement 7 éléments —
  le composant ne gère pas les semaines incomplètes.

---

## ChargeBar

### Responsabilité

Affiche la charge hebdomadaire totale (en minutes) pour chaque
enfant de la famille. Utilisé uniquement dans la vue planning admin
pour visualiser l'équité de la répartition.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `children` | `ChildCharge[]` | oui | Enfants avec leur charge calculée |

### Types

```typescript
type ChildCharge = {
  child: Child
  totalMinutes: number
}
```

### Variantes visuelles

La charge est affichée comme une liste horizontale de badges :

```
🟢 Constance  120 min   🔵 Valentin  95 min   🟡 Agathe  110 min
```

Pas de barre de progression dans le MVP — le total en minutes
est suffisant pour détecter un déséquilibre à l'œil.

### Mise en évidence des déséquilibres

Un enfant est considéré en déséquilibre si son `totalMinutes`
s'écarte de plus de 30% de la moyenne du groupe.
Dans ce cas, son badge est affiché avec une couleur amber.

```typescript
const average = totalMinutes.reduce((a, b) => a + b, 0) / children.length
const isUnbalanced = (minutes: number) => Math.abs(minutes - average) / average > 0.3
```

### Structure interne

```
ChargeBar
└── ChildChargeItem[]  (un par enfant)
    ├── ColorDot       (couleur enfant)
    ├── FirstName      (prénom)
    └── TotalMinutes   (total en minutes, amber si déséquilibre)
```

### Notes d'implémentation

- `totalMinutes` est calculé côté serveur ou dans le hook
  de données de `PlanningView` — `ChargeBar` est purement affichage.
- Le seuil de 30% est une valeur par défaut raisonnable —
  à ajuster selon le retour d'usage réel.
- Martin (4 ans) peut avoir un total à zéro — c'est normal,
  ne pas afficher de déséquilibre dans ce cas.
- Les enfants sont affichés dans l'ordre de création du profil,
  pas triés par charge.

---

## KioskBanner

### Responsabilité

Affiche le bandeau supérieur fixe de la vue kiosque : saint du jour
et nom du jour à gauche, citation du moment au centre, météo à droite.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `date` | `Date` | oui | Date du jour (saint + nom du jour) |
| `weather` | `WeatherData \| null` | oui | Données météo (null si indisponible) |
| `quote` | `Quote \| null` | oui | Citation du moment (null si non configurée) |

### Types

```typescript
type WeatherData = {
  icon: WeatherIcon
  temperatureCelsius: number
  windKmh: number
}

type WeatherIcon =
  | 'sun' | 'cloud' | 'rain'
  | 'storm' | 'snow' | 'fog'

type Quote = {
  text: string
  author: string
  work?: string
}
```

### Correspondance icônes météo

| WeatherIcon | Icône Tabler |
|-------------|-------------|
| `sun` | `ti-sun` |
| `cloud` | `ti-cloud` |
| `rain` | `ti-cloud-rain` |
| `storm` | `ti-storm` |
| `snow` | `ti-snowflake` |
| `fog` | `ti-mist` |

### Comportement si données indisponibles

| Donnée | Comportement si null |
|--------|---------------------|
| `weather` | Section météo masquée sans message d'erreur |
| `quote` | Section citation masquée sans message d'erreur |

### Structure interne

```
KioskBanner
├── BannerLeft
│   ├── SaintOfDay    (ex: "Ste Jeanne")
│   └── DayName       (ex: "mercredi")
├── BannerCenter
│   └── QuoteDisplay  (texte + auteur, masqué si quote === null)
└── BannerRight
    ├── WeatherDisplay (icône + température + vent,
    │                   masqué si weather === null)
    └── TransportSlot  (réservé pour les horaires de bus, cycle
                        ultérieur — non rendu dans le MVP, mais
                        l'espace est prévu dans la grille pour
                        éviter une refonte du bandeau plus tard)
```

### Notes d'implémentation

- `KioskBanner` est purement affichage — le chargement des données
  est géré par `KioskView` via des hooks dédiés.
- Le saint du jour est calculé côté serveur.
- Le bandeau est `position: sticky; top: 0` — reste visible
  même si la grille défile verticalement.
- La citation est tronquée à 120 caractères avec ellipse
  si le texte est trop long.
- Rafraîchissement météo et planning : toutes les 15 minutes
  via un intervalle dans `KioskView`. Ce même intervalle déclenche
  côté backend le recalcul des bascules 30h.

---

## AdminSidebar

### Responsabilité

Affiche la navigation persistante de l'interface d'administration.
Indique la section active et gère la déconnexion.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `activeSection` | `AdminSection` | oui | Section courante (item actif) |
| `onNavigate` | `(section: AdminSection) => void` | oui | Changement de section |
| `onLogout` | `() => void` | oui | Déconnexion |

### Types

```typescript
type AdminSection =
  | 'planning'
  | 'children'
  | 'catalog'
  | 'settings'
```

### Structure interne

```
AdminSidebar
├── SidebarItem — Planning      (ti-calendar)
├── SidebarItem — Enfants       (ti-users)
├── SidebarItem — Catalogue     (ti-list)
├── SidebarItem — Configuration (ti-settings)
├── SidebarSeparator
└── SidebarLogout               (ti-logout)
```

### Variantes visuelles

| État item | Fond | Bordure | Texte |
|-----------|------|---------|-------|
| inactif | transparent | aucune | secondaire |
| actif | background-primary | 0.5px défaut | primaire, 500 |
| hover | background-secondary | aucune | primaire |

### Notes d'implémentation

- Largeur fixe 140px — pas de version rétractable dans le MVP.
- `SidebarLogout` est poussé en bas via `margin-top: auto`
  sur un conteneur flex colonne.
- Navigation interne React (React Router) — pas de rechargement.
- Pas de sous-navigation dans le MVP.
