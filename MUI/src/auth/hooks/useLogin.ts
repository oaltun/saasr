import { useMutation } from "@tanstack/react-query";
import { login } from "../utils/auth";



export function useLogin() {
  const {
    isLoading, mutateAsync } = useMutation(login, {
      retry: 4,
      retryDelay: attempt => Math.min(attempt > 1 ? 2 ** attempt * 1000 : 1000, 30 * 1000)
    });

  return { isLoggingIn: isLoading, login: mutateAsync };
}
