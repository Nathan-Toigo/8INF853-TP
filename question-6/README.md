# 8INF853 – TP1 Question 6
# Patron Publisher-Subscriber via Programmation Par Aspect (AspectJ) + Docker

---

## 🚀 Lancer et tester le projet

### Prérequis
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et en cours d'exécution

### 1. Cloner / se placer dans le répertoire du projet
```bash
cd 8INF853-TP1-Q6-1
```

---

### ▶️ Méthode recommandée — Docker Compose

#### Construire l'image
```bash
docker compose build
```

#### Exécuter la simulation
```bash
docker compose run --rm app
```

#### Build + exécution en une seule commande
```bash
docker compose up
```

> ⏱️ Le premier build prend ~2 minutes (téléchargement des dépendances Maven). Les builds suivants utilisent le cache Docker et sont quasi-instantanés.

---

### 🔧 Méthode alternative — Docker seul

#### Construire l'image
```bash
docker build -t tp-aspectj .
```
Cette commande :
- Télécharge l'image `maven:3.9.6-eclipse-temurin-17` (stage build)
- Compile le code Java avec le tissage AspectJ (weaving à la compilation)
- Produit un fat JAR avec toutes les dépendances
- Crée une image légère `eclipse-temurin:17-jre-alpine` (stage runtime)

#### Exécuter la simulation
```bash
docker run --rm tp-aspectj
```

---

**Sortie attendue :**
```
╔══════════════════════════════════════════════════╗
║   TP Architecture Logicielle - Question 6        ║
║   Publisher-Subscriber via AOP (AspectJ)         ║
║   Simulation : Feu de Circulation                ║
╚══════════════════════════════════════════════════╝
...
>>> Cycle 1 : Passage au VERT
[TrafficLight] 'Carrefour-Principal' change de couleur : RED -> GREEN
[Aspect] Interception de changeColor() — Notification de 4 observateur(s)...
[Car 'ABC-123'] Réaction : 🟢 Feu VERT → Je peux avancer !
[Pedestrian 'Alice'] Réaction : 🟢 Feu VERT → Je dois attendre sur le trottoir.
...
╔══════════════════════════════════════════════════╗
║   SIMULATION TERMINÉE AVEC SUCCÈS                ║
╚══════════════════════════════════════════════════╝
```

### Commandes utiles
```bash
# Voir l'image créée
docker images | grep tp-aspectj-pubsub

# Voir les conteneurs ayant tourné
docker ps -a

# Reconstruire from scratch (sans cache)
docker compose build --no-cache

# Supprimer les ressources Compose (conteneurs + image)
docker compose down --rmi local
```

---

## 1. Description de l'architecture

### Vue d'ensemble

Cette implémentation réalise le patron **Publisher-Subscriber (Observer)** en utilisant la
**Programmation Orientée Aspect (AOP)** avec AspectJ. L'objectif central est d'éliminer tout
couplage entre le Publisher et ses Subscribers, ce que l'AOP accomplit de manière élégante.

### Les composants

| Composant | Rôle | Couplage |
|---|---|---|
| `TrafficLight` | Publisher – émet des événements (changements de couleur) | Aucun vers les Subscribers |
| `TrafficObserver` | Interface des Subscribers – contrat de notification | Interface neutre |
| `Car` | Subscriber #1 – réagit aux feux selon la logique d'une voiture | Aucun vers le Publisher |
| `Pedestrian` | Subscriber #2 – réagit aux feux selon la logique d'un piéton | Aucun vers le Publisher |
| `TrafficLightAspect` | **Médiateur AOP** – intercepte, enregistre, notifie | Connaît les deux parties |

### Structure du projet

```
8INF853-TP1-Q6-1/
├── pom.xml                              ← Maven + AspectJ plugin + assembly plugin
├── Dockerfile                           ← Multi-stage (build JDK 17 + runtime JRE 17)
├── .dockerignore
└── src/main/java/com/tp/q6/
    ├── Main.java                        ← Simulation complète en 6 étapes
    ├── TrafficLight.java                ← Publisher (ZÉRO référence aux observers)
    ├── TrafficObserver.java             ← Interface Subscriber
    ├── Car.java                         ← Subscriber #1
    ├── Pedestrian.java                  ← Subscriber #2
    └── aspect/
        └── TrafficLightAspect.java      ← @Aspect : pointcut + advice + registre
```

### Fonctionnement du mécanisme AOP

```
[Main]
  │── crée ──► TrafficLight (Publisher)
  │── crée ──► Car, Pedestrian (Subscribers)
  │── enregistre dans ──► TrafficLightAspect
  │
  └── appelle ──► trafficLight.changeColor("GREEN")
                         │
                         ▼
               [POINT DE JONCTION AspectJ]
               TrafficLight.changeColor() s'exécute
                         │
                         ▼ @After (Advice)
               TrafficLightAspect.afterColorChange()
                  │── notifie ──► car1.onColorChange(...)
                  │── notifie ──► car2.onColorChange(...)
                  │── notifie ──► pedestrian1.onColorChange(...)
                  └── notifie ──► pedestrian2.onColorChange(...)
```

