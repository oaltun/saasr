import { pseudoRandom } from "./prngUtils";

export function pseudoRandomIntFromInterval(min, max) { // min and max included 
    return Math.floor(pseudoRandom() * (max - min + 1) + min)
}


