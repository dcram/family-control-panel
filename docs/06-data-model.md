# Modèle d'objets — Family Control Panel
_Version 0.1 — mai 2025 — Cycle 1 MVP_

## Entités

**Parent**
- Identifiants (login + mot de passe)
- 2 par foyer, droits symétriques
- Possède un PIN kiosque (voir entité PIN kiosque)

**Enfant**
- Prénom, date de naissance, âge calculé automatiquement
- Possède un PIN kiosque (voir entité PIN kiosque)
- Archivable : un enfant archivé disparaît des listes éditables
  et des sélecteurs mais reste référencé dans les instances
  historiques via le snapshot (voir InstanceTâche).

**PIN kiosque**
- 4 chiffres
- Partagé dans une table dédiée garantissant l'unicité globale
  entre parents et enfants
- Référence polymorphe vers un parent ou un enfant
- Un parent ou enfant a au plus un PIN actif

## Unicité des PINs

Les PINs des parents et des enfants partagent le même espace
(0000–9999) avec **unicité globale** garantie par la table dédiée
`kiosk_pins` (voir schéma SQL dans `00-getting-started.md`).

`kiosk_pins.pin` est PRIMARY KEY → impossible d'avoir deux PINs
identiques quel que soit le titulaire. La résolution d'un PIN
saisi au kiosque consiste à lire `holder_type` et `holder_id`
dans cette table puis joindre vers la table correspondante.

Cohérence applicative à maintenir côté backend :
- À la création d'un parent ou d'un enfant : insérer aussi
  une ligne dans `kiosk_pins`.
- À la modification du PIN : mettre à jour `kiosk_pins.pin`.
- À l'archivage : la ligne `kiosk_pins` est conservée (le PIN
  reste pris pour ne pas être réattribué par mégarde) ; on
  pourra définir une politique de libération ultérieurement.

**Tâche** (catalogue)
- Libellé
- Âge minimum requis
- Durée estimée (minutes)
- Archivable : une tâche archivée disparaît du catalogue
  et des sélecteurs mais reste référencée dans les instances
  historiques via le snapshot (voir InstanceTâche).

**Moment**
- Label fixe : matin / midi / soir
- Heure de début, heure de fin
- La fin du créneau déclenche le compte à rebours de 30h

**Assignation** (planning type, réutilisable)
- Lie : une tâche + un enfant + un jour de semaine + un moment
- Indépendante de toute semaine calendaire

**InstanceTâche** (occurrence concrète)
- Référence une Assignation (lien optionnel — voir snapshot)
- Semaine calendaire (date du lundi) + date concrète de l'instance
- État : assignée → déclarée faite → réalisée / non réalisée / non renseignée
- **Snapshot** : à la création de l'instance, on recopie ici les champs
  d'affichage figés au moment de la génération :
  libellé et emoji de la tâche, durée estimée, prénom et couleur de
  l'enfant, label du moment, jour de la semaine.
  L'instance devient autonome : l'historique reste lisible même si
  la tâche, l'enfant ou l'assignation source sont ensuite
  supprimés ou archivés.

