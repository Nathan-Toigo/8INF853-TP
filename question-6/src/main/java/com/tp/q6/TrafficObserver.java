package com.tp.q6;

/**
 * Interface définissant le contrat des Subscribers (Observers).
 *
 * Toute classe souhaitant être notifiée des changements d'état du feu
 * de circulation doit implémenter cette interface.
 *
 * NOTE : Le Publisher (TrafficLight) n'a AUCUNE connaissance de cette interface.
 * C'est l'Aspect qui fait le lien entre Publisher et Subscribers.
 */
public interface TrafficObserver {

    /**
     * Méthode appelée par l'Aspect lorsque la couleur du feu change.
     *
     * @param oldColor l'ancienne couleur du feu
     * @param newColor la nouvelle couleur du feu
     */
    void onColorChange(String oldColor, String newColor);
}
