# PRD — Family Control Panel App
_Version 0.1 — mai 2025_

## Problème

Gérer la répartition des tâches ménagères entre enfants génère une charge 
cognitive quotidienne pour les parents : qui fait quoi aujourd'hui, comment 
réadapter rapidement si un enfant est absent, comment s'assurer que les tâches 
sont équilibrées — pas trop concentrées sur un même jour pour un enfant, et 
équitables entre enfants sur la semaine — et adaptées à l'âge de chacun. 
Cette coordination se fait par oral ou sur des systèmes ad hoc (tableau blanc, 
notes papier) qui ne scalent pas et créent des frictions inutiles.

## Utilisateurs cibles

**Parents admins** (2 par foyer, droits symétriques) : créent les profils 
enfants avec leur date de naissance, définissent le catalogue de tâches avec 
les contraintes d'âge associées, conçoivent et maintiennent le planning 
hebdomadaire, gèrent les exceptions (absences, réassignations). Interface 
dense, utilisée quelques fois par semaine, authentification classique.

**Enfant (8–18 ans)** : consulte le planning partagé sur la vue kiosque, 
coche ses tâches accomplies via un PIN personnel. Pas de session persistante — 
l'action est authentifiée, pas l'utilisateur. Interface aussi simple que 
possible, lisible par un enfant de 8 ans.

## Périmètre MVP (Cycle 1)

- Gestion des profils enfants : création avec date de naissance et PIN, 
  calcul automatique de l'âge.
- Catalogue de tâches : création de tâches avec âge minimum requis 
  et durée estimée (base de l'équilibre de charge).
- Définition d'un planning hebdomadaire fixe : tâches assignées 
  à chaque enfant par jour de la semaine, dans le respect des contraintes d'âge.
- **Vue kiosque partagée** (écran par défaut, sans authentification) : 
  planning de la semaine centré sur aujourd'hui, visible par tous. 
  Un enfant coche une tâche en tapant son PIN — la vue revient 
  immédiatement en mode public.
- Informations contextuelles du jour sur la vue kiosque : météo, 
  saint du jour, citation du jour.
  Un emplacement est réservé dans le bandeau kiosque pour les horaires 
  des prochains bus, prévus dans un cycle ultérieur.
- Interface d'administration parent : accessible après authentification, 
  permet de gérer profils, catalogue et planning.

## Hors périmètre MVP

### Cycle 2
- Gestion des absences et réassignations.

### Cycle 3+
- Horaires des prochains bus sur la vue kiosque (intégration API 
  transport, emplacement déjà réservé dans le bandeau).
- Historique et scoring (gamification).
- Notifications push ou email.
- Extension du kiosque en panneau familial : liste de courses 
  collaborative, pense-bêtes.
- Assistance IA à la planification : génération ou réadaptation automatique 
  du planning par un LLM. Le parent valide, l'IA propose.

## Critères de succès

- Un parent peut configurer le planning complet de la semaine en moins 
  de 10 minutes, sans formation.
- Un enfant peut cocher une tâche accomplie en moins de 10 secondes 
  depuis la vue kiosque.
- La vue kiosque se charge et affiche les infos contextuelles 
  en moins de 3 secondes sur le réseau local.
- Les parents cessent d'utiliser le tableau blanc ou le verbal 
  pour la coordination des tâches dans les 2 semaines suivant le déploiement.

## Contraintes techniques

- Déployé sur cluster K3S personnel — VPS OVH (Docker + Helm).
- Stack front : React 18 + TypeScript + Vite + Tailwind + shadcn/ui.
- Back : à arbitrer entre FastAPI et Node/Express.
- Données : PostgreSQL.
- Pas de dépendance à des services cloud payants pour le cœur fonctionnel.