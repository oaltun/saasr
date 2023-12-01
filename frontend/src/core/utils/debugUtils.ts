import { DEBUG } from "../config/debug";
import { pseudoRandomIntFromInterval } from "./randomUtils";

export function debugSx(propsSx) {

    let sx = {}
    if (DEBUG) {
        // const rcolor = randomColor({
        //   luminosity: 'bright',
        //   format: 'rgb'
        // });
        const r1 = pseudoRandomIntFromInterval(150, 255);
        const r2 = pseudoRandomIntFromInterval(150, 255);
        const r3 = pseudoRandomIntFromInterval(150, 255);
        const rcolor = `rgb(${r1},${r2},${r3})`;
        console.log(rcolor)
        sx["bgcolor"] = rcolor;
    }
    const psx = propsSx ?? {}
    sx = { ...sx, ...psx };
    return sx
}