# Family Control Panel — Guide Claude Code

## Source de vérité

Avant toute implémentation, lis le doc de conception correspondant :

- `00-getting-started.md` (racine) — stack, structure monorepo, schéma BDD, routes API, roadmap d'implémentation, conventions
- `docs/01-prd.md` — périmètre MVP / hors MVP
- `docs/03-user-stories.md` — US numérotées (US-01 à US-24)
- `docs/06-data-model.md` — entités, snapshots, génération lazy, règle 30h, archivage
- `docs/06b-sitemap.md` — arborescence des vues
- `docs/07-breadboards.md` — wireframes textuels
- `docs/09a-specs-composants-atomiques.md` — TaskCard, ChildBadge, StateIcon, PinPad
- `docs/09b-specs-composants-composites.md` — MomentBlock, DayColumn, WeekGrid, KioskBanner, ChargeBar, AdminSidebar
- `docs/09c-specs-vues.md` — KioskView, PlanningView, ChildrenView, CatalogView, SettingsView

Si tu trouves une contradiction entre les docs, signale-la et **demande
avant de coder**. Ne tranche jamais silencieusement.

## Décisions de design à respecter strictement

Ces choix ont été arbitrés volontairement ; ne les remets pas en
question sans validation explicite.

- **Snapshots dans `task_instances`** : à la création d'une instance,
  on recopie `task_label`, `task_emoji`, `task_duration_minutes`,
  `child_first_name`, `child_color`, `moment_label`, `day_of_week`,
  `instance_date`. L'instance est autonome de l'assignation.
- **Génération lazy plafonnée à S+1** : les instances sont créées au
  premier `GET /instances/week/...`. Pas de matérialisation au-delà
  de la semaine courante + 1.
- **Soft-delete (archivage)** : `tasks` et `children` ont `archived_at`.
  L'UI parle d'« Archiver », pas « Supprimer ». DELETE backend = soft.
- **Table partagée `kiosk_pins`** : unicité globale des PINs (parents
  et enfants). Pas de convention de plage, pas de colonne `kiosk_pin`
  sur `parents`/`children`.
- **Bascule 30h calculée lazy** au chargement (pas de cron, pas
  d'APScheduler). Frontend kiosque recharge toutes les 15 min.
- **Validations parent** : la table `validations` ne trace QUE les
  actions humaines explicites. Les bascules auto 30h modifient
  directement `task_instances.state` sans écrire dans `validations`.
- **Modif/suppression d'assignation** : impacte l'instance courante
  uniquement si état = `assigned`. Sinon 409 → réinitialiser d'abord
  via `POST /instances/{id}/reset`.
- **Bouton « Aujourd'hui »** sur le kiosque : présent dans le MVP.
- **TZ unique** : `Europe/Paris` pour tout (TIME des moments, calcul 30h).

## Conventions Python (obligatoires)

- **Typing systématique** : tous les paramètres et la valeur de retour
  de toute fonction/méthode doivent être annotés (`-> None` inclus).
  `mypy --strict` doit passer.
- **Appels par mots-clés** : à l'invocation, passer tous les arguments
  par keyword (`foo(name="x", age=12)`). Exception : fonctions à un
  seul paramètre.
- **Pydantic v2** pour tous les modèles métier (schémas API, configs).
- **Pydantic-settings** pour la configuration via variables d'env.
- Ne pas utiliser `Any` ni `# type: ignore` sans justification commentée.

## Conventions Frontend

- TypeScript strict (`tsconfig.json` avec `"strict": true`).
- Composants fonctionnels uniquement, hooks pour l'état.
- `shadcn/ui` pour les primitives UI ; pas d'autre lib de composants.
- TanStack Query pour tout le data-fetching (pas de `fetch` brut dans
  les composants).
- Les composants atomiques/composites ne connaissent pas l'API —
  uniquement des props et des callbacks. La logique data vit dans les
  vues (`KioskView`, `PlanningView`, etc.).

## Commandes

```bash
make install-dev   # installe back + front
make lint          # mypy + black sur le backend
make format        # applique black
make test          # pytest
```

Backend dev : `cd backend && uv run uvicorn app.main:app --reload`
Frontend dev : `cd frontend && pnpm dev`

## Workflow Git

- 1 issue = 1 branche = 1 PR = 1 squash-merge.
- Branches nommées `feat/<short-desc>`, `fix/<short-desc>`,
  `chore/<short-desc>`, `docs/<short-desc>`.
- Messages de commit : impératif court, en français OK.
- PR : titre clair + lien vers l'issue (`Closes #N`).
- Pas de merge dans `main` sans CI verte (`make lint` + `make test`
  côté back, `pnpm lint` + `pnpm build` côté front).

## Couleurs enfants (référence rapide)

`green→teal-500`, `blue→blue-500`, `amber→amber-500`,
`coral→orange-500`, `purple→violet-500`, `gray→gray-400`.
Source de vérité : `00-getting-started.md` §10.

## Si tu hésites

Préfère poser une question plutôt qu'inventer. Les specs sont
détaillées : si une décision n'y figure pas, c'est probablement
qu'elle n'a pas été arbitrée — demande.
