import LoadingButton from "@mui/lab/LoadingButton/LoadingButton";
import { Typography } from "@mui/material";
import TextField from "@mui/material/TextField";
import { PropsWithChildren, useState } from 'react'


type Props = {
  label: string;
  defaultValue: string;
  loading?: boolean;
  onButtonClick: (value: string) => any;
  fixValue?: (value: string) => string;
  valueError?: (value: string) => string;
  buttonContents?: string;
  end?: (value: string) => React.ReactNode;
}



export const InputSubmitter = (props: PropsWithChildren<Props>) => {

  const [inputValue, setInputValue] = useState(props.defaultValue);
  const [error, setError] = useState("");

  const onInputChange = (value: string) => {
    if (props.fixValue) setInputValue(props.fixValue(value));
    else setInputValue(value);
    if (inputValue === "") {
      setError("");
    } else if (props.valueError) {
      setError(props.valueError(inputValue));
    }
  }

  const onButtonSubmit = () => {
    if (props.valueError) {
      const error = props.valueError(inputValue);
      if (error) {
        setError(error);
        return;
      }
    }
    props.onButtonClick(inputValue);
  }

  return (
    <>
      <TextField
        label={props.label}

        disabled={props.loading}
        value={inputValue}
        onChange={(e) => onInputChange(e.target.value)}
        onBlur={(e) => onInputChange(e.target.value)}
        error={!!error}
      />
      {" "}
      <LoadingButton
        loading={props.loading}
        onClick={onButtonSubmit}
      >
        {/* span because of a bug in MUI*/}
        <span>
          {props.buttonContents ? props.buttonContents : "Submit"}
        </span>
      </LoadingButton>
      {<Typography color={"red"}>{error}</Typography>}
      {props.end &&
        props.end(inputValue)
      }



    </>
  )
};

export default InputSubmitter;
