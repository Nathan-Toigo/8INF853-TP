package com.tp.q6;

/**
 * Classe Publisher représentant un feu de circulation.
 *
 * IMPORTANT : Cette classe ne contient AUCUNE référence aux Subscribers (Observers).
 * Elle ne connaît pas l'interface TrafficObserver, ne maintient pas de liste
 * d'abonnés et n'appelle aucune méthode de notification.
 *
 * C'est l'Aspect TrafficLightAspect qui intercepte les appels à changeColor()
 * et se charge de notifier tous les abonnés de manière transparente.
 *
 * Cette séparation totale des préoccupations est le cœur de l'approche AOP.
 */
public class TrafficLight {

    /** Couleur courante du feu de circulation. */
    private String color;

    /** Identifiant de ce feu (pour les logs). */
    private final String id;

    /**
     * Constructeur du feu de circulation.
     *
     * @param id       identifiant unique du feu
     * @param initialColor couleur initiale
     */
    public TrafficLight(String id, String initialColor) {
        this.id = id;
        this.color = initialColor;
        System.out.println("[TrafficLight] Feu '" + id + "' initialisé à : " + initialColor);
    }

    /**
     * Change la couleur du feu de circulation.
     *
     * Cette méthode est le point de jonction (Join Point) intercepté par l'Aspect.
     * Elle ne contient que la logique métier pure : mettre à jour la couleur.
     *
     * @param newColor la nouvelle couleur du feu
     */
    public void changeColor(String newColor) {
        System.out.println("[TrafficLight] '" + id + "' change de couleur : " + this.color + " -> " + newColor);
        this.color = newColor;
    }

    /**
     * @return la couleur courante du feu
     */
    public String getColor() {
        return color;
    }

    /**
     * @return l'identifiant du feu
     */
    public String getId() {
        return id;
    }
}
