export const mergeKeys = (a: string, b: string) => {
    return a + "_____________" + b;
}


//----------------
interface HasId {
    id: string;
}
export function array2map<Type extends HasId>(a: Type[]) {
    const map = new Map<string, Type>();
    for (const el of a) {
        map.set(el.id, el);
    }
    return map;
}

