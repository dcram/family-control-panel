# Family Tasks App — Contexte et roadmap

## 1. Le projet

Webapp de gestion des tâches familiales, déployée sur cluster K3S personnel (VPS OVH).

**Fonctionnalités cibles :**
- Définition des tâches récurrentes et leur répartition entre enfants par jour de la semaine (édition réservée aux parents)
- Gestion des absences ponctuelles avec réassignation des tâches
- Dashboard de consultation pour les enfants : tâches du jour + infos contextuelles (météo, saint du jour, citation du jour ; horaires des prochains bus prévus dans un cycle ultérieur)

**Personas pressentis (à formaliser) :**
- Parent admin : conçoit le planning, gère les exceptions
- Parent consultatif : consulte, valide ponctuellement
- Enfant 8-12 ans : consulte ses tâches, coche les faites

**Postures (au sens Cooper) :**
- Parents : sovereign (interface dense, riche)
- Enfants : transient/kiosk (consultation rapide, interactions minimales)

## 2. Stack technique cible

- **Front** : React 18 + TypeScript + Vite + Tailwind + shadcn/ui
- **Back** : à définir (probablement FastAPI ou Node/Express)
- **Données** : PostgreSQL
- **Infra** : Docker, Helm, K3S sur VPS OVH

## 3. Mon profil d'apprentissage

Ingénieur IA & data, fort en back/data/cloud, limité sur le vocabulaire et la méthodologie UI/UX. 
Objectif : apprendre à concevoir des UI data-management et backoffice avec rigueur, 
pour ensuite être capable de prompter efficacement sur d'autres projets pro 
(annotation de datasets, backoffice data).

## 4. Référentiel méthodologique adopté

- **Shape Up** (Basecamp) : breadboarding, fat marker sketches, cycles, appetite, shaping
- **Goal-Directed Design** (Alan Cooper, About Face) : personas, scenarios, goals, postures
- **Principes Don Norman** (Design of Everyday Things) : affordances, signifiers, feedback, mappings, conceptual models
- **Vocabulaire pro UI** : Refactoring UI (résumés gratuits), NN/g, Anthony Hobday

## 5. Pipeline de conception qu'on va suivre

1. PRD léger (1 page) — qui, quoi, pourquoi, succès
2. Personas (3 profils) avec goals
3. User stories priorisées (MoSCoW)
4. Scénarios "key path" (3 scénarios principaux)
5. User flows en Mermaid pour les scénarios prioritaires
6. Information architecture : modèle d'objets + sitemap
7. Breadboards (Shape Up) pour les écrans clés
8. Fat marker sketches pour les écrans visuellement complexes
9. Specs composants + états (par écran)
10. Implémentation en deux cycles Shape Up :
    - Cycle 1 (MVP) : planning hebdo fixe + dashboard enfant simple
    - Cycle 2 : gestion des absences + intégrations externes

## 6. Décisions déjà prises

- Pas d'Ant Design, pas de mix de libs UI : on part sur shadcn/ui + Tailwind, 
  complété par TanStack Table si besoin de tableaux complexes
- Pas de Bootstrap (décision : trop générique, mal adapté aux UI data-heavy)
- Conception d'abord, code ensuite — pas d'inversion
- Le dashboard enfant peut être très visuel/joyeux, l'admin parent doit être 
  dense et efficace

## 7. Setup de travail

- **Phase actuelle** (conception et apprentissage) : tout dans ce Project Claude.ai
- **Phase suivante** (implémentation) : repo Git + Claude Code dans VS Code, 
  avec deux modes (session conception en R/W sur docs/, session dev en R/W 
  sur src/ et lecture seule sur docs/)
- **Source de vérité finale** : le repo Git, pas le Project Claude.ai

## 8. Première étape concrète

Démarrer par le **PRD léger** (1 page), avec accompagnement professoral : 
Claude m'introduit le format PRD, ce qu'il contient, pourquoi, et on le 
remplit ensemble pour la Family Tasks App.