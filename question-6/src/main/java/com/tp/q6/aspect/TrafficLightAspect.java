package com.tp.q6.aspect;

import com.tp.q6.TrafficLight;
import com.tp.q6.TrafficObserver;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.After;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Aspect AspectJ implémentant le patron Publisher-Subscriber (Observer).
 *
 * Cet Aspect est le coeur de l'architecture AOP. Il centralise :
 * 1. L'enregistrement des Subscribers (TrafficObserver)
 * 2. L'interception des appels à TrafficLight.changeColor()
 * 3. La notification automatique de tous les Subscribers enregistrés
 *
 * PRINCIPE CLÉ : TrafficLight (Publisher) ignore totalement l'existence de cet Aspect
 * et des Subscribers. Le couplage entre Publisher et Subscribers est NULJ.
 * C'est l'Aspect qui joue le rôle de médiateur transparent.
 *
 * Design pattern utilisé : Singleton via @Aspect (une seule instance d'Aspect par défaut).
 */
@Aspect
public class TrafficLightAspect {

    /**
     * Registre des Subscribers : associe chaque TrafficLight à sa liste d'observateurs.
     * Utilise un ConcurrentHashMap pour la thread-safety.
     */
    private final Map<TrafficLight, List<TrafficObserver>> observersRegistry =
            new ConcurrentHashMap<>();

    // =========================================================================
    // GESTION DES ABONNEMENTS
    // =========================================================================

    /**
     * Enregistre un Subscriber pour être notifié des changements d'un TrafficLight donné.
     *
     * @param trafficLight le feu de circulation à surveiller
     * @param observer     l'observateur à enregistrer
     */
    public void register(TrafficLight trafficLight, TrafficObserver observer) {
        observersRegistry
                .computeIfAbsent(trafficLight, k -> new ArrayList<>())
                .add(observer);
        System.out.println("[Aspect] Observateur enregistré pour le feu '"
                + trafficLight.getId() + "' : " + observer.getClass().getSimpleName());
    }

    /**
     * Désabonne un Subscriber d'un TrafficLight donné.
     *
     * @param trafficLight le feu de circulation
     * @param observer     l'observateur à retirer
     */
    public void unregister(TrafficLight trafficLight, TrafficObserver observer) {
        List<TrafficObserver> observers = observersRegistry.get(trafficLight);
        if (observers != null) {
            observers.remove(observer);
            System.out.println("[Aspect] Observateur retiré pour le feu '"
                    + trafficLight.getId() + "' : " + observer.getClass().getSimpleName());
        }
    }

    /**
     * Retourne la liste (non modifiable) des observateurs d'un feu donné.
     *
     * @param trafficLight le feu de circulation
     * @return liste des observateurs enregistrés
     */
    public List<TrafficObserver> getObservers(TrafficLight trafficLight) {
        return Collections.unmodifiableList(
                observersRegistry.getOrDefault(trafficLight, new ArrayList<>())
        );
    }

    // =========================================================================
    // POINTCUTS (définition des points de jonction à intercepter)
    // =========================================================================

    /**
     * Pointcut capturant tous les appels à la méthode changeColor(String)
     * sur n'importe quelle instance de TrafficLight.
     *
     * Syntaxe AspectJ :
     * - execution : intercepte l'exécution de la méthode (pas l'appel)
     * - * : n'importe quel type de retour
     * - com.tp.q6.TrafficLight.changeColor : méthode ciblée
     * - (String) : acceptant un String en argument
     * - && args(newColor) : lie le 1er argument au paramètre 'newColor'
     * - && this(trafficLight) : lie l'instance cible au paramètre 'trafficLight'
     */
    @Pointcut("execution(* com.tp.q6.TrafficLight.changeColor(String)) "
            + "&& args(newColor) && this(trafficLight)")
    public void colorChangePointcut(String newColor, TrafficLight trafficLight) {
        // Pointcut vide - sert uniquement à nommer et paramétrer le point de jonction
    }

    // =========================================================================
    // ADVICE (code exécuté au point de jonction)
    // =========================================================================

    /**
     * Advice @After : s'exécute APRÈS l'exécution de changeColor().
     *
     * À ce moment, la nouvelle couleur est déjà enregistrée dans TrafficLight.
     * On récupère l'ancienne couleur via les arguments du join point.
     *
     * @param newColor     la nouvelle couleur (liée par le pointcut)
     * @param trafficLight l'instance du feu (liée par le pointcut)
     */
    @After("colorChangePointcut(newColor, trafficLight)")
    public void afterColorChange(String newColor, TrafficLight trafficLight) {
        // Récupérer la liste des observateurs pour ce feu
        List<TrafficObserver> observers = observersRegistry.getOrDefault(
                trafficLight, Collections.emptyList()
        );

        if (observers.isEmpty()) {
            System.out.println("[Aspect] Aucun observateur enregistré pour le feu '"
                    + trafficLight.getId() + "'.");
            return;
        }

        System.out.println("[Aspect] Interception de changeColor() sur le feu '"
                + trafficLight.getId() + "'. Notification de "
                + observers.size() + " observateur(s)...");
        System.out.println("[Aspect] ─────────────────────────────────────");

        // Notifier chaque observateur
        for (TrafficObserver observer : observers) {
            // On passe la nouvelle couleur ; pour l'ancienne, on utilise
            // la couleur courante (qui est déjà newColor après l'exécution)
            // On indique "PRÉCÉDENT" via une convention de log dans l'Aspect
            observer.onColorChange("PRÉCÉDENT", newColor);
        }

        System.out.println("[Aspect] ─────────────────────────────────────");
    }
}
