# User stories — Family Control Panel App
_Version 0.2 — mai 2025 — Cycle 1 MVP_

## Gestion des profils enfants

US-01 | Must
En tant que parent admin, je veux créer un profil enfant avec son prénom 
et sa date de naissance, afin que le système calcule automatiquement 
son âge et filtre les tâches qui lui sont assignables.

US-02 | Must
En tant que parent admin, je veux définir un PIN à 4 chiffres par enfant, 
afin qu'il puisse déclarer ses tâches accomplies sur le kiosque 
sans session persistante.

US-03 | Should
En tant que parent admin, je veux modifier ou supprimer un profil enfant, 
afin de maintenir la liste à jour si la situation familiale évolue.

---

## Catalogue de tâches

US-04 | Must
En tant que parent admin, je veux créer une tâche avec un libellé, 
un emoji optionnel, un âge minimum requis et une durée estimée, 
afin de disposer d'un catalogue visuellement identifiable 
pour construire le planning.

US-05 | Must
En tant que parent admin, je veux modifier ou supprimer une tâche 
du catalogue, afin de faire évoluer le référentiel sans recréer 
le planning depuis zéro.

---

## Configuration des moments de la journée

US-18 | Must
En tant que parent admin, je veux définir un créneau horaire 
(heure de début, heure de fin) pour chaque moment de la journée 
(matin, midi, soir), afin que le système sache à quel moment 
déclencher le compte à rebours de 30h pour chaque tâche.

---

## Planning hebdomadaire

US-06 | Must
En tant que parent admin, je veux assigner une tâche à un enfant 
pour un jour de la semaine et un moment de la journée donnés 
(matin, midi, soir), afin de construire un planning hebdomadaire 
précis qui reflète l'organisation réelle du foyer.

US-07 | Must
En tant que parent admin, je veux être averti si j'assigne une tâche 
à un enfant trop jeune pour la réaliser, afin d'éviter une erreur 
sans pour autant être bloqué dans ma saisie.

US-08 | Should
En tant que parent admin, je veux visualiser la charge totale par enfant 
sur la semaine (en minutes), afin de détecter les déséquilibres 
sans calcul mental.

US-09 | Could
En tant que parent admin, je veux copier le planning d'une semaine 
existante vers une semaine future, afin de ne pas tout ressaisir 
quand la semaine type ne change pas.

---

## Vue kiosque

US-10 | Must
En tant que membre du foyer (parent ou enfant), je veux voir en un coup 
d'œil qui fait quoi cette semaine, centré sur aujourd'hui et groupé 
par moment de la journée, sans avoir à m'authentifier, afin de répondre 
à la question "qui fait quoi ce soir ?" sans friction.

US-11 | Must
En tant qu'enfant, je veux déclarer une tâche accomplie en saisissant 
mon PIN, afin que mon action soit enregistrée comme "déclarée faite" 
sous mon identité et que la vue revienne immédiatement en mode public.

US-12 | Must
En tant que membre du foyer, je veux voir les informations contextuelles 
du jour sur la vue kiosque (météo, saint du jour, citation du moment), 
afin d'avoir en un seul endroit tout ce dont j'ai besoin le matin.

US-13 | Should
En tant qu'enfant, je veux naviguer vers les jours précédents et à venir 
sur la vue kiosque, afin de vérifier ce que j'ai fait et anticiper 
ce qui m'attend.

---

## Validation parent

US-19 | Must
En tant que parent admin, je veux valider ou invalider une tâche 
déclarée faite par un enfant, via mon PIN sur le kiosque ou depuis 
l'interface d'administration, afin de confirmer que la tâche 
a bien été réalisée.

US-20 | Must
En tant que parent admin, je veux marquer une tâche comme non réalisée 
en précisant la raison (refus d'obtempérer ou autre raison), afin 
de garder une trace honnête de ce qui s'est passé.

US-21 | Must
En tant que système, je veux faire basculer automatiquement une tâche 
"déclarée faite" sans réaction parentale vers l'état "réalisée" 
au bout de 30h après la fin du créneau horaire du moment de la journée, 
afin de bénéficier du doute en faveur de l'enfant.

US-22 | Must
En tant que système, je veux faire basculer automatiquement une tâche 
sans aucune action (ni déclaration enfant ni action parent) vers l'état 
"non renseignée" au bout de 30h après la fin du créneau horaire 
du moment de la journée, afin de clore proprement les tâches oubliées.

US-24 | Must
En tant que parent admin, je veux pouvoir réinitialiser une instance 
de tâche déjà déclarée ou validée pour la ramener à l'état "assignée", 
afin de corriger une erreur d'assignation ou défaire une validation 
posée par mégarde — c'est aussi le pré-requis pour modifier ou 
supprimer une assignation dont l'instance de la semaine en cours 
n'est plus à l'état initial.

---

## Authentification parent

US-14 | Must
En tant que parent admin, je veux m'authentifier avec un identifiant 
et un mot de passe, afin d'accéder à l'interface d'administration 
sans exposer ces fonctions sur le kiosque public.

US-15 | Must
En tant que parent admin, je veux que mes modifications soient 
immédiatement visibles par l'autre parent connecté, afin d'éviter 
tout conflit de version entre les deux comptes.

US-23 | Must
En tant que parent admin, je veux disposer d'un PIN à 4 chiffres 
distinct de celui des enfants, afin de valider ou invalider des tâches 
depuis le kiosque sans m'authentifier complètement.

---

## Citation du moment

US-16 | Should
En tant que parent admin, je veux saisir une citation du moment 
(texte, auteur, ouvrage optionnel), afin qu'elle s'affiche sur 
le kiosque jusqu'à ce que je la remplace.

---

## Configuration du kiosque

US-17 | Must
En tant que parent admin, je veux configurer la ville utilisée 
pour la météo du kiosque, afin que les informations affichées 
correspondent à ma localisation réelle.

---

## Orientations futures

### Cycle 2
US-F01 | Won't — cycle 2
En tant que parent admin, je veux disposer d'une vue globale 
et synthétique de l'état des tâches sur la semaine, afin d'identifier 
d'un coup d'œil les tâches validées, déclarées, non réalisées 
et non renseignées pour tous les enfants.

### Cycle 3+
US-F02 | Won't — cycle 3+
En tant que parent admin, je veux ajouter une tâche ad-hoc 
à un enfant pour un jour donné, en dehors du catalogue de tâches, 
afin de gérer les imprévus sans modifier le planning type.