import { useMutation } from "@tanstack/react-query";
import { logout } from "../utils/auth";



export function useLogout() {
  const { isLoading, mutateAsync } = useMutation(logout);

  return { isLoggingOut: isLoading, logout: mutateAsync };
}
