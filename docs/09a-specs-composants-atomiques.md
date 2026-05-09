# Specs composants atomiques — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

---

## TaskCard

### Responsabilité

Affiche une tâche assignée à un enfant pour un créneau donné.
Gère l'affichage de son état et expose les affordances d'interaction
adaptées au contexte (kiosque ou admin).

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `task` | `Task` | oui | Objet tâche du catalogue (libellé, emoji) |
| `child` | `Child` | oui | Enfant assigné (prénom, couleur) |
| `state` | `TaskState` | oui | État de l'instance de tâche |
| `mode` | `'kiosk' \| 'admin'` | oui | Contexte d'affichage |
| `overdue` | `boolean` | non (défaut: false) | Créneau dépassé, tâche non close |
| `onTap` | `() => void` | non | Callback au tap (kiosque) |
| `onValidate` | `() => void` | non | Callback validation (admin) |
| `onInvalidate` | `() => void` | non | Callback invalidation (admin) |
| `onReset` | `() => void` | non | Callback réinitialisation (admin) |
| `onDelete` | `() => void` | non | Callback suppression (admin) |
| `onEdit` | `() => void` | non | Callback édition (admin) |

### Types

```typescript
type TaskState =
  | 'assigned'   // assignée, rien de fait
  | 'declared'   // déclarée faite par l'enfant
  | 'done'       // réalisée (validée parent ou 30h)
  | 'undone'     // non réalisée (invalidée parent)
  | 'unknown'    // non renseignée (30h sans action)

type Task = {
  id: string
  label: string
  emoji?: string
  minAge: number
  durationMinutes: number
}

type Child = {
  id: string
  firstName: string
  color: ChildColor
}

type ChildColor =
  | 'green' | 'blue' | 'amber'
  | 'coral' | 'purple' | 'gray'
```

### États visuels

| TaskState | overdue | Bordure | Icône état | Opacité |
|-----------|---------|---------|------------|---------|
| `assigned` | false | défaut | aucune | 100% |
| `assigned` | true | amber accentuée | ⚠ amber | 100% |
| `declared` | false | accentuée | ✓ grise | 100% |
| `declared` | true | amber accentuée | ✓ grise + ⚠ amber | 100% |
| `done` | — | défaut | ✓ verte | 70% |
| `undone` | — | défaut | ✗ rouge | 70% |
| `unknown` | — | défaut | ? grise | 50% |

`overdue` n'a pas de sens sur les états finaux (done / undone / unknown)
— le créneau est dépassé mais la tâche est close, pas d'emphase.

### Comportement selon le mode

**Mode kiosque**

- `assigned` → tappable par tous → appelle `onTap` → ouvre PinPad
- `declared` → tappable par un parent → appelle `onTap` → ouvre PinPad
  Le système distingue enfant / parent au moment de la saisie du PIN :
  - PIN enfant sur `declared` → message discret "déjà déclarée faite"
  - PIN parent sur `declared` → choix Valider / Invalider
- États finaux (`done` / `undone` / `unknown`) → non tappables,
  affichage en lecture seule

**Mode admin**

- Tap sur la carte → appelle `onEdit` → ouvre panneau d'édition
- Bouton [✕] toujours visible → appelle `onDelete`
- Boutons [Valider] et [Invalider] visibles uniquement si
  `state === 'declared'` → appellent `onValidate` / `onInvalidate`
- Bouton [Réinitialiser] visible si `state` ∈
  {`declared`, `done`, `undone`, `unknown`} → appelle `onReset`
  → ramène l'instance à `assigned`. Indispensable pour pouvoir
  modifier ou supprimer l'assignation associée si l'instance n'est
  plus à `assigned`.

### Structure interne

