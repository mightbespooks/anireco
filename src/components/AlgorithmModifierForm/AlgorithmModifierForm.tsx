import { useState } from 'react'
import Slider from '@mui/material/Slider';
import NumberField from '../NumberField';
import { formToJSON } from '../../utils/formToJSON';

const formatValueLabel = (value: number) => { return `${100 - value}/${value}`}

function AlgorithmModifierForm() {
  const [values, setValues] = useState({
    "mean_popularity": {
      val: 70,
      weight: 20
    }
  })
  
  const handleSubmit = async (formData: FormData) => {};

  return (
    <div>
      <form action={handleSubmit}>
        <Slider 
          value={values['mean_popularity']['val']}
          defaultValue={70} 
          valueLabelDisplay="auto" 
          step={1} 
          getAriaValueText={formatValueLabel}
          valueLabelFormat={formatValueLabel}
          onChange={(e, newValue) => {
            setValues(prevValues => ({
              ...prevValues,
              mean_popularity: {
                ...prevValues.mean_popularity,
                val: newValue as number
              }
            }));
          }}
        />
        <NumberField label="Weight" min={10} max={40} />
        <button type="submit">Save Algorithm</button>
      </form>
    </div>
  )
}

export default AlgorithmModifierForm
