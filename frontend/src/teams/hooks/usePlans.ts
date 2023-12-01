import { useQuery } from "@tanstack/react-query";
import { array2map } from "../../core/utils/mapUtils";
import { Plan, subscriptionPlanList } from "../../saasrapi";

const fetchPlans = async (): Promise<{
  plans: Plan[];
  planMap: Map<string, Plan>;
}> => {
  const plans = await subscriptionPlanList();
  const planMap = array2map(plans.data);
  return { plans: plans.data, planMap: planMap };
};
export function usePlans() {
  return useQuery({
    queryKey: ["subscription plans"],
    queryFn: fetchPlans,
  });
}