```
TaskCard
├── TaskEmoji        (emoji ou icône générique si absent)
├── TaskLabel        (libellé, élément dominant)
├── ChildBadge       (point couleur + prénom)
├── StateIcon        (icône état, alignée à droite)
├── OverdueIndicator (visible si overdue === true et état non final)
└── TaskActions      (admin uniquement)
    ├── ValidateButton   (si state === 'declared')
    ├── InvalidateButton (si state === 'declared')
    ├── ResetButton      (si state ∈ {declared, done, undone, unknown})
    └── DeleteButton     (toujours visible en admin)
```

### Notes d'implémentation

- `overdue` est calculé par le composant parent — `TaskCard`
  ne connaît pas l'heure courante ni le créneau du moment.
- Si `emoji` est absent, afficher une icône Tabler générique
  (`ti-checklist` par défaut).
- La couleur de `ChildBadge` est dérivée de `child.color` —
  map de 6 valeurs vers les tokens Tailwind, définie à l'implémentation.
- Les états `done` / `undone` / `unknown` sont en opacité réduite
  pour signaler qu'ils sont clos.
- `overdue` amber : bordure et icône amber suffisamment distinctes
  du rouge (erreur) et du vert (succès). L'amber signale l'urgence
  sans dramatiser.

---

## ChildBadge

### Responsabilité

Affiche l'identité visuelle d'un enfant : un point coloré et son prénom.
Utilisé dans `TaskCard` pour identifier l'enfant assigné à une tâche.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `child` | `Child` | oui | Enfant (prénom + couleur) |
| `size` | `'sm' \| 'md'` | non (défaut: 'sm') | Taille du badge |

### Variantes visuelles

| size | Diamètre point | Taille texte |
|------|---------------|--------------|
| `sm` | 7px | 9px |
| `md` | 10px | 12px |

`sm` est utilisé dans `TaskCard`. `md` est réservé aux usages
futurs (liste enfants, bandeau charge).

### Structure interne

```
ChildBadge
├── ColorDot   (cercle plein, couleur dérivée de child.color)
└── FirstName  (prénom, texte secondaire)
```

### Notes d'implémentation

- Le point coloré est un `div` avec `border-radius: 50%`.
- La couleur est résolue via une map statique :
  `green → teal-500`, `blue → blue-500`, `amber → amber-500`,
  `coral → orange-500`, `purple → violet-500`, `gray → gray-400`.
  Voir la table de référence dans `00-getting-started.md` §10.
- Pas d'état interactif — composant purement affichage.

---

## StateIcon

### Responsabilité

Affiche l'icône représentant l'état d'une instance de tâche.
Utilisé dans `TaskCard`, aligné à droite du badge enfant.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `state` | `TaskState` | oui | État de la tâche |
| `overdue` | `boolean` | non (défaut: false) | Créneau dépassé |

### Variantes visuelles

| state | overdue | Icône | Couleur |
|-------|---------|-------|---------|
| `assigned` | false | aucune | — |
| `assigned` | true | ti-alert-triangle | amber |
| `declared` | false | ti-check | grise |
| `declared` | true | ti-check + ti-alert-triangle | grise + amber |
| `done` | — | ti-check | verte |
| `undone` | — | ti-x | rouge |
| `unknown` | — | ti-question-mark | grise |

### Notes d'implémentation

- Utilise exclusivement les icônes Tabler outline.
- `declared` + `overdue` affiche deux icônes côte à côte —
  le check gris confirme la déclaration, le triangle amber
  signale l'urgence de validation parentale.
- `done` / `undone` / `unknown` ignorent `overdue` —
  état final, aucune emphase supplémentaire.
- Pas d'état interactif — composant purement affichage.
- Taille icône : 12px dans `TaskCard` (contexte contraint).

---

## PinPad

### Responsabilité

Overlay de saisie du PIN. Identifie l'utilisateur (enfant ou parent)
et déclenche l'action appropriée selon le profil reconnu et l'état
de la tâche sélectionnée.

### Props

