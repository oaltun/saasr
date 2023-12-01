
import { useMutation } from "@tanstack/react-query";
import { forgotPasswordConfirm } from "../utils/auth";



export function useForgotPasswordConfirm() {
  const { isLoading, mutateAsync } = useMutation(forgotPasswordConfirm);
  return { isLoading, forgotPasswordConfirm: mutateAsync };
}
