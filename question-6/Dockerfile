# =============================================================================
# Dockerfile Multi-Stage pour TP AspectJ Publisher-Subscriber
#
# Stage 1 (build)  : Compilation Maven + tissage AspectJ (weaving)
# Stage 2 (runtime): Exécution légère avec JRE minimal
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1 : BUILD
# Utilise une image Maven avec JDK 11 pour compiler et tisser les aspects
# -----------------------------------------------------------------------------
FROM maven:3.9.6-eclipse-temurin-17 AS build

# Métadonnées
LABEL stage="build"
LABEL description="Compilation Maven + AspectJ weaving"

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier d'abord le pom.xml seul pour profiter du cache Docker sur les dépendances.
# Si le code change mais pas le pom.xml, les dépendances ne seront pas re-téléchargées.
COPY pom.xml .

# Pré-télécharger toutes les dépendances Maven (optimisation du cache Docker)
RUN mvn dependency:go-offline -B

# Copier le code source
COPY src ./src

# Compiler et packager l'application avec le tissage d'aspects AspectJ
# -B : mode batch (pas de sortie interactive)
# -DskipTests : pas de tests unitaires pour le TP
# Le résultat est un fat JAR avec toutes les dépendances incluses
RUN mvn clean package -B -DskipTests

# -----------------------------------------------------------------------------
# STAGE 2 : RUNTIME
# Image légère avec uniquement le JRE (pas de JDK/Maven) pour la production
# -----------------------------------------------------------------------------
FROM eclipse-temurin:17-jre-alpine AS runtime

# Métadonnées de l'image finale
LABEL maintainer="TP Architecture Logicielle"
LABEL description="Publisher-Subscriber via AspectJ AOP - Simulation feu de circulation"
LABEL version="1.0"

# Répertoire de travail
WORKDIR /app

# Copier uniquement le JAR compilé depuis le stage build
# Le stage runtime n'a pas accès à Maven ni aux sources
COPY --from=build /app/target/tp-aspectj-pubsub-1.0-SNAPSHOT.jar ./app.jar

# Lancer l'application Java
# -jar : exécute le JAR exécutable
# ENTRYPOINT (vs CMD) : rend la commande non-overridable par défaut
ENTRYPOINT ["java", "-jar", "app.jar"]