### Comment l'Aspect centralise le protocole d'interaction

L'`TrafficLightAspect` joue le rôle de **médiateur transparent** grâce à trois mécanismes AspectJ :

**1. Le Pointcut (Point de Coupure)**
```java
@Pointcut("execution(* com.tp.q6.TrafficLight.changeColor(String))
           && args(newColor) && this(trafficLight)")
public void colorChangePointcut(String newColor, TrafficLight trafficLight) { }
```
Le pointcut définit *où* AspectJ doit intervenir. Il capture toute exécution de `changeColor(String)`
sur `TrafficLight`, en liant automatiquement l'argument et l'instance cible pour l'Advice.

**2. L'Advice @After (Greffon)**
```java
@After("colorChangePointcut(newColor, trafficLight)")
public void afterColorChange(String newColor, TrafficLight trafficLight) { ... }
```
L'Advice s'exécute *après* la méthode originale. L'Aspect itère sur la liste des observateurs
enregistrés pour ce feu et appelle `onColorChange()` sur chacun d'eux.

**3. Le Tissage (Weaving) à la compilation**
Le plugin `aspectj-maven-plugin` instrumente le bytecode Java à la compilation. Le JAR produit
contient déjà le code tissé : aucune configuration runtime n'est nécessaire.

### Preuve de l'absence de couplage dans `TrafficLight.java`

```java
public class TrafficLight {
    private String color;
    private final String id;

    // ✅ Méthode PURE - aucune référence aux Observers, aucun import Observer
    public void changeColor(String newColor) {
        this.color = newColor;  // Logique métier uniquement
    }
}
```

---

## 2. Forces et Faiblesses

### ✅ Forces

#### 2.1 Séparation radicale des préoccupations (SRP / Separation of Concerns)
Le patron Observer traditionnel oblige le Publisher à maintenir une liste de Subscribers.
Avec l'AOP, cette responsabilité est **entièrement extraite** dans un Aspect :
- `TrafficLight` ne contient que sa logique métier pure
- Facilite les tests unitaires du Publisher de façon isolée
- Le Publisher est **réutilisable** dans n'importe quel contexte

#### 2.2 Couplage nul entre Publisher et Subscribers
`TrafficLight` n'importe **rien** lié aux Subscribers. On peut ajouter un nouveau type de
Subscriber (ex: `EmergencyVehicle`) sans modifier une seule ligne de `TrafficLight`.

#### 2.3 Extension non-invasive du comportement
Si `TrafficLight` était une classe d'une bibliothèque tierce, on pourrait lui greffer le
mécanisme de notification en créant simplement un Aspect, **sans toucher à la bibliothèque**.

#### 2.4 Centralisation du protocole d'interaction
Toute la logique du protocole (qui notifie qui, quand, comment) réside dans un seul fichier.
Si le protocole change (ex: notification asynchrone, filtrage conditionnel), on modifie
**uniquement l'Aspect**, pas le Publisher ni les Subscribers.

#### 2.5 Abonnement / désabonnement dynamique
L'Aspect expose `register()` et `unregister()` pour gérer les abonnements à runtime,
comme démontré dans la simulation (désabonnement de `Car ABC-123` avant le Cycle 4).

---

### ❌ Faiblesses

#### 2.6 Complexité et courbe d'apprentissage
L'AOP introduit un paradigme supplémentaire. Un développeur non familier avec AspectJ
doit comprendre Pointcut, Advice, Join Point et Weaving. Le flot d'exécution devient
**non linéaire et difficile à tracer** dans un débogueur classique.

#### 2.7 Magie implicite — violation du principe de moindre surprise
Lorsqu'un développeur lit `trafficLight.changeColor("GREEN")`, rien n'indique qu'une
notification sera déclenchée. Ce comportement **invisible** peut créer de la confusion
et des bugs difficiles à diagnostiquer lors de la maintenance.

#### 2.8 Dépendance à l'outillage AspectJ
Le projet requiert `aspectj-maven-plugin` et une JDK compatible (≥ 17 pour AspectJ 1.9.21).
Cela ajoute une dépendance de build non triviale et peut créer des problèmes de compatibilité
lors de mises à jour.

#### 2.9 Couplage inversé : l'Aspect connaît tout
On élimine le couplage `Publisher → Subscriber` mais on crée `Aspect → Publisher`
ET `Aspect → Subscriber`. Toute modification du nom de `changeColor()` casse silencieusement
le pointcut **sans erreur de compilation** (le greffon ne s'exécutera plus).

#### 2.10 Difficile à déboguer et à tester
Les Aspects ne sont pas visibles dans le code source. Sans outillage adapté (plugin AJDT
pour Eclipse, support AspectJ IntelliJ), la navigation dans le code est malaisée.