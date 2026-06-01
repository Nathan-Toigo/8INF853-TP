package com.tp.q6;

/**
 * Subscriber représentant un piéton réagissant aux changements du feu.
 *
 * Implémente TrafficObserver pour définir le comportement spécifique
 * d'un piéton face à chaque couleur du feu de circulation.
 */
public class Pedestrian implements TrafficObserver {

    /** Nom du piéton. */
    private final String name;

    /**
     * @param name nom du piéton
     */
    public Pedestrian(String name) {
        this.name = name;
        System.out.println("[Pedestrian] Piéton '" + name + "' enregistré comme observateur.");
    }

    /**
     * Réaction du piéton au changement de couleur du feu.
     * Appelée automatiquement par l'Aspect, sans que TrafficLight le sache.
     *
     * @param oldColor ancienne couleur
     * @param newColor nouvelle couleur
     */
    @Override
    public void onColorChange(String oldColor, String newColor) {
        System.out.print("[Pedestrian '" + name + "'] Réaction : ");
        switch (newColor.toUpperCase()) {
            case "RED":
                System.out.println("🔴 Feu ROUGE → C'est mon tour ! Je traverse.");
                break;
            case "ORANGE":
            case "YELLOW":
                System.out.println("🟡 Feu ORANGE → Je termine ma traversée rapidement.");
                break;
            case "GREEN":
                System.out.println("🟢 Feu VERT → Je dois attendre sur le trottoir.");
                break;
            default:
                System.out.println("⚪ Couleur inconnue '" + newColor + "' → Je reste sur place.");
        }
    }

    public String getName() {
        return name;
    }
}
