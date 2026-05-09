# Getting started — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

---

## 1. Stack technique

### Frontend
- React 18 + TypeScript
- Vite (bundler)
- Tailwind CSS
- shadcn/ui (composants)
- React Router v6 (navigation)
- TanStack Query (data fetching + cache)

### Backend
- Python 3.14
- uv (gestionnaire de paquets et venv)
- pyproject.toml (dépendances + config outils)
- FastAPI
- Pydantic v2 (modélisation des objets, schémas de validation)
- pydantic-settings (variables d'environnement typées)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- python-jose (JWT)
- passlib + bcrypt (hash des mots de passe)
- httpx (appels API externes : météo)

### Outils backend (group dev)
- mypy (type-checking strict)
- black (formatage)
- ruff (linter)
- pytest (tests)

### Conventions Python (obligatoires)
- **Annotations de typage systématiques** : toute méthode ou
  fonction Python doit annoter ses paramètres et sa valeur de
  retour. Pas d'exception, y compris pour les fonctions privées,
  les helpers de tests et les fonctions sans retour explicite
  (utiliser `-> None`).
- **Appels par mots-clés** : à l'invocation d'une méthode ou
  fonction, passer tous les arguments par keyword (`foo(name="x",
  age=12)`), sauf si la fonction n'accepte qu'un seul paramètre.
  Améliore la lisibilité et la robustesse aux refactos.
- mypy est exécuté en mode strict — les fonctions sans annotation
  font échouer `make lint`.

### Base de données
- PostgreSQL 16

### Infrastructure
- Docker + Docker Compose (développement local)
- Helm (déploiement K3S sur VPS OVH)
- GitHub Actions (CI/CD)
- GitHub Container Registry ghcr.io (registre Docker)

### Outils de développement
- Claude Code (implémentation)
- gh CLI (interaction GitHub depuis le terminal)
- pnpm (gestionnaire de paquets Node)

---

## 2. Structure du monorepo

```
family-control-panel/
├── .github/
│   └── workflows/
│       ├── ci.yml              # tests + lint sur chaque PR
│       └── build.yml           # build Docker + push ghcr.io sur merge main
├── docs/                       # conception (source de vérité)
│   ├── 00-getting-started.md   # ce fichier
│   ├── 00-contexte-et-roadmap.md
│   ├── 01-prd.md
│   ├── 02-personnas.md
│   ├── 03-user-stories.md
│   ├── 04a-scenario-key-path.md
│   ├── 05-user-flows.md
│   ├── 06-data-model.md
│   ├── 06b-sitemap.md
│   ├── 07-breadboards.md
│   ├── 08-fat-marker-sketches.md
│   ├── 09a-specs-composants-atomiques.md
│   ├── 09b-specs-composants-composites.md
│   └── 09c-specs-vues.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── atomic/         # TaskCard, ChildBadge, StateIcon, PinPad
│   │   │   ├── composite/      # MomentBlock, DayColumn, WeekGrid, etc.
│   │   │   └── ui/             # composants shadcn/ui générés
│   │   ├── views/              # KioskView, PlanningView, etc.
│   │   ├── hooks/              # hooks React personnalisés
│   │   ├── lib/                # utilitaires, constantes
│   │   ├── types/              # types TypeScript partagés
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── children.py
│   │   │       ├── tasks.py
│   │   │       ├── planning.py
│   │   │       ├── instances.py
│   │   │       ├── config.py
│   │   │       └── kiosk.py
│   │   ├── models/             # modèles SQLAlchemy
│   │   ├── schemas/            # schémas Pydantic
│   │   ├── services/           # logique métier
│   │   ├── core/
│   │   │   ├── config.py       # pydantic-settings
│   │   │   ├── security.py     # JWT, hashing
│   │   │   └── database.py     # session SQLAlchemy
│   │   └── main.py
│   ├── alembic/                # migrations
│   ├── tests/
│   ├── pyproject.toml          # dépendances + config mypy/black/ruff
│   └── Dockerfile
├── helm/                       # chart Helm pour K3S
│   └── family-control-panel/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── docker-compose.yml          # développement local
├── Makefile                    # install-dev, lint, test, run
└── README.md
```

---

## 3. Setup initial

### Prérequis
```bash
# Sur Linux (équivalent brew sur macOS)
sudo apt install gh git docker make
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv
corepack enable && corepack prepare pnpm@latest --activate  # pnpm

# Python 3.14 via uv
uv python install 3.14

# Authentification GitHub
gh auth login

# Vérification
gh auth status
uv --version
pnpm --version
```

### Créer le repo GitHub
```bash
gh repo create family-control-panel \
  --private \
  --description "Family Control Panel — gestion des tâches familiales" \
  --clone

cd family-control-panel
```

### Configurer Claude Code
```bash
# Installer Claude Code
npm install -g @anthropic/claude-code

# Dans le repo
claude
# → Claude Code lit automatiquement le repo et docs/
```

### Variables d'environnement
Créer un fichier `.env` à la racine (non commité) :

```env
# Base de données
DATABASE_URL=postgresql://fcp:fcp@localhost:5432/fcp

# Auth
SECRET_KEY=<générer avec: openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Météo (API OpenWeatherMap, gratuite jusqu'à 1000 appels/jour)
OPENWEATHER_API_KEY=<ta clé>
WEATHER_CITY=Paris

# Environnement
ENVIRONMENT=development
```

### Lancer l'environnement local
```bash
# Installer toutes les dépendances (front + back) via le Makefile
make install-dev

# Base de données PostgreSQL en Docker
docker compose up -d db

# Backend (terminal 1)
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
pnpm dev
```

### Makefile — cibles utiles
```makefile
install-dev:    ## installe les dépendances backend + frontend (group dev)
	cd backend && uv sync --group dev
	cd frontend && pnpm install

lint:           ## mypy + black sur le backend
	cd backend && uv run mypy app
	cd backend && uv run black --check app

format:         ## applique black
	cd backend && uv run black app

test:           ## pytest backend
	cd backend && uv run pytest
```

---

## 4. Modèle de données PostgreSQL

### Tables

```sql
-- Parents (2 par foyer)
CREATE TABLE parents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enfants
-- Soft-delete : archived_at = "Archivé" dans l'UI.
-- Un enfant archivé est masqué des sélecteurs et listes éditables
-- mais reste référencé par les instances historiques via leur snapshot.
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    color VARCHAR(20) NOT NULL,  -- green|blue|amber|coral|purple|gray
    sort_order INTEGER NOT NULL DEFAULT 0,
    archived_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PINs kiosque partagés entre parents et enfants.
-- L'unicité globale est garantie par la PRIMARY KEY sur `pin`.
-- Aucune convention de plage : les 10000 combinaisons sont disponibles
-- pour l'ensemble du foyer.
-- holder_type : 'parent' | 'child' — détermine la table cible.
-- (holder_type, holder_id) UNIQUE : un holder a au plus un PIN actif.
CREATE TABLE kiosk_pins (
    pin CHAR(4) PRIMARY KEY,
    holder_type VARCHAR(10) NOT NULL
        CHECK (holder_type IN ('parent', 'child')),
    holder_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (holder_type, holder_id)
);

-- Cohérence holder_id ↔ table cible : maintenue côté applicatif
-- (FK polymorphe non exprimable directement en SQL standard).
-- Le backend doit vérifier que holder_id existe bien dans la table
-- correspondante au holder_type avant INSERT.

-- Moments de la journée (matin / midi / soir)
CREATE TABLE moments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(20) NOT NULL,  -- matin|midi|soir
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    sort_order INTEGER NOT NULL  -- 0=matin, 1=midi, 2=soir
);

-- Catalogue de tâches
-- Soft-delete : archived_at = "Archivé" dans l'UI.
-- Une tâche archivée est masquée des sélecteurs et du catalogue
-- mais reste référencée par les instances historiques via leur snapshot.
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(200) NOT NULL,
    emoji VARCHAR(10),
    min_age INTEGER NOT NULL DEFAULT 4,
    duration_minutes INTEGER NOT NULL,
    archived_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Assignations (planning type, réutilisable)
-- ON DELETE RESTRICT sur task_id et child_id : impossible de
-- supprimer en dur une tâche ou un enfant tant qu'une assignation
-- existe. La suppression UI passe par un soft-delete (archivage).
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE RESTRICT,
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE RESTRICT,
    moment_id UUID NOT NULL REFERENCES moments(id) ON DELETE RESTRICT,
    day_of_week INTEGER NOT NULL,  -- 0=lundi, 6=dimanche
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Instances de tâches (occurrences concrètes par semaine)
--
-- Snapshot : à la création d'une instance, on recopie ici les champs
-- d'affichage de l'assignation source (task, child, moment, jour).
-- L'instance devient autonome — l'historique reste lisible même si
-- l'assignation, la tâche ou l'enfant sont ensuite supprimés/archivés.
--
-- assignment_id est nullable avec ON DELETE SET NULL : on peut
-- supprimer une assignation sans casser l'historique des instances.
CREATE TABLE task_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID REFERENCES assignments(id) ON DELETE SET NULL,
    week_start DATE NOT NULL,  -- toujours un lundi
    instance_date DATE NOT NULL,  -- date concrète = week_start + day_of_week
    state VARCHAR(20) NOT NULL DEFAULT 'assigned',
    -- assigned|declared|done|undone|unknown
    declared_at TIMESTAMPTZ,
    state_changed_at TIMESTAMPTZ,
    -- Snapshot figé à la création de l'instance
    task_label VARCHAR(200) NOT NULL,
    task_emoji VARCHAR(10),
    task_duration_minutes INTEGER NOT NULL,
    child_first_name VARCHAR(100) NOT NULL,
    child_color VARCHAR(20) NOT NULL,
    moment_label VARCHAR(20) NOT NULL,  -- matin|midi|soir
    day_of_week INTEGER NOT NULL,       -- 0=lundi, 6=dimanche
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(assignment_id, week_start)
);

-- Validations parent sur une instance
-- Ne contient QUE des actions parent explicites.
-- Les transitions automatiques (job 30h) mettent directement à jour
-- task_instances.state sans créer de ligne ici.
-- Présence d'une ligne ⇒ action parent ; absence ⇒ état atteint
-- automatiquement (auto-validation après 30h, ou bascule en
-- "non renseignée").
CREATE TABLE validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID NOT NULL UNIQUE REFERENCES task_instances(id),
    parent_id UUID NOT NULL REFERENCES parents(id),
    target_state VARCHAR(20) NOT NULL,  -- done|undone
    reason VARCHAR(20),  -- refused|other (si undone)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Configuration du kiosque (singleton)
CREATE TABLE kiosk_config (
    id INTEGER PRIMARY KEY DEFAULT 1,  -- toujours 1
    weather_city VARCHAR(100) DEFAULT 'Paris',
    quote_text TEXT,
    quote_author VARCHAR(200),
    quote_work VARCHAR(200),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)
);
```

### Données initiales (seed)
```sql
-- Moments par défaut
INSERT INTO moments (label, start_time, end_time, sort_order) VALUES
    ('matin', '07:00', '12:00', 0),
    ('midi',  '12:00', '14:00', 1),
    ('soir',  '18:00', '21:00', 2);

-- Config kiosque vide
INSERT INTO kiosk_config (id) VALUES (1);
```

---

## 5. Routes API FastAPI

### Auth — `/api/v1/auth`
```
POST   /login              # login parent → JWT cookie httpOnly
POST   /logout             # supprime le cookie
GET    /me                 # infos du parent connecté
POST   /verify-pin         # vérifie un PIN (enfant ou parent) → profil reconnu
```

### Enfants — `/api/v1/children`
```
GET    /                   # liste les enfants non archivés
POST   /                   # créer un enfant
PUT    /{id}               # modifier un enfant
DELETE /{id}               # archive l'enfant (soft-delete via archived_at)
                             ses assignations sont supprimées.
                             Les instances historiques restent intactes
                             grâce au snapshot.
```

### Catalogue — `/api/v1/tasks`
```
GET    /                   # liste les tâches non archivées
POST   /                   # créer une tâche
PUT    /{id}               # modifier une tâche
DELETE /{id}               # archive la tâche (soft-delete via archived_at)
                             ses assignations sont supprimées.
                             Les instances historiques restent intactes
                             grâce au snapshot.
```

### Moments — `/api/v1/moments`
```
GET    /                   # liste les 3 moments avec leurs créneaux
PUT    /{id}               # modifier le créneau d'un moment
```

### Planning — `/api/v1/assignments`
```
GET    /                   # liste toutes les assignations (planning type)
POST   /                   # créer une assignation
                             matérialise l'instance correspondante si la
                             semaine en cours (ou S+1) est déjà matérialisée.
PUT    /{id}               # modifier une assignation
                             met à jour le snapshot de l'instance de la
                             semaine en cours si état = 'assigned' ; sinon
                             retourne 409 Conflict (réinitialisation requise).
                             Les instances de S+1 et passées ne sont jamais
                             modifiées.
DELETE /{id}               # supprimer une assignation
                             supprime l'instance de la semaine en cours si
                             état = 'assigned' ; sinon 409 Conflict.
                             Les instances de S+1 et passées conservent
                             leur snapshot (assignment_id devient NULL).
POST   /clone              # cloner une semaine vers une autre
         body: { source_week: "2025-05-05", target_week: "2025-05-12", overwrite: bool }
```

### Instances — `/api/v1/instances`
```
GET    /week/{week_start}  # toutes les instances d'une semaine (YYYY-MM-DD)
                             génération lazy plafonnée à S+1.
                             Recalcule aussi les bascules 30h éligibles
                             à chaque appel (pas de job en arrière-plan).
                             Voir docs/06-data-model.md.

POST   /{id}/declare       # enfant déclare faite (via PIN — auth kiosque)
         body: { "pin": "1234" }
         - Vérifie que le PIN appartient à l'enfant assigné de l'instance.
         - Si oui : état → 'declared', declared_at = NOW().
         - 401 si PIN inconnu.
         - 403 si PIN parent (utiliser /validate à la place).
         - 403 si PIN d'un autre enfant que l'assigné
           ("Ce n'est pas ton PIN pour cette tâche").
         - 409 si état actuel ≠ 'assigned'.

POST   /{id}/validate      # parent valide (done ou undone + reason)
         body: { "pin": "0001",
                 "target_state": "done" }
              | { "pin": "0001",
                  "target_state": "undone",
                  "reason": "refused" | "other" }
         - Si appelé avec PIN dans le body : vérifie que le PIN appartient
           à un parent (cas kiosque).
         - Si appelé avec cookie JWT admin valide : PIN optionnel
           (parent déjà authentifié dans la vue admin).
         - 401 si ni PIN parent valide ni session admin.
         - Crée une ligne dans `validations`, met à jour state_changed_at.

POST   /{id}/reset         # parent admin réinitialise à 'assigned'
                             supprime la ligne validations associée si
                             elle existe. Réservé à l'admin authentifié
                             (cookie JWT, pas de PIN accepté).
```

### Kiosque — `/api/v1/kiosk`
```
GET    /info               # saint du jour + météo + citation (public)
GET    /week/{week_start}  # planning semaine complet pour affichage kiosque (public)
```

### Configuration — `/api/v1/config`
```
GET    /                   # récupère la config kiosque
PUT    /weather            # met à jour la ville météo
PUT    /quote              # met à jour la citation du moment
```

---

## 6. Structure des issues GitHub

Chaque issue suit ce format pour que Claude Code puisse l'implémenter
de manière autonome :

```markdown
## Contexte
[Référence au doc de conception concerné — ex: docs/09a-specs-composants-atomiques.md#TaskCard]

## Objectif
[Ce que cette issue accomplit en une phrase]

## Critères d'acceptance
- [ ] Critère 1 précis et testable
- [ ] Critère 2
- [ ] Tests unitaires couvrant les cas nominaux

## Notes d'implémentation
[Contraintes techniques, dépendances sur d'autres issues]
```

Les issues sont organisées en **milestones** correspondant aux cycles :
- `Cycle 1 — MVP` pour toutes les issues du premier cycle
- `Cycle 2` pour les issues futures

---

## 7. Ordre d'implémentation — Cycle 1

Les issues doivent être implémentées dans cet ordre pour éviter
les dépendances bloquantes.

### Phase 1 — Fondations (backend)
1. Setup projet FastAPI + SQLAlchemy + Alembic
2. Migrations PostgreSQL (toutes les tables)
3. Seed données initiales (moments, kiosk_config)
4. Auth parent : login/logout/me avec JWT cookie httpOnly
5. CRUD enfants
6. CRUD catalogue de tâches
7. CRUD moments (mise à jour créneaux)
8. CRUD assignations + clone de semaine
9. Génération des instances de tâches pour une semaine
   (avec snapshot des champs d'affichage : task_label, task_emoji,
    task_duration_minutes, child_first_name, child_color,
    moment_label, day_of_week, instance_date)
10. Endpoint declare + validate + reset (instances)
11. Bascule lazy des états à 30h dans GET /instances/week
    (calcul à chaque chargement, pas de job)
12. Endpoint kiosque public (info + week)
13. Intégration météo OpenWeatherMap
14. Saint du jour (calcul côté serveur)
15. CRUD config kiosque (ville, citation)

### Phase 2 — Fondations (frontend)
16. Setup projet React + Vite + Tailwind + shadcn/ui + React Router
17. Configuration Tailwind — palette couleurs enfants
18. Types TypeScript partagés (TaskState, Child, Task, etc.)
19. Hook `useWeekPlanning` — fetch + cache TanStack Query
20. Hook `useKioskInfo` — météo + saint + citation

### Phase 3 — Composants atomiques
21. `ChildBadge`
22. `StateIcon`
23. `TaskCard` (modes kiosk et admin)
24. `PinPad` (overlay complet avec flux de saisie)

### Phase 4 — Composants composites
25. `MomentBlock`
26. `DayColumn`
27. `WeekGrid`
28. `KioskBanner`
29. `ChargeBar`
30. `AdminSidebar`

### Phase 5 — Vues
31. `KioskView` — vue publique complète
32. Login parent
33. `PlanningView` — vue admin planning
34. `ChildrenView` — CRUD enfants
35. `CatalogView` — CRUD catalogue
36. `SettingsView` — configuration kiosque

### Phase 6 — CI/CD et déploiement
37. GitHub Actions — CI (tests + lint sur PR)
38. GitHub Actions — build Docker + push ghcr.io sur merge main
39. Dockerfiles frontend et backend
40. docker-compose.yml développement local
41. Chart Helm pour K3S

---

## 8. GitHub Actions

### CI — `.github/workflows/ci.yml`
Déclenché sur chaque pull request vers `main` :
- Backend : `make lint` (mypy + black) + `make test` (pytest)
- Frontend : `pnpm lint` + `pnpm build` (vérifie que ça compile)

### Build — `.github/workflows/build.yml`
Déclenché sur chaque merge dans `main` :
- Build image Docker frontend → push `ghcr.io/<user>/fcp-frontend:latest`
- Build image Docker backend → push `ghcr.io/<user>/fcp-backend:latest`
- Tag additionnel avec le SHA du commit pour rollback facile

---

## 9. Dockerfiles

### Frontend — `frontend/Dockerfile`
Build multi-stage : `node:20-alpine` pour le build Vite,
`nginx:alpine` pour servir les fichiers statiques.
Le frontend est une SPA statique servie par nginx.

### Backend — `backend/Dockerfile`
Base `python:3.12-slim`.
Lance uvicorn en mode production (sans `--reload`).
Les migrations Alembic sont appliquées au démarrage via un script
`entrypoint.sh` : `alembic upgrade head && uvicorn app.main:app`.

### docker-compose.yml (développement local)
Trois services : `db` (PostgreSQL), `backend`, `frontend`.
Le frontend proxifie `/api` vers le backend (config nginx dev).

---

## 10. Couleurs enfants

Six couleurs assignées automatiquement à la création dans cet ordre,
non modifiables dans le MVP.

| Index | Identifiant | Token Tailwind | Hex approximatif |
|-------|-------------|----------------|-----------------|
| 0 | `green` | `teal-500` | #14b8a6 |
| 1 | `blue` | `blue-500` | #3b82f6 |
| 2 | `amber` | `amber-500` | #f59e0b |
| 3 | `coral` | `orange-500` | #f97316 |
| 4 | `purple` | `violet-500` | #8b5cf6 |
| 5 | `gray` | `gray-400` | #9ca3af |

Si un 7ème enfant est ajouté (hors périmètre MVP), la couleur
revient au début du cycle.

---

## 11. Comment travailler avec Claude Code

### Démarrer une session
```bash
cd family-control-panel
claude
```

Claude Code lit automatiquement le repo, les docs/, et le contexte
courant. Tu peux lui passer des instructions directement :

```
Implémente l'issue #5 (CRUD enfants).
Lis d'abord docs/09c-specs-vues.md#ChildrenView et
docs/06-data-model.md pour le contexte complet.
```

### Bonnes pratiques
- Toujours référencer l'issue et le doc de conception dans
  ta demande à Claude Code — il aura le contexte exact.
- Implémenter une issue à la fois, dans l'ordre défini
  en section 7 — les dépendances sont importantes.
- Faire une PR par issue, merger avant de passer à la suivante.
- Si Claude Code pose une question d'architecture non couverte
  par les docs, noter la décision prise et committer dans docs/.

### Commandes gh CLI utiles
```bash
# Créer une issue
gh issue create --title "Setup FastAPI + SQLAlchemy" --milestone "Cycle 1 MVP"

# Lister les issues ouvertes
gh issue list --milestone "Cycle 1 MVP"

# Voir une issue
gh issue view 5

# Créer une PR depuis la branche courante
gh pr create --title "feat: CRUD enfants" --body "Closes #5"

# Merger une PR
gh pr merge 3 --squash
```