| Prop | Type | Obligatoire | Description |
|------|------|-------------|-------------|
| `task` | `Task` | oui | Tâche sélectionnée (libellé, emoji) |
| `child` | `Child` | oui | Enfant assigné à la tâche |
| `taskState` | `TaskState` | oui | État courant de la tâche |
| `onDeclare` | `(childId: string) => void` | non | Tâche déclarée faite par l'enfant |
| `onValidate` | `() => void` | non | Tâche validée par le parent |
| `onInvalidate` | `(reason: InvalidReason) => void` | non | Tâche invalidée par le parent |
| `onClose` | `() => void` | oui | Fermeture de l'overlay |

### Types

```typescript
type InvalidReason =
  | 'refused'  // refus d'obtempérer
  | 'other'    // autre raison

type PinPadStep =
  | 'pin_entry'              // saisie du PIN
  | 'pin_error'              // PIN invalide
  | 'parent_choice'          // choix valider / invalider
  | 'invalid_reason'         // saisie du motif
  | 'child_already_declared' // enfant tape sur tâche déjà déclarée
```

### États internes

| State | Description |
|-------|-------------|
| `digits` | Tableau des chiffres saisis (max 4) |
| `step` | Étape courante du flux (`PinPadStep`) |

### Flux de saisie

```
pin_entry
    │
    ├─→ [4 chiffres saisis]
    │       │
    │       ├─→ PIN reconnu comme enfant
    │       │       │
    │       │       ├─→ taskState === 'assigned'
    │       │       │   → onDeclare(childId) → fermeture
    │       │       │
    │       │       └─→ taskState === 'declared'
    │       │           → child_already_declared
    │       │           → message discret → fermeture auto 1.5s
    │       │
    │       ├─→ PIN reconnu comme parent → parent_choice
    │       │       │
    │       │       ├─→ [Valider] → onValidate() → fermeture
    │       │       │
    │       │       └─→ [Invalider] → invalid_reason
    │       │               │
    │       │               ├─→ [Refus d'obtempérer]
    │       │               │   → onInvalidate('refused') → fermeture
    │       │               │
    │       │               └─→ [Autre raison]
    │       │                   → onInvalidate('other') → fermeture
    │       │
    │       └─→ PIN non reconnu → pin_error
    │               → animation secousse
    │               → digits réinitialisé
    │               → retour pin_entry
    │
    └─→ [Tap ✕ ou extérieur] → onClose()
```

### Structure interne

```
PinPad (overlay plein écran semi-transparent)
└── PinPadModal (carte centrée)
    ├── TaskSummary
    │   ├── TaskEmoji + TaskLabel
    │   └── ChildBadge
    ├── PinDisplay       (4 points, remplis selon digits.length)
    ├── PinGrid          (step === 'pin_entry' || 'pin_error')
    │   ├── DigitButton × 9  (1–9)
    │   ├── ClearButton  (✕)
    │   ├── DigitButton  (0)
    │   └── BackspaceButton  (⌫)
    ├── ParentChoice     (step === 'parent_choice')
    │   ├── ValidateButton
    │   └── InvalidateButton
    ├── InvalidReason    (step === 'invalid_reason')
    │   ├── RefusedButton
    │   └── OtherButton
    └── AlreadyDeclared  (step === 'child_already_declared')
        └── Message discret + fermeture auto
```

### Notes d'implémentation

- La validation du PIN se fait côté serveur —
  le composant ne voit jamais les PINs en clair.
- À 4 chiffres saisis, la validation est déclenchée
  automatiquement — pas de bouton "confirmer".
- Les `DigitButton` font minimum 56px × 56px —
  tappables confortablement par un enfant de 6 ans.
- Pas de clavier virtuel système — le `PinGrid` est le seul
  moyen de saisie pour éviter les comportements inattendus
  sur tablette.
- Pas de limite de tentatives dans le MVP.
- Le retour kiosque immédiat après action est géré par
  le composant parent, pas par `PinPad`.
