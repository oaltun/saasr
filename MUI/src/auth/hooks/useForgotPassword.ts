import { useMutation } from "@tanstack/react-query";
import { forgotPassword } from "../utils/auth.js";


export function useForgotPassword() {
  const { isLoading, mutateAsync } = useMutation(forgotPassword);
  return { isLoading, forgotPassword: mutateAsync };
}