**Validation**
- Liée à une InstanceTâche (0..1)
- Posée par un parent — trace d'une action humaine explicite
- État cible + motif optionnel (refus d'obtempérer / autre raison)
- Les transitions automatiques (basculement 30h) ne créent pas
  de Validation : elles mettent directement à jour l'état
  de l'InstanceTâche. La présence d'une Validation distingue
  donc une décision parent d'un état atteint automatiquement.

**ConfigKiosque**
- Ville pour la météo
- Citation du moment : texte, auteur, ouvrage (optionnel)

## États d'une InstanceTâche

- **Assignée** — état initial
- **Déclarée faite** — enfant a coché via PIN kiosque
- **Réalisée ✓** — validée par parent, ou 30h sans réaction après déclaration enfant
- **Non réalisée ✗** — invalidée par parent + motif
- **Non renseignée ?** — 30h écoulées sans aucune action

## Règle des 30h

Le délai court à partir de l'heure de fin du créneau horaire
du moment de la journée associé à l'assignation.
Toutes les heures sont interprétées en `Europe/Paris` (TZ du foyer).

- InstanceTâche "déclarée faite" + 30h sans action parent → Réalisée ✓
- InstanceTâche "assignée" + 30h sans aucune action → Non renseignée ?

**Calcul lazy au chargement.** Aucun job en arrière-plan : les
transitions sont calculées à chaque `GET /api/v1/instances/week/...`
(et endpoints kiosque équivalents). Le frontend kiosque recharge
les données toutes les 15 minutes — la fraîcheur effective des
états est donc d'au plus 15 min.

Avantage : zéro infra de scheduling, robustesse intrinsèque
en cas de downtime serveur (tout se recalcule au prochain chargement).

## Génération des instances (lazy, plafonnée à S+1)

Les InstanceTâches sont générées **à la demande**, à la première
consultation d'une semaine donnée. La matérialisation est plafonnée
à la semaine en cours + 1 semaine future.

Soit `S` = semaine en cours (lundi calendaire de `now`).

- `GET /api/v1/instances/week/{week_start}` :
  - si `week_start <= S+1` :
    - si **aucune** instance n'existe pour cette `week_start` :
      le backend prend toutes les assignations existantes et crée
      une InstanceTâche par assignation, avec snapshot complet
      (état initial = "assignée"). Puis renvoie la liste.
    - si des instances existent déjà : renvoie l'existant tel quel.
  - si `week_start > S+1` : la consultation au-delà de S+1 n'est pas
    autorisée dans le MVP — la navigation kiosque/admin est plafonnée
    en conséquence.
  - si `week_start < S` (semaine passée) : renvoie ce qui existe en
    base sans rien créer. Une semaine passée jamais consultée
    n'aura pas d'historique exploitable (tradeoff assumé).

- `POST /api/v1/assignments` (création) :
  - le backend détecte les semaines déjà matérialisées et crée
    l'instance manquante pour la nouvelle assignation, avec snapshot.

- `POST /api/v1/assignments/clone` :
  - même logique : si la semaine cible est matérialisée,
    les instances correspondantes sont créées.

## Modification et suppression d'une assignation

Une assignation représente exactement une occurrence par semaine
(1 tâche × 1 enfant × 1 jour × 1 moment). Sa modification ou sa
suppression impacte au plus 1 instance dans la semaine en cours
et 1 instance dans la semaine S+1 si matérialisée.

**Règle d'impact :**

- Instance de la **semaine en cours** :
  - si état = `assigned` → snapshot mis à jour (modif) ou instance
    supprimée (suppression d'assignation).
  - si état ≠ `assigned` (déclarée / réalisée / non réalisée /
    non renseignée) → l'opération est **rejetée** côté API
    (409 Conflict). Le parent admin doit d'abord **réinitialiser**
    l'instance pour la ramener à l'état `assigned`, puis ré-essayer.
- Instance de la **semaine S+1 matérialisée** : aucune modification.
  La décision préparée est figée jusqu'à matérialisation effective.
- Instances **passées** : aucune modification (snapshot figé).

## Réinitialisation d'une instance

Pour défaire une déclaration ou une validation (par exemple parce
qu'on s'est trompé d'enfant et qu'il faut réassigner la tâche),
un parent admin peut **réinitialiser** l'instance :

- Action : `POST /api/v1/instances/{id}/reset`
- Effet : état ramené à `assigned`, ligne dans `validations`
  supprimée si elle existe, `declared_at` et `state_changed_at`
  remis à NULL.
- Réservée au parent admin authentifié (depuis la vue admin),
  pas accessible depuis le kiosque.
- Confirmation UI requise : *"Réinitialiser cette tâche ?
  L'historique de validation sera effacé."*