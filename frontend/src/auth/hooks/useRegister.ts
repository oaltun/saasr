import { useMutation } from "@tanstack/react-query";
import { signUp } from "../utils/auth";

export function useRegister() {
  const { isLoading, mutateAsync } = useMutation(signUp);
  return { isRegistering: isLoading, register: mutateAsync };
}
