package com.tp.q6;

import com.tp.q6.aspect.TrafficLightAspect;
import org.aspectj.lang.Aspects;

/**
 * Point d'entrée de l'application - Simulation du patron Publisher-Subscriber via AOP.
 *
 * Cette classe démontre :
 * 1. La création des objets Publisher et Subscribers
 * 2. L'enregistrement des Subscribers dans l'Aspect (pas dans le Publisher !)
 * 3. La simulation de changements d'état du feu de circulation
 * 4. La notification automatique et transparente via l'Aspect
 *
 * TrafficLight ne sait PAS qu'il y a des observateurs.
 * Car et Pedestrian ne savent PAS qu'il y a un feu de circulation.
 * L'Aspect est le seul à connaître les deux parties.
 */
public class Main {

    public static void main(String[] args) throws InterruptedException {

        // =====================================================================
        // ENTÊTE DE LA SIMULATION
        // =====================================================================
        printHeader();

        // =====================================================================
        // ÉTAPE 1 : Récupération de l'instance unique de l'Aspect (Singleton)
        //           Aspects.aspectOf() est fourni par AspectJ pour accéder
        //           à l'instance gérée par le framework.
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 1 : Initialisation de l'Aspect");
        System.out.println("══════════════════════════════════════════════════");

        TrafficLightAspect aspect = Aspects.aspectOf(TrafficLightAspect.class);
        System.out.println("[Main] Aspect TrafficLightAspect obtenu : " + aspect);

        // =====================================================================
        // ÉTAPE 2 : Création du Publisher (TrafficLight)
        //           Note : aucune référence aux Observers dans TrafficLight !
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 2 : Création du Publisher (TrafficLight)");
        System.out.println("══════════════════════════════════════════════════");

        TrafficLight mainCrossroadLight = new TrafficLight("Carrefour-Principal", "RED");

        // =====================================================================
        // ÉTAPE 3 : Création des Subscribers
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 3 : Création des Subscribers");
        System.out.println("══════════════════════════════════════════════════");

        Car car1 = new Car("ABC-123");
        Car car2 = new Car("XYZ-789");
        Pedestrian pedestrian1 = new Pedestrian("Alice");
        Pedestrian pedestrian2 = new Pedestrian("Bob");

        // =====================================================================
        // ÉTAPE 4 : Enregistrement des Subscribers dans l'ASPECT (pas dans TrafficLight !)
        //           C'est ici que le découplage est visible : on parle à l'Aspect,
        //           jamais au Publisher.
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 4 : Enregistrement des Subscribers dans l'Aspect");
        System.out.println("══════════════════════════════════════════════════");

        aspect.register(mainCrossroadLight, car1);
        aspect.register(mainCrossroadLight, car2);
        aspect.register(mainCrossroadLight, pedestrian1);
        aspect.register(mainCrossroadLight, pedestrian2);

        System.out.println("[Main] Nombre d'observateurs enregistrés : "
                + aspect.getObservers(mainCrossroadLight).size());

        // =====================================================================
        // ÉTAPE 5 : SIMULATION - Changements d'état du feu
        //           Chaque appel à changeColor() est automatiquement intercepté
        //           par l'Aspect qui notifie tous les Subscribers.
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 5 : SIMULATION DES CHANGEMENTS D'ÉTAT");
        System.out.println("══════════════════════════════════════════════════");

        // Cycle 1 : RED → GREEN
        System.out.println("\n>>> Cycle 1 : Passage au VERT");
        System.out.println("----------------------------------------------------");
        mainCrossroadLight.changeColor("GREEN");
        Thread.sleep(500); // Simulation d'un délai réaliste

        // Cycle 2 : GREEN → ORANGE
        System.out.println("\n>>> Cycle 2 : Passage à l'ORANGE");
        System.out.println("----------------------------------------------------");
        mainCrossroadLight.changeColor("ORANGE");
        Thread.sleep(500);

        // Cycle 3 : ORANGE → RED
        System.out.println("\n>>> Cycle 3 : Retour au ROUGE");
        System.out.println("----------------------------------------------------");
        mainCrossroadLight.changeColor("RED");
        Thread.sleep(500);

        // =====================================================================
        // ÉTAPE 6 : Démonstration du désabonnement dynamique
        // =====================================================================
        System.out.println("\n══════════════════════════════════════════════════");
        System.out.println("  ÉTAPE 6 : Désabonnement dynamique de Car ABC-123");
        System.out.println("══════════════════════════════════════════════════");

        aspect.unregister(mainCrossroadLight, car1);
        System.out.println("[Main] Observateurs restants : "
                + aspect.getObservers(mainCrossroadLight).size());

        System.out.println("\n>>> Cycle 4 : Nouveau passage au VERT (sans Car ABC-123)");
        System.out.println("----------------------------------------------------");
        mainCrossroadLight.changeColor("GREEN");

        // =====================================================================
        // CONCLUSION
        // =====================================================================
        printFooter();
    }

    private static void printHeader() {
        System.out.println("╔══════════════════════════════════════════════════╗");
        System.out.println("║   TP Architecture Logicielle - Question 6        ║");
        System.out.println("║   Publisher-Subscriber via AOP (AspectJ)         ║");
        System.out.println("║   Simulation : Feu de Circulation                ║");
        System.out.println("╚══════════════════════════════════════════════════╝");
    }

    private static void printFooter() {
        System.out.println("\n╔══════════════════════════════════════════════════╗");
        System.out.println("║   SIMULATION TERMINÉE AVEC SUCCÈS                ║");
        System.out.println("║                                                  ║");
        System.out.println("║   Résultat : TrafficLight n'a JAMAIS référencé   ║");
        System.out.println("║   aucun Subscriber. L'Aspect a joué le rôle      ║");
        System.out.println("║   de médiateur transparent.                      ║");
        System.out.println("╚══════════════════════════════════════════════════╝");
    }
}
