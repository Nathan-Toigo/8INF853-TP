package com.tp.q6;

/**
 * Subscriber représentant une voiture réagissant aux changements du feu.
 *
 * Implémente TrafficObserver pour définir le comportement spécifique
 * d'une voiture face à chaque couleur du feu de circulation.
 */
public class Car implements TrafficObserver {

    /** Identifiant de la voiture. */
    private final String licensePlate;

    /**
     * @param licensePlate plaque d'immatriculation de la voiture
     */
    public Car(String licensePlate) {
        this.licensePlate = licensePlate;
        System.out.println("[Car] Voiture '" + licensePlate + "' enregistrée comme observateur.");
    }

    /**
     * Réaction de la voiture au changement de couleur du feu.
     * Appelée automatiquement par l'Aspect, sans que TrafficLight le sache.
     *
     * @param oldColor ancienne couleur
     * @param newColor nouvelle couleur
     */
    @Override
    public void onColorChange(String oldColor, String newColor) {
        System.out.print("[Car '" + licensePlate + "'] Réaction : ");
        switch (newColor.toUpperCase()) {
            case "RED":
                System.out.println("🔴 Feu ROUGE → STOP ! Je m'arrête.");
                break;
            case "ORANGE":
            case "YELLOW":
                System.out.println("🟡 Feu ORANGE → Attention, je ralentis.");
                break;
            case "GREEN":
                System.out.println("🟢 Feu VERT → Je peux avancer !");
                break;
            default:
                System.out.println("⚪ Couleur inconnue '" + newColor + "' → Je reste prudent.");
        }
    }

    public String getLicensePlate() {
        return licensePlate;
    }
}
