import { PropsWithChildren } from 'react'

type Props = {
  condition: boolean;
  true?: any;
  else?: any;
}

export const If = (props: PropsWithChildren<Props>) => {
  return (props.condition ? props.true : props.else);
};

export default If;
