import { useQuery } from "@tanstack/react-query";
import { array2map } from "../../core/utils/mapUtils";
import { BillingCycle, subscriptionBillingCycleList } from "../../saasrapi";

const fetchBillingCycles = async (): Promise<{
  billingCycles: BillingCycle[];
  billingCycleMap: Map<string, BillingCycle>;
}> => {
  const cycles = await subscriptionBillingCycleList();
  const activeCycles = cycles.data.filter(
    (cycle: BillingCycle) => cycle.is_active === true
  );
  const cycleMap = array2map(activeCycles);

  return { billingCycles: activeCycles, billingCycleMap: cycleMap };
};
export function useBillingCycles() {
  return useQuery({
    queryKey: ["subscription billing cycles"],
    queryFn: fetchBillingCycles,
  });
}
