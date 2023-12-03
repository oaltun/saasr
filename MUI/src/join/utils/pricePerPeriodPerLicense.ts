import { mergeKeys } from "../../core/utils/mapUtils";

export const pricePerPeriodPerLicense = (priceQry, planId, billingCycleId) => {
    return priceQry.data?.priceMap.get(mergeKeys(planId, billingCycleId));
}
